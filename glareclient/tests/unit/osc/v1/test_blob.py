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

from glareclient.osc.v1 import blobs as osc_blob
from glareclient.tests.unit.osc.v1 import fakes
from glareclient.v1 import artifacts as api_art
import testtools


class TestBlobs(fakes.TestArtifacts):
    def setUp(self):
        super(TestBlobs, self).setUp()
        self.blob_mock = \
            self.app.client_manager.artifact.blobs
        self.http = mock.MagicMock()


class TestUploadBlob(TestBlobs):
    def setUp(self):
        super(TestUploadBlob, self).setUp()
        self.blob_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_blob.UploadBlob(self.app, None)

        self.COLUMNS = ('blob_property', 'content_type', 'external',
                        'md5', 'sha1', 'sha256', 'size', 'status', 'url')

    def test_upload_images(self):
        exp_data = ('image', 'application/octet-stream', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)

    def test_upload_tosca_template(self):
        exp_data = ('template', 'application/octet-stream', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')
        arglist = ['tosca_templates',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'tosca_templates')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)

    def test_upload_heat_template(self):
        exp_data = ('template', 'application/octet-stream', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')
        arglist = ['heat_templates',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'heat_templates')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)

    def test_upload_environment(self):
        exp_data = ('environment', 'application/octet-stream', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')
        arglist = ['heat_environments',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'heat_environments')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)

    def test_upload_package(self):
        exp_data = ('package', 'application/octet-stream', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')
        arglist = ['murano_packages',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'murano_packages')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)

    def test_upload_bad(self):
        arglist = ['user_type',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file']
        verify = [('type_name', 'user_type')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with testtools.ExpectedException(SystemExit):
            self.cmd.take_action(parsed_args)

    def test_upload_with_custom_content_type(self):
        exp_data = ('template', 'application/x-yaml', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')

        mocked_get = {
            "status": "active",
            "url": "fake_url",
            "md5": "35d83e8eedfbdb87ff97d1f2761f8ebf",
            "sha1": "942854360eeec1335537702399c5aed940401602",
            "sha256": "d8a7834fc6652f316322d80196f6dcf2"
                      "94417030e37c15412e4deb7a67a367dd",
            "external": False,
            "content_type": "application/x-yaml",
            "size": 594}
        self.app.client_manager.artifact.artifacts.get = \
            lambda id, type_name: {'template': mocked_get}

        arglist = ['tosca_templates',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file',
                   '--content-type', 'application/x-yaml']
        verify = [('type_name', 'tosca_templates')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)

    def test_upload_blob_with_blob_prop(self):
        exp_data = ('blob', 'application/octet-stream', False,
                    '35d83e8eedfbdb87ff97d1f2761f8ebf',
                    '942854360eeec1335537702399c5aed940401602',
                    'd8a7834fc6652f316322d80196f6dcf2'
                    '94417030e37c15412e4deb7a67a367dd',
                    594, 'active', 'fake_url')
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--file', '/path/to/file',
                   '--blob-property', 'blob']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        self.assertEqual(self.COLUMNS, columns)
        self.assertEqual(exp_data, data)


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
                   '--progress', 'True']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        self.cmd.take_action(parsed_args)
