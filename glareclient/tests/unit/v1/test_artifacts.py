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

import testtools

from glareclient.exc import HTTPBadRequest
from glareclient.tests.unit.v1 import fixtures
from glareclient.tests import utils
from glareclient.v1 import artifacts


class TestController(testtools.TestCase):
    def setUp(self):
        super(TestController, self).setUp()
        self.api = utils.FakeAPI(fixtures.data_fixtures)
        self.controller = artifacts.Controller(self.api)

    def test_list_artifacts(self):
        artifacts = list(self.controller.list(type_name='images'))
        self.assertEqual('3a4560a1-e585-443e-9b39-553b46ec92d1',
                         artifacts[0]['id'])
        self.assertEqual('art1', artifacts[0]['name'])
        self.assertEqual('db721fb0-5b85-4738-9401-f161d541de5e',
                         artifacts[1]['id'])
        self.assertEqual('art2', artifacts[1]['name'])
        self.assertEqual('e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                         artifacts[2]['id'])
        self.assertEqual('art3', artifacts[2]['name'])

        exp_headers = {}
        expect_body = None
        expect = [('GET', '/artifacts/images?limit=20',
                   exp_headers,
                   expect_body)]
        self.assertEqual(expect, self.api.calls)

    def test_list_with_paginate(self):
        artifacts = list(self.controller.list(type_name='images',
                                              page_size=2))
        self.assertEqual('3a4560a1-e585-443e-9b39-553b46ec92d1',
                         artifacts[0]['id'])
        self.assertEqual('art1', artifacts[0]['name'])
        self.assertEqual('art2', artifacts[1]['name'])
        self.assertEqual('db721fb0-5b85-4738-9401-f161d541de5e',
                         artifacts[1]['id'])
        exp_headers = {}
        expect_body = None
        expect = [('GET', '/artifacts/images?limit=2',
                   exp_headers,
                   expect_body),
                  ('GET', '/artifacts/images?limit=2'
                          '&marker=e1090471-1d12-4935-a8d8-a9351266ece8',
                   exp_headers,
                   expect_body)]
        self.assertEqual(expect, self.api.calls)

    def test_list_artifacts_limit(self):
        artifacts = list(self.controller.list(type_name='images',
                                              limit=2))
        self.assertEqual('3a4560a1-e585-443e-9b39-553b46ec92d1',
                         artifacts[0]['id'])
        self.assertEqual('art1', artifacts[0]['name'])
        self.assertEqual('art2', artifacts[1]['name'])
        self.assertEqual('db721fb0-5b85-4738-9401-f161d541de5e',
                         artifacts[1]['id'])
        exp_headers = {}
        expect_body = None
        expect = [('GET', '/artifacts/images?limit=2',
                   exp_headers,
                   expect_body)]
        self.assertEqual(expect, self.api.calls)

    def test_list_artifact_sort_name(self):

        artifacts = list(self.controller.list(type_name='images',
                                              sort='name:desc'))
        self.assertEqual('e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                         artifacts[0]['id'])
        self.assertEqual('art2', artifacts[0]['name'])
        self.assertEqual('art1', artifacts[1]['name'])
        self.assertEqual('3a4560a1-e585-443e-9b39-553b46ec92d1',
                         artifacts[1]['id'])
        exp_headers = {}
        expect_body = None
        expect = [('GET', '/artifacts/images?limit=20'
                          '&sort=name%3Adesc',
                   exp_headers,
                   expect_body),
                  ('GET', '/artifacts/images?limit=20'
                          '&marker=3a4560a1-e585-443e-9b39-553b46ec92d1',
                   exp_headers,
                   expect_body)]
        self.assertEqual(expect, self.api.calls)

    def test_list_artifact_sort_badrequest(self):
        with testtools.ExpectedException(HTTPBadRequest):
            list(self.controller.list(type_name='images',
                                      sort='name:KAK'))

    def test_create_artifact(self):
        properties = {
            'name': 'art_1',
            'type_name': 'images'
        }

        art = self.controller.create(**properties)
        self.assertEqual('art_1', art['images'][0]['name'])
        self.assertEqual('0.0.0', art['images'][0]['version'])
        self.assertIsNotNone(art['images'][0]['id'])
        exp_headers = {}
        expect_body = [('name', 'art_1'), ('version', '0.0.0')]
        expect = [('POST', '/artifacts/images',
                   exp_headers,
                   expect_body)]
        self.assertEqual(expect, self.api.calls)

    def test_create_artifact_bad_prop(self):
        properties = {
            'name': 'art_1',
            'type_name': 'bad_type_name',
        }
        with testtools.ExpectedException(KeyError):
            self.controller.create(**properties)

    def test_delete_artifact(self):
        self.controller.delete(
            artifact_id='3a4560a1-e585-443e-9b39-553b46ec92a3',
            type_name='images')

        expect = [('DELETE', '/artifacts/images/'
                             '3a4560a1-e585-443e-9b39-553b46ec92a3',
                   {},
                   None)]
        self.assertEqual(expect, self.api.calls)

    def test_update_prop(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        param = {'type_name': 'images',
                 'name': 'new_name'}

        self.controller.update(artifact_id=art_id,
                               **param)

        exp_headers = {
            'Content-Type': 'application/json-patch+json'
        }

        expect_body = [{'path': '/name',
                        'value': 'new_name',
                        'op': 'add'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)

    def test_remove_prop(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'

        self.controller.update(artifact_id=art_id,
                               remove_props=['name'],
                               type_name='images')
        exp_headers = {
            'Content-Type': 'application/json-patch+json'
        }

        expect_body = [{'path': '/name',
                        'op': 'replace',
                        'value': None}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)
        self.api.calls = []

        self.controller.update(artifact_id=art_id,
                               remove_props=['metadata/key1'],
                               type_name='images')

        expect_body = [{'path': '/metadata/key1',
                        'op': 'remove'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)
        self.api.calls = []

        self.controller.update(artifact_id=art_id,
                               remove_props=['releases/1'],
                               type_name='images')

        expect_body = [{'path': '/releases/1',
                        'op': 'remove'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)

    def test_nontype_type_name(self):
        with testtools.ExpectedException(HTTPBadRequest):
            self.controller.create(name='art')

    def test_active_artifact(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.activate(artifact_id=art_id,
                                 type_name='images')
        exp_headers = {
            'Content-Type': 'application/json-patch+json'
        }

        expect_body = [{'path': '/status',
                        'value': 'active',
                        'op': 'add'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)

    def test_deactivate_artifact(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.deactivate(artifact_id=art_id,
                                   type_name='images')
        exp_headers = {
            'Content-Type': 'application/json-patch+json'
        }

        expect_body = [{'path': '/status',
                        'value': 'deactivated',
                        'op': 'add'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)

    def test_reactivate_artifact(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.reactivate(artifact_id=art_id,
                                   type_name='images')
        exp_headers = {
            'Content-Type': 'application/json-patch+json'
        }

        expect_body = [{'path': '/status',
                        'value': 'active',
                        'op': 'add'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]

        self.assertEqual(expect, self.api.calls)

    def test_publish_artifact(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.publish(artifact_id=art_id,
                                type_name='images')
        exp_headers = {
            'Content-Type': 'application/json-patch+json'
        }

        expect_body = [{'path': '/visibility',
                        'value': 'public',
                        'op': 'add'}]

        expect = [('PATCH', '/artifacts/images/%s' % art_id,
                   exp_headers,
                   expect_body)]
        self.assertEqual(expect, self.api.calls)

    def test_upload_blob(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.upload_blob(artifact_id=art_id,
                                    type_name='images',
                                    blob_property='image',
                                    data='data')

        exp_headers = {
            'Content-Type': 'application/octet-stream'
        }

        expect = [('PUT', '/artifacts/images/%s/image' % art_id,
                   exp_headers,
                   'data')]
        self.assertEqual(expect, self.api.calls)

    def test_upload_blob_custom_content_type(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.upload_blob(artifact_id=art_id,
                                    type_name='images',
                                    blob_property='image',
                                    data='{"a":"b"}',
                                    content_type='application/json',)

        exp_headers = {
            'Content-Type': 'application/json'
        }

        expect = [('PUT', '/artifacts/images/%s/image' % art_id,
                   exp_headers,
                   {"a": "b"})]
        self.assertEqual(expect, self.api.calls)

    def test_download_blob(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        self.controller.download_blob(artifact_id=art_id,
                                      type_name='images',
                                      blob_property='image')

        exp_headers = {}

        expect = [('GET', '/artifacts/images/%s/image' % art_id,
                   exp_headers,
                   None)]
        self.assertEqual(expect, self.api.calls)

    def test_download_blob_with_checksum(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a2'
        data = self.controller.download_blob(artifact_id=art_id,
                                             type_name='images',
                                             blob_property='image')
        self.assertIsNotNone(data.iterable)

        expect = [('GET', '/artifacts/images/%s/image' % art_id,
                   {},
                   None)]
        self.assertEqual(expect, self.api.calls)

    def test_download_blob_without_checksum(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a2'
        data = self.controller.download_blob(artifact_id=art_id,
                                             type_name='images',
                                             blob_property='image',
                                             do_checksum=False)
        self.assertIsNotNone(data.iterable)

        expect = [('GET', '/artifacts/images/%s/image' % art_id,
                   {},
                   None)]
        self.assertEqual(expect, self.api.calls)

    def test_get_artifact(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a3'
        art = self.controller.get(artifact_id=art_id,
                                  type_name='images')
        self.assertEqual(art_id, art['images'][0]['id'])
        self.assertEqual('art_1', art['images'][0]['name'])

    def test_type_list(self):
        data = self.controller.get_type_list()
        expect_data = [('images', '1.0'), ('heat_environments', '1.0')]
        expect_call = [('GET', '/schemas', {}, None)]
        self.assertEqual(expect_call, self.api.calls)
        self.assertEqual(expect_data, data)

    def test_get_schema(self):
        data = self.controller.get_type_schema(type_name='images')
        expect_data = {'name': 'images', 'version': '1.0',
                       'properties': {'foo': 'bar'}}
        expect_call = [('GET', '/schemas/images', {}, None)]
        self.assertEqual(expect_call, self.api.calls)
        self.assertEqual(expect_data, data)
