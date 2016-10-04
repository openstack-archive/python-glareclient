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


class TestListArtifacts(TestArtifacts):

    def setUp(self):
        super(TestListArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.ListArtifacts(self.app, None)
        self.COLUMNS = ['Id', 'Name', 'Version',
                        'Owner', 'Visibility', 'Status']

    def test_artifact_list(self):
        arglist = ['sample_artifact']
        verify = [('type_name', 'sample_artifact')]

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
        arglist = ['sample_artifact',
                   '--filter', 'spam:spam',
                   '--filter', 'maps:maps']
        verify = [('type_name', 'sample_artifact'),
                  ('filter', ['spam:spam', 'maps:maps'])]

        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_with_sort(self):
        arglist = ['sample_artifact', '--sort', 'name:asc']
        verify = [('type_name', 'sample_artifact'),
                  ('sort', 'name:asc')]

        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_with_multisort(self):
        arglist = ['sample_artifact',
                   '--sort', 'name:desc',
                   '--sort', 'name:asc']
        verify = [('type_name', 'sample_artifact'),
                  ('sort', 'name:asc')]
        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_page_size(self):
        arglist = ['sample_artifact', '--page-size', '1']
        verify = [('type_name', 'sample_artifact'),
                  ('page_size', '1')]
        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_limit(self):
        arglist = ['sample_artifact', '--limit', '2']
        verify = [('type_name', 'sample_artifact'),
                  ('limit', '2')]
        self.check_parser(self.cmd, arglist, verify)

    def test_artifact_list_multilimit(self):
        arglist = ['sample_artifact', '--limit', '2', '--limit', '1']
        verify = [('type_name', 'sample_artifact'),
                  ('limit', '1')]
        self.check_parser(self.cmd, arglist, verify)


class TestShowArtifacts(TestArtifacts):

    def setUp(self):
        super(TestShowArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.ShowArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_artifact_show(self):
        arglist = ['sample_artifact', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact')]
        COLUMNS = ('blob', 'environment', 'id', 'image', 'name', 'owner',
                   'package', 'status', 'template', 'version', 'visibility')

        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        self.assertEqual(COLUMNS, columns)

    def test_artifact_show_without_id(self):
        arglist = ['sample_artifact']
        verify = [('type_name', 'sample_artifact')]

        with testtools.ExpectedException(ParserException):
            self.check_parser(self.cmd, arglist, verify)

    def test_artifact_show_without_type_id(self):
        arglist = ['fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact')]

        with testtools.ExpectedException(ParserException):
            self.check_parser(self.cmd, arglist, verify)


class TestCreateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestCreateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.CreateArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_create_artifact(self):
        arglist = ['sample_artifact', 'art',
                   '--artifact-version', '0.2.4',
                   '--property', 'blah=10']
        verify = [('type_name', 'sample_artifact'),
                  ('property', ['blah=10']),
                  ('artifact_version', '0.2.4')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)

    def test_create_artifact_multiproperty(self):
        arglist = ['sample_artifact', 'art',
                   '--artifact-version', '0.2.4',
                   '--property', 'blah=1',
                   '--property', 'blag=2']
        verify = [('type_name', 'sample_artifact'),
                  ('property', ['blah=1', 'blag=2']),
                  ('artifact_version', '0.2.4')]
        self.check_parser(self.cmd, arglist, verify)

    def test_create_artifact_multiversion(self):
        arglist = ['sample_artifact', 'art',
                   '--artifact-version', '0.2.4',
                   '--artifact-version', '0.2.5']
        verify = [('type_name', 'sample_artifact'),
                  ('artifact_version', '0.2.5')]
        self.check_parser(self.cmd, arglist, verify)


class TestUpdateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestUpdateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.UpdateArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_artifact_update(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--property', 'blah=1',
                   '--property', 'blag=2']
        verify = [('type_name', 'sample_artifact'),
                  ('property', ['blah=1', 'blag=2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)

    def test_artifact_update_bad(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--property', 'blah',
                   '--property', 'blah'
                   ]
        verify = [('type_name', 'sample_artifact')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        with testtools.ExpectedException(ValueError):
            self.cmd.take_action(parsed_args)

    def test_artifact_update_multiremove_prop(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba',
                   '--remove-property', 'prop1',
                   '--remove-property', 'prop2']
        verify = [('type_name', 'sample_artifact'),
                  ('remove_property', ['prop1', 'prop2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)


class TestDeleteArtifacts(TestArtifacts):

    def setUp(self):
        super(TestDeleteArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.DeleteArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_artifact_delete(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact'),
                  ('id', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)


class TestActivateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestActivateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.ActivateArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_artifact_activate(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact'),
                  ('id', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)


class TestDeactivateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestDeactivateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.DeactivateArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_artifact_deactivate(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact'),
                  ('id', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)


class TestReactivateArtifacts(TestArtifacts):

    def setUp(self):
        super(TestReactivateArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.ReactivateArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_artifact_rectivate(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact'),
                  ('id', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)


class TestPublishArtifacts(TestArtifacts):

    def setUp(self):
        super(TestPublishArtifacts, self).setUp()
        self.artifact_mock.call.return_value = \
            api_art.Controller(self.http, type_name='sample_artifact')

        # Command to test
        self.cmd = osc_art.PublishArtifact(self.app, None)
        self.COLUMNS = ('id', 'name', 'owner',
                        'status', 'version', 'visibility')

    def test_publish_delete(self):
        arglist = ['sample_artifact',
                   'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba']
        verify = [('type_name', 'sample_artifact'),
                  ('id', 'fc15c365-d4f9-4b8b-a090-d9e230f1f6ba')]
        parsed_args = self.check_parser(self.cmd, arglist, verify)
        columns, data = self.cmd.take_action(parsed_args)
        # Check that columns are correct
        self.assertEqual(self.COLUMNS, columns)
