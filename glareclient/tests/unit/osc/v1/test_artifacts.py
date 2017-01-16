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

import testtools

from glareclient.osc.v1 import artifacts as osc_art
from glareclient.tests.unit.osc.v1 import fakes
from glareclient.v1 import artifacts as api_art
from osc_lib.tests.utils import ParserException


class TestArtifacts(fakes.TestArtifacts):
    def setUp(self):
        super(TestArtifacts, self).setUp()
        self.artifact_mock = \
            self.app.client_manager.artifact.artifacts
        self.http = mock.MagicMock()
        self.COLUMNS = set(['id', 'name', 'owner',
                            'status', 'version', 'visibility'])


class TestListArtifacts(TestArtifacts):

    def setUp(self):
        super(TestListArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.ListArtifacts(self.app, None)
        self.COLUMNS = ['Id', 'Name', 'Version',
                        'Owner', 'Visibility', 'Status']

    def test_artifact_list(self):
        arglist = ['images']
        verify = [('type_name', 'images')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)

        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_all(self):
        arglist = ['all']
        verify = [('type_name', 'all')]

        parsed_args = self.check_parser(self.cmd, arglist, verify)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        self.assertEqual(['Id', 'Name', 'Version', 'Type name',
                          'Owner', 'Visibility', 'Status'], columns)

        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_with_multifilters(self):
        arglist = ['images',
                   '--filter', 'spam:spam',
                   '--filter', 'maps:maps']
        verify = [('type_name', 'images'),
                  ('filter', ['spam:spam', 'maps:maps'])]

        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_with_sort(self):
        arglist = ['sample_artifact', '--sort', 'name:asc']
        verify = [('type_name', 'sample_artifact'),
                  ('sort', 'name:asc')]

        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_with_multisort(self):
        arglist = ['images',
                   '--sort', 'name:desc',
                   '--sort', 'name:asc']
        verify = [('type_name', 'images'),
                  ('sort', 'name:asc')]
        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_page_size(self):
        arglist = ['images', '--page-size', '1']
        verify = [('type_name', 'images'),
                  ('page_size', 1)]
        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_limit(self):
        arglist = ['images', '--limit', '2']
        verify = [('type_name', 'images'),
                  ('limit', 2)]
        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_multilimit(self):
        arglist = ['images', '--limit', '2', '--limit', '1']
        verify = [('type_name', 'images'),
                  ('limit', 1)]
        self.check_parser(self.cmd, arglist, verify)


class TestShowArtifacts(TestArtifacts):

    def setUp(self):
        super(TestShowArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.ShowArtifact(self.app, None)

    def test_artifact_show(self):
        arglist = ['images', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'images')]
        COLUMNS = set(['blob', 'environment', 'id', 'image',
                       'name', 'owner', 'package', 'status',
                       'template', 'version', 'visibility'])

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(COLUMNS, name_fields)

    def test_artifact_show_without_id(self):
        arglist = ['images']
        verify = [('type_name', 'images')]

        with testtools.ExpectedException(ParserException):
            self.check_parser(self.cmd, arglist, verify)

    def test_artifact_show_without_type_id(self):
        arglist = ['fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'images')]

        with testtools.ExpectedException(ParserException):
            self.check_parser(self.cmd, arglist, verify)

    def test_artifact_show_by_name(self):
        arglist = ['images', 'name1']
        verify = [('type_name', 'images'), ('id', False)]
        COLUMNS = set(['blob', 'environment', 'id', 'image',
                       'name', 'owner', 'package', 'status',
                       'template', 'version', 'visibility'])

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(COLUMNS, name_fields)


class TestCreateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestCreateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.CreateArtifact(self.app, None)

    def test_create_artifact(self):
        arglist = ['images', 'art',
                   '--artifact-version', '0.2.4',
                   '--property', 'blah=10']
        verify = [('type_name', 'images'),
                  ('property', ['blah=10']),
                  ('artifact_version', '0.2.4')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)

    def test_create_artifact_list_prop(self):
        arglist = ['images', 'art',
                   '--artifact-version', '0.2.4',
                   '--list', 'l=10,11,12']
        verify = [('type_name', 'images'),
                  ('list', ['l=10,11,12']),
                  ('artifact_version', '0.2.4')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with mock.patch.object(
                self.app.client_manager.artifact.artifacts,
                'create') as patched_create:
            self.cmd.take_action(parsed_args)
            patched_create.assert_called_once_with(
                'art',
                l=['10', '11', '12'],
                type_name='images',
                version='0.2.4')

    def test_create_artifact_dict_prop(self):
        arglist = ['images', 'art',
                   '--artifact-version', '0.2.4',
                   '--dict', 'd=a:10,b:11,c:12']
        verify = [('type_name', 'images'),
                  ('dict', ['d=a:10,b:11,c:12']),
                  ('artifact_version', '0.2.4')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with mock.patch.object(
                self.app.client_manager.artifact.artifacts,
                'create') as patched_create:
            self.cmd.take_action(parsed_args)
            patched_create.assert_called_once_with(
                'art',
                d={'a': '10', 'c': '12', 'b': '11'},
                type_name='images',
                version='0.2.4')

    def test_create_artifact_multiproperty(self):
        arglist = ['images', 'art',
                   '--artifact-version', '0.2.4',
                   '--property', 'blah=1',
                   '--property', 'blag=2']
        verify = [('type_name', 'images'),
                  ('property', ['blah=1', 'blag=2']),
                  ('artifact_version', '0.2.4')]
        self.check_parser(self.cmd, arglist, verify)

    def test_create_artifact_multiversion(self):
        arglist = ['images', 'art',
                   '--artifact-version', '0.2.4',
                   '--artifact-version', '0.2.5']
        verify = [('type_name', 'images'),
                  ('artifact_version', '0.2.5')]
        self.check_parser(self.cmd, arglist, verify)


class TestUpdateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestUpdateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.UpdateArtifact(self.app, None)

    def test_artifact_update(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--property', 'blah=1',
                   '--property', 'blag=2']
        verify = [('type_name', 'images'),
                  ('property', ['blah=1', 'blag=2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)

    def test_update_artifact_list_prop(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--list', 'l=10,11,12']
        verify = [('type_name', 'images'),
                  ('list', ['l=10,11,12'])]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with mock.patch.object(
                self.app.client_manager.artifact.artifacts,
                'update') as patched_update:
            self.cmd.take_action(parsed_args)
            patched_update.assert_called_once_with(
                'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                l=['10', '11', '12'],
                remove_props=[],
                type_name='images')

    def test_update_artifact_dict_prop(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--dict', 'd=a:10,b:11,c:12']
        verify = [('type_name', 'images'),
                  ('dict', ['d=a:10,b:11,c:12'])]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with mock.patch.object(
                self.app.client_manager.artifact.artifacts,
                'update') as patched_update:
            self.cmd.take_action(parsed_args)
            patched_update.assert_called_once_with(
                'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                d={'a': '10', 'c': '12', 'b': '11'},
                remove_props=[],
                type_name='images')

    def test_artifact_update_bad(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--property', 'blah',
                   '--property', 'blah'
                   ]
        verify = [('type_name', 'images')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with testtools.ExpectedException(ValueError):
            self.cmd.take_action(parsed_args)

    def test_artifact_update_multiremove_prop(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--remove-property', 'prop1',
                   '--remove-property', 'prop2']
        verify = [('type_name', 'images'),
                  ('remove_property', ['prop1', 'prop2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TestDeleteArtifacts(TestArtifacts):

    def setUp(self):
        super(TestDeleteArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.DeleteArtifact(self.app, None)

    def test_artifact_delete(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        self.assertIsNone(self.cmd.take_action(parsed_args))


class TestActivateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestActivateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.ActivateArtifact(self.app, None)

    def test_artifact_activate(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--id']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TestDeactivateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestDeactivateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.DeactivateArtifact(self.app, None)

    def test_artifact_deactivate(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TestReactivateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestReactivateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.ReactivateArtifact(self.app, None)

    def test_artifact_rectivate(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TestAddTag(TestArtifacts):

    def setUp(self):
        super(TestAddTag, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.AddTag(self.app, None)

    def test_artifact_add_tag(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id',
                   '123']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True),
                  ('tag', '123')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TestRemoveTag(TestArtifacts):

    def setUp(self):
        super(TestRemoveTag, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.RemoveTag(self.app, None)

    def test_artifact_add_tag(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id',
                   '123']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True),
                  ('tag', '123')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TestPublishArtifacts(TestArtifacts):

    def setUp(self):
        super(TestPublishArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.PublishArtifact(self.app, None)

    def test_publish_delete(self):
        arglist = ['images',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba', '--id']
        verify = [('type_name', 'images'),
                  ('name', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba'),
                  ('id', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        name_fields = set([column[0] for column in data])
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, name_fields)


class TypeSchema(TestArtifacts):

    def setUp(self):
        super(TypeSchema, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='images')

        # Command to test
        self.cmd = osc_art.TypeSchema(self.app, None)

    def test_get_schema(self):
        arglist = ['images']
        verify = [('type_name', 'images')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        exp_columns = ['Name', 'Glare_type', 'Mutable', 'Required',
                       'Sortable', 'Filters', 'Available_values']
        exp_data = [
            (u'image', u'Blob', False, False, False, [], ''),
            (u'updated_at', u'DateTime', False, True, True,
             [u'eq', u'neq', u'in', u'gt', u'gte', u'lt', u'lte'], ''),
            (u'owner', u'String', False, False, True,
             [u'eq', u'neq', u'in'], ''),
            (u'provided_by', u'StringDict', False, False, False,
             [u'eq', u'neq', u'in'], ''),
            (u'id', u'String', False, True, True, [u'eq', u'neq', u'in'], ''),
            (u'environment', u'Blob', False, True, False, [], ''),
            (u'version', u'String', False, False, True,
             [u'eq', u'neq', u'in', u'gt', u'gte', u'lt', u'lte'], ''),
            (u'blob', u'Blob', True, False, False, [], ''),
            (u'template', u'Blob', False, True, False, [], ''),
            (u'metadata', u'StringDict', False, False, False,
             [u'eq', u'neq'], ''),
            (u'status', u'String', False, True, True, [u'eq', u'neq', u'in'],
             [u'drafted', u'active', u'deactivated', u'deleted']),
            (u'description', u'String', True, False, False,
             [u'eq', u'neq', u'in'], ''),
            (u'tags', u'StringList', True, False, False,
             [u'eq', u'neq', u'in'], ''),
            (u'activated_at', u'DateTime', False, False, True,
             [u'eq', u'neq', u'in', u'gt', u'gte', u'lt', u'lte'], ''),
            (u'supported_by', u'StringDict', False, False, False,
             [u'eq', u'neq', u'in'], ''),
            (u'visibility', u'String', False, True, True, [u'eq'], ''),
            (u'icon', u'Blob', False, False, False, [], ''),
            (u'name', u'String', False, False, True,
             [u'eq', u'neq', u'in'], ''),
            (u'license', u'String', False, False, False,
             [u'eq', u'neq', u'in'], ''),
            (u'package', u'Blob', False, False, False, [], ''),
            (u'created_at', u'DateTime', False, True, True,
             [u'eq', u'neq', u'in', u'gt', u'gte', u'lt', u'lte'], ''),
            (u'license_url', u'String', False, False, False,
             [u'eq', u'neq', u'in'], ''),
            (u'release', u'StringList', False, False, False,
             [u'eq', u'neq', u'in'], '')]

        data.sort(key=lambda x: x[0])
        exp_data.sort(key=lambda x: x[0])

        # Check that columns are correct
        self.assertEqual(exp_columns, columns)
        self.assertEqual(exp_data, data)
