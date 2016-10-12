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

import mock
from six import StringIO
import testtools

from glareclient.common import progressbar

MOD = 'glareclient.common.progressbar'


class TestProgressBar(testtools.TestCase):

    @mock.patch(MOD + '.os')
    def test_totalsize_fileno(self, mock_os):
        mock_os.fstat.return_value.st_size = 43
        fake_file = mock.Mock()
        del fake_file.len
        fake_file.fileno.return_value = 42
        pb = progressbar.VerboseFileWrapper(fake_file)
        self.assertEqual(43, pb._totalsize)
        mock_os.fstat.assert_called_once_with(42)

    @mock.patch(MOD + '.sys')
    def test__display_progress_bar(self, mock_sys):
        fake_file = StringIO('test')  # 4 bytes
        fake_file.len = 4
        pb = progressbar.VerboseFileWrapper(fake_file)
        pb._display_progress_bar(2)  # 2 of 4 bytes = 50%
        pb._display_progress_bar(1)  # 3 of 4 bytes = 75%
        pb._display_progress_bar(1)  # 4 of 4 bytes = 100%
        expected = [
            mock.call('\r[===============>              ] 50%'),
            mock.call('\r[======================>       ] 75%'),
            mock.call('\r[=============================>] 100%'),
        ]
        self.assertEqual(expected, mock_sys.stdout.write.mock_calls)

    @mock.patch(MOD + '.sys')
    def test__display_progress_bar_unknown_len(self, mock_sys):
        fake_file = StringIO('')
        fake_file.len = 0
        pb = progressbar.VerboseFileWrapper(fake_file)
        for i in range(6):
            pb._display_progress_bar(1)
        expected = [
            mock.call('\r[-] 1 bytes'),
            mock.call('\r[\\] 2 bytes'),
            mock.call('\r[|] 3 bytes'),
            mock.call('\r[/] 4 bytes'),
            mock.call('\r[-] 5 bytes'),
            mock.call('\r[\\] 6 bytes'),
        ]
        self.assertEqual(expected, mock_sys.stdout.write.mock_calls)

    @mock.patch(MOD + '._ProgressBarBase.__init__')
    @mock.patch(MOD + '._ProgressBarBase._display_progress_bar')
    def test_read(self, mock_display_progress_bar, mock_init):
        mock_init.return_value = None
        pb = progressbar.VerboseFileWrapper()
        pb._wrapped = mock.Mock(len=42)
        pb._wrapped.read.return_value = 'ok'
        pb.read(2)
        mock_display_progress_bar.assert_called_once_with(2)
