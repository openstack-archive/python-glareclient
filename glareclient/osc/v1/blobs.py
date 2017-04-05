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

import logging
import sys

from osc_lib.command import command

from glareclient.common import progressbar
from glareclient.common import utils
from glareclient import exc
from glareclient.osc.v1 import TypeMapperAction

LOG = logging.getLogger(__name__)


def _default_blob_property(type_name):
    if type_name == 'images':
        return 'image'
    elif type_name == 'murano_packages':
        return 'package'
    elif type_name in ('heat_templates', 'tosca_templates'):
        return 'template'
    elif type_name == 'heat_environments':
        return 'environment'
    utils.exit('Unknown artifact type. Please specify --blob-property.')


class UploadBlob(command.ShowOne):
    """Upload blob"""

    def get_parser(self, prog_name):
        parser = super(UploadBlob, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to upload.',
        ),
        parser.add_argument(
            '--artifact-version', '-V',
            metavar='<VERSION>',
            default='latest',
            help='Version of the artifact.',
        ),
        parser.add_argument(
            '--id', '-i',
            action='store_true',
            help='The specified id of the artifact.',
        ),
        parser.add_argument(
            '--file',
            metavar='<FILE_PATH>',
            help='Local file that contains data to be uploaded.',
        )
        parser.add_argument(
            '--blob-property', '-p',
            metavar='<BLOB_PROPERTY>',
            help='Name of the blob field.'
        )
        parser.add_argument(
            '--content-type', '-C',
            metavar='<CONTENT_TYPE>',
            default='application/octet-stream',
            help='Content-type of the blob.'
        )
        parser.add_argument(
            '--progress',
            action='store_true',
            help='Show download progress bar.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = utils.get_artifact_id(client, parsed_args)

        if not parsed_args.blob_property:
            parsed_args.blob_property = _default_blob_property(
                parsed_args.type_name)

        if parsed_args.file is None:
            if sys.stdin.isatty():
                raise exc.CommandError('Blob file should be specified or '
                                       'explicitly connected to stdin')
            blob = sys.stdin
        else:
            blob = open(parsed_args.file, 'rb')
        if parsed_args.progress:
            blob = progressbar.VerboseFileWrapper(blob)

        client.artifacts.upload_blob(af_id, parsed_args.blob_property, blob,
                                     content_type=parsed_args.content_type,
                                     type_name=parsed_args.type_name)

        data = client.artifacts.get(af_id, type_name=parsed_args.type_name)

        data_to_display = {'blob_property': parsed_args.blob_property}
        if '/' in parsed_args.blob_property:
            dict_name, __, key_name = parsed_args.blob_property.partition('/')
            data_to_display.update(data[dict_name][key_name])
        else:
            data_to_display.update(data[parsed_args.blob_property])
        return self.dict2columns(data_to_display)


class DownloadBlob(command.Command):
    """Download blob"""

    def get_parser(self, prog_name):
        parser = super(DownloadBlob, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to download.',
        ),
        parser.add_argument(
            '--artifact-version', '-V',
            metavar='<VERSION>',
            default='latest',
            help='Version of the artifact.',
        ),
        parser.add_argument(
            '--id', '-i',
            action='store_true',
            help='The specified id of the artifact.',
        ),
        parser.add_argument(
            '--progress',
            action='store_true',
            help='Show download progress bar.'
        )
        parser.add_argument(
            '--file',
            metavar='<FILE>',
            help='Local file to save downloaded blob to. '
                 'If this is not specified and there is no redirection '
                 'the blob will not be saved.'
        )
        parser.add_argument(
            '--blob-property', '-p',
            metavar='<BLOB_PROPERTY>',
            default=None,
            help='Name of the blob field.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        if not parsed_args.blob_property:
            parsed_args.blob_property = _default_blob_property(
                parsed_args.type_name)
        af_id = utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.download_blob(af_id,
                                              parsed_args.blob_property,
                                              type_name=parsed_args.type_name)
        if parsed_args.progress:
            data = progressbar.VerboseFileWrapper(data)
        if not (sys.stdout.isatty() and parsed_args.file is None):
            utils.save_blob(data, parsed_args.file)
        else:
            msg = ('No redirection or local file specified for downloaded '
                   'blob. Please specify a local file with --file to save '
                   'downloaded blob or redirect output to another source.')
            utils.exit(msg)


class AddLocation(command.ShowOne):
    """Add external location"""

    def get_parser(self, prog_name):
        parser = super(AddLocation, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to download.',
        ),
        parser.add_argument(
            '--artifact-version', '-V',
            metavar='<VERSION>',
            default='latest',
            help='Version of the artifact.',
        ),
        parser.add_argument(
            '--id', '-i',
            action='store_true',
            help='The specified id of the artifact.',
        ),
        parser.add_argument(
            '--url',
            metavar='<FILE_PATH>',
            help='External location that contains data to be uploaded.',
        )
        parser.add_argument(
            '--md5',
            metavar='<FILE_PATH>',
            help='Specify a checksum md5.',
        )
        parser.add_argument(
            '--sha1',
            metavar='<FILE_PATH>',
            help='Specify a checksum sha1.',
        )
        parser.add_argument(
            '--sha256',
            metavar='<FILE_PATH>',
            help='Specify a checksum sha256.',
        )
        parser.add_argument(
            '--blob-property', '-p',
            metavar='<BLOB_PROPERTY>',
            help='Name of the blob field.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = utils.get_artifact_id(client, parsed_args)

        if not parsed_args.blob_property:
            parsed_args.blob_property = _default_blob_property(
                parsed_args.type_name)

        data = {
            'url': parsed_args.url,
            'md5': parsed_args.md5,
            'sha1': parsed_args.sha1,
            'sha256': parsed_args.sha256
        }

        client.artifacts.add_external_location(
            af_id,
            parsed_args.blob_property,
            data,
            type_name=parsed_args.type_name)

        data = client.artifacts.get(af_id,
                                    type_name=parsed_args.type_name)

        data_to_display = {'blob_property': parsed_args.blob_property}
        if '/' in parsed_args.blob_property:
            dict_name, __, key_name = parsed_args.blob_property.partition('/')
            data_to_display.update(data[dict_name][key_name])
        else:
            data_to_display.update(data[parsed_args.blob_property])
        return self.dict2columns(data_to_display)
