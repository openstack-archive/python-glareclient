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

from __future__ import print_function

import errno
import hashlib
import os
import sys

if os.name == 'nt':
    import msvcrt
else:
    msvcrt = None

from oslo_utils import encodeutils
from oslo_utils import importutils
import requests

from glareclient import exc

SENSITIVE_HEADERS = ('X-Auth-Token', )


def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars.

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


def import_versioned_module(version, submodule=None):
    module = 'glareclient.v%s' % version
    if submodule:
        module = '.'.join((module, submodule))
    return importutils.import_module(module)


def exit(msg='', exit_code=1):
    if msg:
        print(encodeutils.safe_decode(msg), file=sys.stderr)
    sys.exit(exit_code)


class ResponseBlobWrapper(object):
    """Represent HTTP response as iterator with known length."""

    def __init__(self, resp, verify_md5=True):
        self.hash_md5 = resp.headers.get("Content-MD5")
        self.blob_md5 = hashlib.md5()
        if 301 <= resp.status_code <= 302:
            # NOTE(sskripnick): handle redirect manually to prevent sending
            # auth token to external resource.
            # Use stream=True to prevent reading whole response into memory.
            # Set Accept-Encoding explicitly to "identity" because setting
            # stream=True forces Accept-Encoding to be "gzip, deflate".
            # It should be "identity" because we should know Content-Length.
            resp = requests.get(resp.headers.get("Location"),
                                headers={"Accept-Encoding": "identity"})
        self.len = resp.headers.get("Content-Length", 0)
        self.iter = resp.iter_content(65536)
        self.verify_md5 = verify_md5

    def __iter__(self):
        return self

    def next(self):
        try:
            data = self.iter.next()
            if self.verify_md5:
                self.blob_md5.update(data)
            return data
        except StopIteration:
            if self.verify_md5 and self.blob_md5.hexdigest() != self.hash_md5:
                raise IOError(errno.EPIPE,
                              'Checksum mismatch: %s (expected %s)' %
                              (self.blob_md5.hexdigest(), self.hash_md5))
            raise

    __next__ = next


def get_item_properties(item, fields, mixed_case_fields=None, formatters=None):
    """Return a tuple containing the item properties.

    :param item: a single item resource (e.g. Server, Project, etc)
    :param fields: tuple of strings with the desired field names
    :param mixed_case_fields: tuple of field names to preserve case
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    if mixed_case_fields is None:
        mixed_case_fields = []
    if formatters is None:
        formatters = {}

    row = []

    for field in fields:
        if field in mixed_case_fields:
            field_name = field.replace(' ', '_')
        else:
            field_name = field.lower().replace(' ', '_')
        data = item[field_name]
        if field in formatters:
            row.append(formatters[field](data))
        else:
            row.append(data)
    return tuple(row)


def make_size_human_readable(size):
    suffix = ['B', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB']
    base = 1024.0
    index = 0

    if size is None:
        size = 0
    while size >= base:
        index = index + 1
        size = size / base

    padded = '%.1f' % size
    stripped = padded.rstrip('0').rstrip('.')

    return '%s%s' % (stripped, suffix[index])


def save_blob(data, path):
    """Save a blob to the specified path.

    :param data: blob of the artifact
    :param path: path to save the blob to
    """
    if path is None:
        blob = getattr(sys.stdout, 'buffer',
                       sys.stdout)
    else:
        blob = open(path, 'wb')
    try:
        for chunk in data:
            blob.write(chunk)
    finally:
        if path is not None:
            blob.close()


def get_artifact_id(client, parsed_args):
    if parsed_args.id:
        return parsed_args.name
    try:
        return client.artifacts.get_by_name(
            parsed_args.name,
            version=parsed_args.artifact_version,
            type_name=parsed_args.type_name)['id']
    except exc.BadRequest as e:
        exit(msg=e.details)
