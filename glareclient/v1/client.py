
# Copyright 2012 OpenStack Foundation
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

from glareclient.common import http
from glareclient.v1 import artifacts
from glareclient.v1 import versions


class Client(object):
    """Client for the Glare Artifact Repository v1 API.

    :param string endpoint: A user-supplied endpoint URL for the glare service.
    :param string token: Token for authentication.
    """

    def __init__(self, endpoint, **kwargs):
        """Initialize a new client for the Glare v1 API."""

        self.version = kwargs.get('version')
        self.http_client = http.construct_http_client(endpoint, **kwargs)
        self.artifacts = artifacts.Controller(self.http_client)
        self.versions = versions.VersionController(self.http_client)
