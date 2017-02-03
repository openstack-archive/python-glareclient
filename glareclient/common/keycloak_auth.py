# Copyright 2016 - Nokia Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import logging
import pprint
import requests

LOG = logging.getLogger(__name__)


def authenticate(**kwargs):
    """Performs authentication using Keycloak OpenID Protocol.

    :param auth_url: Base authentication url of KeyCloak server (e.g.
            "https://my.keycloak:8443/auth"
    :param client_id: Client ID (according to OpenID Connect protocol).
    :param realm_name: KeyCloak realm name.
    :param username: User name (Optional, if None then access_token must be
            provided).
    :param password: Password (Optional).
    :param insecure: If True, SSL certificate is not verified (Optional).

    """
    auth_url = kwargs.get('auth_url')
    client_id = kwargs.get('client_id')
    realm_name = kwargs.get('realm_name')
    username = kwargs.get('username')
    password = kwargs.get('password')
    insecure = kwargs.get('insecure', False)

    if not auth_url:
        raise ValueError('Base authentication url is not provided.')

    if not client_id:
        raise ValueError('Client ID is not provided.')

    if not realm_name:
        raise ValueError('Project(realm) name is not provided.')

    if not username:
        raise ValueError('Username is not provided.')

    if password is None:
        raise ValueError('Password is not provided.')

    access_token_endpoint = (
        "%s/realms/%s/protocol/openid-connect/token" %
        (auth_url, realm_name)
    )

    body = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'scope': 'profile',
        'client_id': client_id
    }

    resp = requests.post(
        access_token_endpoint,
        data=body,
        verify=not insecure
    )

    try:
        resp.raise_for_status()
    except Exception as e:
        raise Exception("Failed to get access token:\n %s" % str(e))

    LOG.debug(
        "HTTP response from OIDC provider: %s" %
        pprint.pformat(resp.json())
    )

    return resp.json()['access_token']
