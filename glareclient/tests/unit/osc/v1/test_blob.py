# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock

from glareclient import exc
from glareclient.osc.v1 import blobs as osc_blob
from glareclient.tests.unit.osc.v1 import fakes
from glareclient.v1 import artifacts as api_art
import testtools


class TestUpload(testtools.TestCase):

    def setUp(self):
        self.mock_app = mock.Mock()
        self.mock_args = mock.Mock()
        self.mock_manager = mock.Mock()
        self.mock_manager.artifacts.get.return_value = {'image': {}}
        super(TestUpload, self).setUp()

    @mock.patch('glareclient.osc.v1.blobs.progressbar')
    @mock.patch('glareclient.osc.v1.blobs.sys')
    @mock.patch('glareclient.osc.v1.blobs.open', create=True)
    @mock.patch('glareclient.common.utils.get_artifact_id')
    def test_upload_file_progress(self, mock_get_id,
                                  mock_open, mock_sys, mock_progressbar):
        mock_parsed_args = mock.Mock(name='test-id',
                                     id=True,
                                     blob_property='image',
                                     file='/path/file',
                                     progress=True,
                                     content_type='application/test',
                                     type_name='test-type')
        mock_get_id.return_value = 'test-id'
        cli = osc_blob.UploadBlob(self.mock_app, self.mock_args)
        cli.app.client_manager.artifact = self.mock_manager
        cli.dict2columns = mock.Mock(return_value=42)
        self.assertEqual(42, cli.take_action(mock_parsed_args))
        cli.dict2columns.assert_called_once_with({'blob_property': 'image'})
        upload_args = ['test-id', 'image',
                       mock_progressbar.VerboseFileWrapper.return_value]
        upload_kwargs = {'content_type': 'application/test',
                         'type_name': 'test-type'}
        self.mock_manager.artifacts.upload_blob.\
            assert_called_once_with(*upload_args, **upload_kwargs)

    @mock.patch('glareclient.osc.v1.blobs.sys')
    @mock.patch('glareclient.osc.v1.blobs.open', create=True)
    @mock.patch('glareclient.common.utils.get_artifact_id')
    def test_upload_file_no_progress(self, mock_get_id, mock_open, mock_sys):
        mock_parsed_args = mock.Mock(name='test-id',
                                     id=True,
                                     blob_property='image',
                                     progress=False,
                                     file='/path/file',
                                     content_type='application/test',
                                     type_name='test-type')
        mock_get_id.return_value = 'test-id'
        cli = osc_blob.UploadBlob(self.mock_app, self.mock_args)
        cli.app.client_manager.artifact = self.mock_manager
        cli.dict2columns = mock.Mock(return_value=42)
        self.assertEqual(42, cli.take_action(mock_parsed_args))
        cli.dict2columns.assert_called_once_with({'blob_property': 'image'})
        upload_args = ['test-id', 'image', mock_open.return_value]
        upload_kwargs = {'content_type': 'application/test',
                         'type_name': 'test-type'}
        self.mock_manager.artifacts.upload_blob.\
            assert_called_once_with(*upload_args, **upload_kwargs)

    @mock.patch('glareclient.osc.v1.blobs.sys')
    @mock.patch('glareclient.common.utils.get_artifact_id')
    def test_upload_file_stdin(self, mock_get_id, mock_sys):
        mock_sys.stdin.isatty.return_value = False
        mock_parsed_args = mock.Mock(name='test-id',
                                     id=True,
                                     blob_property='image',
                                     progress=False,
                                     file=None,
                                     content_type='application/test',
                                     type_name='test-type')
        mock_get_id.return_value = 'test-id'
        cli = osc_blob.UploadBlob(self.mock_app, self.mock_args)
        cli.app.client_manager.artifact = self.mock_manager
        cli.dict2columns = mock.Mock(return_value=42)
        self.assertEqual(42, cli.take_action(mock_parsed_args))
        cli.dict2columns.assert_called_once_with({'blob_property': 'image'})
        upload_args = ['test-id', 'image', mock_sys.stdin]
        upload_kwargs = {'content_type': 'application/test',
                         'type_name': 'test-type'}
        self.mock_manager.artifacts.upload_blob.\
            assert_called_once_with(*upload_args, **upload_kwargs)

    @mock.patch('glareclient.osc.v1.blobs.sys')
    def test_upload_file_stdin_isatty(self, mock_sys):
        mock_sys.stdin.isatty.return_value = True
        mock_parsed_args = mock.Mock(id='test-id',
                                     blob_property='image',
                                     progress=False,
                                     file=None,
                                     content_type='application/test',
                                     type_name='test-type')
        cli = osc_blob.UploadBlob(self.mock_app, self.mock_args)
        cli.app.client_manager.artifact = self.mock_manager
        self.assertRaises(exc.CommandError, cli.take_action, mock_parsed_args)


class TestBlobs(fakes.TestArtifacts):
    def setUp(self):
        super(TestBlobs, self).setUp()
        self.blob_mock = \
            self.app.client_manager.artifact.blobs
        self.http = mock.MagicMock()


class TestDownloadBlob(TestBlobs):
    def setUp(self):
        super(TestDownloadBlob, self).setUp()
        self.blob_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_blob.DownloadBlob(self.app, None)

        self.COLUMNS = ('blob_property', 'id', 'name',
                        'size', 'status', 'version')

    def test_download_exception(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--blob-property', 'blob',
                   '--file', None]
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with testtools.ExpectedException(SystemExit):
            self.cmd.take_action(parsed_args)

    def test_download_blob(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--blob-property', 'blob',
                   '--file', '/path/to/file']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        self.cmd.take_action(parsed_args)

    def test_download_without_blob_property(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        self.cmd.take_action(parsed_args)

    def test_download_progress(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file',
                   '--progress']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        self.cmd.take_action(parsed_args)


class TestAddLocation(TestBlobs):
    def setUp(self):
        super(TestAddLocation, self).setUp()
        self.blob_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_blob.AddLocation(self.app, None)
        self.COLUMNS = ('blob_property', 'content_type', 'external',
                        'md5', 'sha1', 'sha256', 'size', 'status', 'url')

    def test_add_location(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id',
                   '--url', 'fake_url',
                   '--md5', "35d83e8eedfbdb87ff97d1f2761f8ebf",
                   '--sha1', "942854360eeec1335537702399c5aed940401602",
                   '--sha256', "d8a7834fc6652f316322d80196f6dcf2"
                               "94417030e37c15412e4deb7a67a367dd"]
        verify = [('type_name', 'images'), ('url', 'fake_url')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)

    def test_add_dict_location(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id',
                   '--blob-property', 'nested_templates/blob',
                   '--url', 'fake_url',
                   '--md5', "35d83e8eedfbdb87ff97d1f2761f8ebf",
                   '--sha1', "942854360eeec1335537702399c5aed940401602",
                   '--sha256', "d8a7834fc6652f316322d80196f6dcf2"
                               "94417030e37c15412e4deb7a67a367dd"]
        verify = [('type_name', 'images'), ('url', 'fake_url')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        self.app.client_manager.artifact.artifacts.get = \
            lambda *args, **kwargs: {
                'nested_templates': {'blob': fakes.blob_fixture}
            }
        columns, data = self.cmd.take_action(parsed_args)
        self.app.client_manager.artifact.artifacts.get = fakes.mock_get
        self.assertEqual(self.COLUMNS, columns)
