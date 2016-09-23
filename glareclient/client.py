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

from glareclient.common import utils


def Client(version='1', endpoint=None, session=None, *args, **kwargs):
    """Client for the Glare Artifact Repository.

    Generic client for the Glare Artifact Repository. See version classes
    for specific details.
    :param string version: The version of API to use.
    :param session: A keystoneauth1 session that should be used for transport.
    :type session: keystoneauth1.session.Session
    """

    if endpoint is not None:
        kwargs.setdefault('endpoint_override', endpoint)

    if version is None:
        raise RuntimeError("You must provide a client version")

    module = utils.import_versioned_module(int(version), 'client')
    client_class = getattr(module, 'Client')
    return client_class(endpoint, *args, session=session, **kwargs)
