# Copyright 2016 OpenStack Foundation
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

import sys

import mock
from osc_lib.tests import utils

from glareclient.common import utils as g_utils
from glareclient.tests.unit.osc.v1 import fakes_schemas

blob_fixture = {
    "status": "active",
    "url": "fake_url",
    "md5": "35d83e8eedfbdb87ff97d1f2761f8ebf",
    "sha1": "942854360eeec1335537702399c5aed940401602",
    "sha256": "d8a7834fc6652f316322d80196f6dcf2"
              "94417030e37c15412e4deb7a67a367dd",
    "external": False,
    "content_type": "application/octet-stream",
    "size": 594}


def mock_list(*args, **kwargs):
    return [{'id': 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
             'name': 'art1',
             'version': '0.0.0',
             'owner': 'f649c77999e449e89627024f71b76603',
             'visibility': 'private',
             'status': 'active',
             'type_name': 'images'},
            {'id': '48d35c1d-6739-459b-bbda-e4dcba8a684a',
             'name': 'art2',
             'version': '0.0.0',
             'owner': 'f649c77999e449e89627024f71b76603',
             'visibility': 'private',
             'status': 'active',
             'type_name': 'heat_templates'}]


def mock_get(*args, **kwargs):
    return {'id': 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
            'name': 'art1',
            'version': '0.0.0',
            'owner': 'f649c77999e449e89627024f71b76603',
            'visibility': 'private',
            'status': 'active',
            'blob': blob_fixture,
            'image': blob_fixture,
            'package': blob_fixture,
            'template': blob_fixture,
            'environment': blob_fixture}


def mock_g_servs(*args, **kwargs):
    return {'id': 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
            'name': 'art1',
            'version': '0.0.0',
            'owner': 'f649c77999e449e89627024f71b76603',
            'visibility': 'private',
            'status': 'active'}


def mock_g_schema(*args, **kwargs):
    return fakes_schemas.FIXTURE_SCHEMA


def mock_get_data_file(*args, **kwargs):
    return 'data'


class TestArtifacts(utils.TestCommand):

    def setUp(self):
        super(TestArtifacts, self).setUp()
        self.app.client_manager.artifact = mock.MagicMock()
        self.app.client_manager.artifact.artifacts.list = mock_list
        self.app.client_manager.artifact.artifacts.get = mock_get
        self.app.client_manager.artifact.artifacts.get_by_name = mock_get
        self.app.client_manager.artifact.artifacts.add_tag = mock_g_servs
        self.app.client_manager.artifact.artifacts.remove_tag = mock_g_servs
        self.app.client_manager.artifact.artifacts.create = mock_g_servs
        self.app.client_manager.artifact.artifacts.update = mock_g_servs
        self.app.client_manager.artifact.artifacts.delete = mock_g_servs
        self.app.client_manager.artifact.artifacts.activate = mock_g_servs
        self.app.client_manager.artifact.artifacts.deactivate = mock_g_servs
        self.app.client_manager.artifact.artifacts.reactivate = mock_g_servs
        self.app.client_manager.artifact.artifacts.publish = mock_g_servs
        self.app.client_manager.artifact.blobs.upload_blob = mock_g_servs
        self.app.client_manager.artifact.blobs.download_blob = mock_g_servs
        self.app.client_manager.artifact.blobs.add_external_location = \
            mock_g_servs
        self.app.client_manager.artifact.artifacts.get_type_schema = \
            mock_g_schema
        g_utils.get_data_file = mock.MagicMock()
        g_utils.get_data_file = mock_get_data_file
        g_utils.save_blob = mock.MagicMock()
        sys.stdout.isatty = mock.MagicMock()
        sys.stdout.isatty._mock_return_value = True
