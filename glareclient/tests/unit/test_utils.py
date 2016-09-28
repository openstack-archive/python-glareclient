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


import mock
import six
import testtools

from glareclient.common import utils


class TestUtils(testtools.TestCase):

    def test_make_size_human_readable(self):
        self.assertEqual("106B", utils.make_size_human_readable(106))
        self.assertEqual("1000kB", utils.make_size_human_readable(1024000))
        self.assertEqual("1MB", utils.make_size_human_readable(1048576))
        self.assertEqual("1.4GB", utils.make_size_human_readable(1476395008))
        self.assertEqual("9.3MB", utils.make_size_human_readable(9761280))
        self.assertEqual("0B", utils.make_size_human_readable(None))

    def test_get_new_file_size(self):
        size = 98304
        file_obj = six.StringIO('X' * size)
        try:
            self.assertEqual(size, utils.get_file_size(file_obj))
            # Check that get_file_size didn't change original file position.
            self.assertEqual(0, file_obj.tell())
        finally:
            file_obj.close()

    def test_get_consumed_file_size(self):
        size, consumed = 98304, 304
        file_obj = six.StringIO('X' * size)
        file_obj.seek(consumed)
        try:
            self.assertEqual(size, utils.get_file_size(file_obj))
            # Check that get_file_size didn't change original file position.
            self.assertEqual(consumed, file_obj.tell())
        finally:
            file_obj.close()

    def test_iterable_closes(self):
        # Regression test for bug 1461678.
        def _iterate(i):
            for chunk in i:
                raise(IOError)

        data = six.moves.StringIO('somestring')
        data.close = mock.Mock()
        i = utils.IterableWithLength(data, 10)
        self.assertRaises(IOError, _iterate, i)
        data.close.assert_called_with()
