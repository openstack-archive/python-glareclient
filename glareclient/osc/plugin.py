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

import logging

from osc_lib import utils

from glareclient._i18n import _

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = "1"
API_VERSION_OPTION = "os_artifact_api_version"
API_NAME = "artifact"
API_VERSIONS = {
    '1': 'glareclient.v1.client.Client',
}


def make_client(instance):
    """Returns an artifact service client"""
    glare_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug("Instantiating glare client: {0}".format(
              glare_client))
    kwargs = dict(
        region_name=instance._region_name,
        session=instance.session,
        service_type='artifact',
    )
    return glare_client(instance.get_configuration().get('glare_url'),
                        **kwargs)


def build_option_parser(parser):
    """Hook to add global options"""
    parser.add_argument(
        '--os-artifact-api-version',
        metavar='<artifact-api-version>',
        default=utils.env('OS_ARTIFACT_API_VERSION'),
        help=_('Artifact API version, default=%s '
               '(Env: OS_ARTIFACT_API_VERSION)') % DEFAULT_API_VERSION)
