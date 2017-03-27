# Copyright 2012 OpenStack Foundation.
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

import copy
import hashlib
import os
import socket

from keystoneauth1 import adapter
from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import encodeutils
import requests
import six
from six.moves import urllib

from glareclient.common import exceptions as exc
from glareclient.common import keycloak_auth

LOG = logging.getLogger(__name__)
USER_AGENT = 'python-glareclient'
CHUNKSIZE = 1024 * 64  # 64kB


def get_system_ca_file():
    """Return path to system default CA file."""
    # Standard CA file locations for Debian/Ubuntu, RedHat/Fedora,
    # Suse, FreeBSD/OpenBSD, MacOSX, and the bundled ca
    ca_path = ['/etc/ssl/certs/ca-certificates.crt',
               '/etc/pki/tls/certs/ca-bundle.crt',
               '/etc/ssl/ca-bundle.pem',
               '/etc/ssl/cert.pem',
               '/System/Library/OpenSSL/certs/cacert.pem',
               requests.certs.where()]
    for ca in ca_path:
        LOG.debug("Looking for ca file %s", ca)
        if os.path.exists(ca):
            LOG.debug("Using ca file %s", ca)
            return ca
    LOG.warning("System ca file could not be found.")


def _handle_response(resp):
        content_type = resp.headers.get('Content-Type')
        if not content_type:
            body_iter = six.StringIO(resp.text)
            try:
                body_iter = jsonutils.loads(''.join([c for c in body_iter]))
            except ValueError:
                body_iter = None
        elif 'json' in content_type:
            # Let's use requests json method, it should take care of
            # response encoding
            try:
                body_iter = resp.json()
            except Exception:
                body_iter = None
        else:
            # Do not read all response in memory when downloading a blob.
            body_iter = _close_after_stream(resp, CHUNKSIZE)
        return resp, body_iter


def _close_after_stream(response, chunk_size):
    """Iterate over the content and ensure the response is closed after."""
    # Yield each chunk in the response body
    for chunk in response.iter_content(chunk_size=chunk_size):
        yield chunk
    # Once we're done streaming the body, ensure everything is closed.
    # This will return the connection to the HTTPConnectionPool in urllib3
    # and ideally reduce the number of HTTPConnectionPool full warnings.
    response.close()


class HTTPClient(object):

    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.auth_url = kwargs.get('auth_url')
        self.auth_token = kwargs.get('auth_token')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.region_name = kwargs.get('region_name')
        self.include_pass = kwargs.get('include_pass')
        self.endpoint_url = endpoint
        self.tenant_name = kwargs.get('tenant_name')

        self.cert_file = kwargs.get('cert_file')
        self.key_file = kwargs.get('key_file')
        self.timeout = kwargs.get('timeout')

        self.ssl_connection_params = {
            'cacert': kwargs.get('cacert'),
            'cert_file': kwargs.get('cert_file'),
            'key_file': kwargs.get('key_file'),
            'insecure': kwargs.get('insecure'),
        }

        self.verify_cert = None
        if urllib.parse.urlparse(endpoint).scheme == "https":
            if kwargs.get('insecure'):
                self.verify_cert = False
            else:
                self.verify_cert = kwargs.get('cacert', get_system_ca_file())

    def _safe_header(self, name, value):
        if name in ['X-Auth-Token', 'X-Subject-Token']:
            # because in python3 byte string handling is ... ug
            v = value.encode('utf-8')
            h = hashlib.sha1(v)
            d = h.hexdigest()
            return encodeutils.safe_decode(name), "{SHA1}%s" % d
        else:
            return (encodeutils.safe_decode(name),
                    encodeutils.safe_decode(value))

    def log_curl_request(self, url, method, kwargs):
        curl = ['curl -i -X %s' % method]

        for (key, value) in kwargs['headers'].items():
            header = '-H \'%s: %s\'' % self._safe_header(key, value)
            curl.append(header)

        conn_params_fmt = [
            ('key_file', '--key %s'),
            ('cert_file', '--cert %s'),
            ('cacert', '--cacert %s'),
        ]
        for (key, fmt) in conn_params_fmt:
            value = self.ssl_connection_params.get(key)
            if value:
                curl.append(fmt % value)

        if self.ssl_connection_params.get('insecure'):
            curl.append('-k')

        if 'data' in kwargs:
            curl.append('-d \'%s\'' % kwargs['data'])

        curl.append('%s%s' % (self.endpoint, url))
        LOG.debug(' '.join(curl))

    @staticmethod
    def log_http_response(resp):
        status = (resp.raw.version / 10.0, resp.status_code, resp.reason)
        dump = ['\nHTTP/%.1f %s %s' % status]
        dump.extend(['%s: %s' % (k, v) for k, v in resp.headers.items()])
        dump.append('')
        if resp.content:
            content = resp.content
            if isinstance(content, six.binary_type):
                try:
                    content = encodeutils.safe_decode(resp.content)
                except UnicodeDecodeError:
                    pass
                else:
                    dump.extend([content, ''])
        LOG.debug('\n'.join(dump))

    def request(self, url, method, log=True, **kwargs):
        """Send an http request with the specified characteristics.

        Wrapper around requests.request to handle tasks such
        as setting headers and error handling.
        """
        # Copy the kwargs so we can reuse the original in case of redirects
        kwargs['headers'] = copy.deepcopy(kwargs.get('headers', {}))
        kwargs['headers'].setdefault('User-Agent', USER_AGENT)
        if self.auth_token:
            kwargs['headers'].setdefault('X-Auth-Token', self.auth_token)
        else:
            kwargs['headers'].update(self.credentials_headers())
        if self.auth_url:
            kwargs['headers'].setdefault('X-Auth-Url', self.auth_url)
        if self.region_name:
            kwargs['headers'].setdefault('X-Region-Name', self.region_name)
        if self.tenant_name:
            kwargs['headers'].setdefault('X-Project-Id', self.tenant_name)

        self.log_curl_request(url, method, kwargs)

        if self.cert_file and self.key_file:
            kwargs['cert'] = (self.cert_file, self.key_file)

        if self.verify_cert is not None:
            kwargs['verify'] = self.verify_cert

        if self.timeout is not None:
            kwargs['timeout'] = float(self.timeout)

        # Allow the option not to follow redirects
        follow_redirects = kwargs.pop('redirect', True)

        # Since requests does not follow the RFC when doing redirection to sent
        # back the same method on a redirect we are simply bypassing it.  For
        # example if we do a DELETE/POST/PUT on a URL and we get a 302 RFC says
        # that we should follow that URL with the same method as before,
        # requests doesn't follow that and send a GET instead for the method.
        # Hopefully this could be fixed as they say in a comment in a future
        # point version i.e.: 3.x
        # See issue: https://github.com/kennethreitz/requests/issues/1704
        allow_redirects = False
        try:
            resp = requests.request(
                method,
                self.endpoint_url + url,
                allow_redirects=allow_redirects,
                **kwargs)
        except socket.gaierror as e:
            message = ("Error finding address for %(url)s: %(e)s" %
                       {'url': self.endpoint_url + url, 'e': e})
            raise exc.InvalidEndpoint(message=message)
        except (socket.error,
                socket.timeout,
                requests.exceptions.ConnectionError) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s" %
                       {'endpoint': endpoint, 'e': e})
            raise exc.CommunicationError(message=message)

        if log:
            self.log_http_response(resp)

        if 'X-Auth-Key' not in kwargs['headers'] and \
                (resp.status_code == 401 or
                 (resp.status_code == 500 and
                  "(HTTP 401)" in resp.content)):
            raise exc.HTTPUnauthorized("Authentication failed. Please try"
                                       " again.\n%s"
                                       % resp.content)
        elif 400 <= resp.status_code < 600:
            raise exc.from_response(resp)
        elif resp.status_code in (301, 302, 305):
            # Redirected. Reissue the request to the new location,
            # unless caller specified follow_redirects=False
            if follow_redirects:
                location = resp.headers.get('location')
                path = self.strip_endpoint(location)
                resp = self.request(path, method, **kwargs)
        elif resp.status_code == 300:
            raise exc.from_response(resp)

        return resp

    def strip_endpoint(self, location):
        if location is None:
            message = "Location not returned with 302"
            raise exc.InvalidEndpoint(message=message)
        elif location.startswith(self.endpoint):
            return location[len(self.endpoint):]
        else:
            message = "Prohibited endpoint redirect %s" % location
            raise exc.InvalidEndpoint(message=message)

    def credentials_headers(self):
        creds = {}
        if self.username:
            creds['X-Auth-User'] = self.username
        if self.password:
            creds['X-Auth-Key'] = self.password
        return creds

    def process_request(self, url, method, **kwargs):
        resp = self.request(url, method, **kwargs)
        return _handle_response(resp)

    def head(self, url, **kwargs):
        return self.process_request(url, "HEAD", **kwargs)

    def get(self, url, **kwargs):
        return self.process_request(url, "GET", **kwargs)

    def post(self, url, **kwargs):
        return self.process_request(url, "POST", **kwargs)

    def put(self, url, **kwargs):
        return self.process_request(url, "PUT", **kwargs)

    def delete(self, url, **kwargs):
        return self.request(url, "DELETE", **kwargs)

    def patch(self, url, **kwargs):
        return self.process_request(url, "PATCH", **kwargs)


class SessionClient(adapter.LegacyJsonAdapter):
    """HTTP client based on Keystone client session."""

    def request(self, url, method, **kwargs):
        resp, body = super(SessionClient, self).request(
            url, method, **kwargs)

        if resp.status_code == 300 or (400 <= resp.status_code < 600):
            raise exc.from_response(resp)

        return resp, body


def construct_http_client(*args, **kwargs):
    session = kwargs.pop('session', None)
    auth = kwargs.pop('auth', None)
    endpoint = next(iter(args), None)
    keycloak_auth_url = kwargs.pop('keycloak_auth_url', None)
    auth_token = kwargs.pop('auth_token', None)
    if session:
        service_type = kwargs.pop('service_type', None)
        endpoint_type = kwargs.pop('endpoint_type', None)
        region_name = kwargs.pop('region_name', None)
        service_name = kwargs.pop('service_name', None)
        parameters = {
            'endpoint_override': endpoint,
            'session': session,
            'auth': auth,
            'interface': endpoint_type,
            'service_type': service_type,
            'region_name': region_name,
            'service_name': service_name,
            'user_agent': 'python-glareclient',
        }
        parameters.update(kwargs)
        return SessionClient(**parameters)
    elif endpoint:
        realm_name = kwargs.pop('keycloak_realm_name', None)
        if keycloak_auth_url:
            kwargs['auth_token'] = keycloak_auth.authenticate(
                auth_url=keycloak_auth_url,
                client_id=kwargs.pop('openid_client_id', None),
                username=kwargs.pop('keycloak_username', None),
                password=kwargs.pop('keycloak_password', None),
                realm_name=realm_name
            )
        else:
            kwargs['auth_token'] = auth_token
        return HTTPClient(endpoint, **kwargs)
    else:
        raise AttributeError('Constructing a client must contain either an '
                             'endpoint or a session')
