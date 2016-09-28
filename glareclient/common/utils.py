# Copyright 2012 OpenStack Foundation
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

from __future__ import print_function

import errno
import hashlib
import os
import six
import sys

if os.name == 'nt':
    import msvcrt
else:
    msvcrt = None

from oslo_utils import encodeutils
from oslo_utils import importutils

SENSITIVE_HEADERS = ('X-Auth-Token', )


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars.

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def import_versioned_module(version, submodule=None):
    module = 'glareclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def exit(msg='', exit_code=1):
    if msg:
        print(encodeutils.safe_decode(msg), file=sys.stderr)
    sys.exit(exit_code)


def integrity_iter(iter, checksum):
    """Check blob integrity.

    :raises: IOError
    """
    md5sum = hashlib.md5()
    for chunk in iter:
        yield chunk
        if isinstance(chunk, six.string_types):
            chunk = six.b(chunk)
        md5sum.update(chunk)
    md5sum = md5sum.hexdigest()
    if md5sum != checksum:
        raise IOError(errno.EPIPE,
                      'Corrupt blob download. Checksum was %s expected %s' %
                      (md5sum, checksum))


class IterableWithLength(object):
    def __init__(self, iterable, length):
        self.iterable = iterable
        self.length = length

    def __iter__(self):
        try:
            for chunk in self.iterable:
                yield chunk
        finally:
            self.iterable.close()

    def next(self):
        return next(self.iterable)

    def __len__(self):
        return self.length


def get_item_properties(item, fields, mixed_case_fields=None, formatters=None):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Project, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name]
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def make_size_human_readable(size):
    suffix = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
    base = 1024.0
    index = 0

    if size is None:
        size = 0
    while size >= base:
        index = index + 1
        size = size / base

    padded = '%.1f' % size
    stripped = padded.rstrip('0').rstrip('.')

    return '%s%s' % (stripped, suffix[index])


def save_blob(data, path):
    """Save a blob to the specified path.

    :param data: blob of the artifact
    :param path: path to save the blob to
    """
    if path is None:
        blob = getattr(sys.stdout, 'buffer',
                       sys.stdout)
    else:
        blob = open(path, 'wb')
    try:
        for chunk in data:
            blob.write(chunk)
    finally:
        if path is not None:
            blob.close()


def get_data_file(blob):
    if blob:
        return open(blob, 'rb')
    else:
        # distinguish cases where:
        # (1) stdin is not valid (as in cron jobs):
        #     glare ... <&-
        # (2) blob is provided through standard input:
        #     glare ... < /tmp/file or cat /tmp/file | glare ...
        # (3) no blob provided:
        #     glare ...
        try:
            os.fstat(0)
        except OSError:
            # (1) stdin is not valid (closed...)
            return None
        if not sys.stdin.isatty():
            # (2) blob data is provided through standard input
            blob_data = sys.stdin
            if hasattr(sys.stdin, 'buffer'):
                blob_data = sys.stdin.buffer
            if msvcrt:
                msvcrt.setmode(blob_data.fileno(), os.O_BINARY)
            return blob_data
        else:
            # (3) no blob data provided
            return None


def get_file_size(file_obj):
    """Analyze file-like object and attempt to determine its size.

    :param file_obj: file-like object.
    :retval The file's size or None if it cannot be determined.
    """
    if (hasattr(file_obj, 'seek') and hasattr(file_obj, 'tell') and
            (six.PY2 or six.PY3 and file_obj.seekable())):
        try:
            curr = file_obj.tell()
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()
            file_obj.seek(curr)
            return size
        except IOError as e:
            if e.errno == errno.ESPIPE:
                # Illegal seek. This means the file object
                # is a pipe (e.g. the user is trying
                # to pipe blob to the client,
                # echo testdata | bin/glare add blah...), or
                # that file object is empty, or that a file-like
                # object which doesn't support 'seek/tell' has
                # been supplied.
                return
            else:
                raise
