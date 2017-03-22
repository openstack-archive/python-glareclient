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

import mock
from oslo_serialization import jsonutils
import testtools

from glareclient.v1 import artifacts


class TestController(testtools.TestCase):

    def setUp(self):
        self.mock_resp = mock.MagicMock()
        self.mock_body = mock.MagicMock()
        self.mock_http_client = mock.MagicMock()
        for method in ('get', 'post', 'patch', 'delete'):
            method = getattr(self.mock_http_client, method)
            method.return_value = (self.mock_resp, self.mock_body)
        self.c = artifacts.Controller(self.mock_http_client, 'test_name')
        self.c._check_type_name = mock.Mock(return_value='checked_name')
        super(TestController, self).setUp()

    def test_create(self):
        body = self.c.create('name', version='0.1.2', type_name='ok')
        self.assertEqual(self.mock_body, body)
        self.mock_http_client.post.assert_called_once_with(
            '/artifacts/checked_name',
            json={'version': '0.1.2', 'name': 'name'})
        self.c._check_type_name.assert_called_once_with('ok')

    def test_update(self):
        remove_props = ['remove1', 'remove2']
        body = self.c.update('test-id', type_name='test_name',
                             remove_props=remove_props, update1=1, update2=2)
        self.assertEqual(self.mock_body, body)
        patch_kwargs = {
            'headers': {'Content-Type': 'application/json-patch+json'},
            'json': [
                {'path': '/remove1', 'value': None, 'op': 'replace'},
                {'path': '/remove2', 'value': None, 'op': 'replace'},
                {'path': '/update2', 'value': 2, 'op': 'add'},
                {'path': '/update1', 'value': 1, 'op': 'add'}
            ]
        }
        self.mock_http_client.patch.assert_called_once_with(
            '/artifacts/checked_name/test-id', **patch_kwargs)
        self.c._check_type_name.assert_called_once_with('test_name')

    def test_get(self):
        body = self.c.get('test-id', type_name='test_name')
        self.assertEqual(self.mock_body, body)
        self.mock_http_client.get.assert_called_once_with(
            '/artifacts/checked_name/test-id')
        self.c._check_type_name.assert_called_once_with('test_name')

    def test_list(self):
        self.mock_http_client.get.side_effect = [
            (None, {'checked_name': [10, 11, 12], "next": "next1"}),
            (None, {'checked_name': [13, 14, 15], "next": "next2"}),
            (None, {'checked_name': [16, 17, 18], "next": "next3"}),
            (None, {'checked_name': [19, 20, 21]}),
        ]
        data = list(self.c.list(type_name='test-type', limit=10, page_size=3))
        expected = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        self.assertEqual(expected, data)
        expected_calls = [
            mock.call.get('/artifacts/checked_name?&limit=3'),
            mock.call.get('next1'),
            mock.call.get('next2'),
            mock.call.get('next3'),
        ]
        self.assertEqual(expected_calls, self.mock_http_client.mock_calls)

    def test_activate(self):
        self.c.update = mock.Mock()
        self.assertEqual(self.c.update.return_value,
                         self.c.activate('test-id', type_name='test-type'))
        self.c.update.assert_called_once_with('test-id', 'test-type',
                                              status='active')

    def test_deactivate(self):
        self.c.update = mock.Mock()
        self.assertEqual(self.c.update.return_value,
                         self.c.deactivate('test-id', type_name='test-type'))
        self.c.update.assert_called_once_with('test-id', 'test-type',
                                              status='deactivated')

    def test_reactivate(self):
        self.c.update = mock.Mock()
        self.assertEqual(self.c.update.return_value,
                         self.c.reactivate('test-id', type_name='test-type'))
        self.c.update.assert_called_once_with('test-id', 'test-type',
                                              status='active')

    def test_delete(self):
        self.assertIsNone(self.c.delete('test-id', type_name='test-name'))
        self.mock_http_client.delete.assert_called_once_with(
            '/artifacts/checked_name/test-id')

    def test_upload_blob(self):
        self.c.upload_blob('test-id', 'blob-prop', 'data',
                           type_name='test-type',
                           content_type='application/test')
        self.mock_http_client.put.assert_called_once_with(
            '/artifacts/checked_name/test-id/blob-prop',
            data='data', headers={'Content-Type': 'application/test'})

    def test_get_type_list(self):
        schemas = {'schemas': {'a': {'version': 1}, 'b': {'version': 2}}}
        self.mock_http_client.get.return_value = (None, schemas)
        expected_types = [('a', 1), ('b', 2)]
        self.assertEqual(expected_types, self.c.get_type_list())

    def test_get_type_schema(self):
        test_schema = {'schemas': {'checked_name': 'test-schema'}}
        self.mock_http_client.get.return_value = (None, test_schema)
        self.assertEqual('test-schema',
                         self.c.get_type_schema(type_name='test-type'))
        self.mock_http_client.get.assert_called_once_with(
            '/schemas/checked_name')

    def test_add_external_location(self):
        art_id = '3a4560a1-e585-443e-9b39-553b46ec92a8'
        data = {
            'url': 'http://fake_url',
            'md5': '7CA772EE98D5CAF99F3674085D5E4124',
            'sha1': None,
            'sha256': None},
        resp = self.c.add_external_location(
            art_id, 'image',
            data=data,
            type_name='images')
        self.c.http_client.put.assert_called_once_with(
            '/artifacts/checked_name/'
            '3a4560a1-e585-443e-9b39-553b46ec92a8/image',
            data=jsonutils.dumps(data),
            headers={'Content-Type':
                     'application/vnd+openstack.glare-custom-location+json'})
        self.assertIsNone(resp)

    def test_add_tag(self):
        art_id = '07a679d8-d0a8-45ff-8d6e-2f32f2097b7c'
        d = {'tags': ['a', 'b', 'c']}
        self.mock_body.__getitem__.side_effect = d.__getitem__
        data = self.c.add_tag(
            art_id, tag_value="123", type_name='images')
        self.c.http_client.get.assert_called_once_with(
            '/artifacts/checked_name/07a679d8-d0a8-45ff-8d6e-2f32f2097b7c')
        self.c.http_client.patch.assert_called_once_with(
            '/artifacts/checked_name/07a679d8-d0a8-45ff-8d6e-2f32f2097b7c',
            headers={'Content-Type': 'application/json-patch+json'},
            json=[{'path': '/tags',
                   'value': ['a', 'b', 'c', '123'],
                   'op': 'add'}])
        self.assertIsNotNone(data)

    def test_add_existing_tag(self):
        art_id = '07a679d8-d0a8-45ff-8d6e-2f32f2097b7c'
        d = {'tags': ['a', 'b', 'c']}
        self.mock_body.__getitem__.side_effect = d.__getitem__
        data = self.c.add_tag(
            art_id, tag_value="a", type_name='images')
        self.c.http_client.get.assert_called_once_with(
            '/artifacts/checked_name/07a679d8-d0a8-45ff-8d6e-2f32f2097b7c')
        self.assertEqual(0, self.c.http_client.patch.call_count)
        self.assertIsNotNone(data)

    def test_remove_tag(self):
        art_id = '07a679d8-d0a8-45ff-8d6e-2f32f2097b7c'
        d = {'tags': ['a', 'b', 'c']}
        self.mock_body.__getitem__.side_effect = d.__getitem__
        data = self.c.remove_tag(
            art_id, tag_value="a", type_name='images')
        self.c.http_client.get.assert_called_once_with(
            '/artifacts/checked_name/07a679d8-d0a8-45ff-8d6e-2f32f2097b7c')
        self.c.http_client.patch.assert_called_once_with(
            '/artifacts/checked_name/07a679d8-d0a8-45ff-8d6e-2f32f2097b7c',
            headers={'Content-Type': 'application/json-patch+json'},
            json=[{'path': '/tags',
                   'value': ['b', 'c'],
                   'op': 'add'}])
        self.assertIsNotNone(data)

    def test_remove_nonexisting_tag(self):
        art_id = '07a679d8-d0a8-45ff-8d6e-2f32f2097b7c'
        d = {'tags': ['a', 'b', 'c']}
        self.mock_body.__getitem__.side_effect = d.__getitem__
        data = self.c.remove_tag(
            art_id, tag_value="123", type_name='images')
        self.c.http_client.get.assert_called_once_with(
            '/artifacts/checked_name/07a679d8-d0a8-45ff-8d6e-2f32f2097b7c')
        self.assertEqual(0, self.c.http_client.patch.call_count)
        self.assertIsNotNone(data)
