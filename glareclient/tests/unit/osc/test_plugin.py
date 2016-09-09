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

from glareclient.osc import plugin
from glareclient.tests.unit import base


class TestArtifactPlugin(base.TestCaseShell):

    @mock.patch("glareclient.v1.client.Client")
    def test_make_client(self, p_client):

        instance = mock.Mock()
        instance._api_version = {"artifact": '1'}
        instance._region_name = 'glare_region'
        instance.session = 'glare_session'

        plugin.make_client(instance)
        p_client.assert_called_with(
            mock.ANY,
            region_name='glare_region',
            session='glare_session',
            service_type='artifact')
