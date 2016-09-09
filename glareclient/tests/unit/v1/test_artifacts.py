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

from glareclient.tests.unit.v1 import fixtures
from glareclient.tests import utils
from glareclient.v1 import artifacts


class TestController(testtools.TestCase):
    def setUp(self):
        super(TestController, self).setUp()
        self.api = utils.FakeAPI(fixtures.data_fixtures)
        self.controller = artifacts.Controller(self.api)

    def test_list_artifacts(self):
        artifacts = list(self.controller.list(type_name='sample_artifact'))
        self.assertEqual('3a4560a1-e585-443e-9b39-553b46ec92d1',
                         artifacts[0]['id'])
        self.assertEqual('art1', artifacts[0]['name'])
        self.assertEqual('db721fb0-5b85-4738-9401-f161d541de5e',
                         artifacts[1]['id'])
        self.assertEqual('art2', artifacts[1]['name'])
        self.assertEqual('e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                         artifacts[2]['id'])
        self.assertEqual('art3', artifacts[2]['name'])
