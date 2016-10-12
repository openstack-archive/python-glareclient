# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import decimal
import os
import sys

SPIN_CHARS = ('-', '\\', '|', '/')
CHUNKSIZE = 1024 * 64  # 64kB


class _ProgressBarBase(object):
    """A progress bar provider for a wrapped object.

    Base abstract class used by specific class wrapper to show
    a progress bar when the wrapped object are consumed.

    :param wrapped: Object to wrap that hold data to be consumed.
    :param totalsize: The total size of the data in the wrapped object.

    :note: The progress will be displayed only if sys.stdout is a tty.
    """

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._show_progress = sys.stdout.isatty()
        self._percent = 0
        self._totalread = 0
        self._spin_index = 0
        if hasattr(wrapped, "len"):
            self._totalsize = wrapped.len
        elif hasattr(wrapped, "fileno"):
            self._totalsize = os.fstat(wrapped.fileno()).st_size
        else:
            self._totalsize = 0

    def _display_progress_bar(self, size_read):
        self._totalread += size_read
        if self._show_progress:
            if self._totalsize:
                percent = float(self._totalread) / float(self._totalsize)
                # Output something like this: [==========>             ] 49%
                sys.stdout.write('\r[{0:<30}] {1:.0%}'.format(
                    '=' * int(decimal.Decimal(percent * 29).quantize(
                        decimal.Decimal('1'),
                        rounding=decimal.ROUND_HALF_UP)) + '>', percent
                ))
            else:
                sys.stdout.write(
                    '\r[%s] %d bytes' % (SPIN_CHARS[self._spin_index],
                                         self._totalread))
                self._spin_index += 1
                if self._spin_index == len(SPIN_CHARS):
                    self._spin_index = 0
            sys.stdout.flush()

    def __getattr__(self, attr):
        # Forward other attribute access to the wrapped object.
        return getattr(self._wrapped, attr)


class VerboseFileWrapper(_ProgressBarBase):
    """A file wrapper with a progress bar.

    The file wrapper shows and advances a progress bar whenever the
    wrapped file's read method is called.
    """

    def read(self, *args, **kwargs):
        data = self._wrapped.read(*args, **kwargs)
        if data:
            self._display_progress_bar(len(data))
        else:
            if self._show_progress:
                # Break to a new line from the progress bar for incoming
                # output.
                sys.stdout.write('\n')
        return data

    def __iter__(self):
        return self

    def next(self):
        try:
            data = self._wrapped.next()
            self._display_progress_bar(len(data))
            return data
        except StopIteration:
            if self._show_progress:
                # Break to a new line from the progress bar for incoming
                # output.
                sys.stdout.write('\n')
            raise

    # In Python 3, __next__() has replaced next().
    __next__ = next
