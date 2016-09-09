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

from osc_lib.command import command

from glareclient.common import utils as glare_utils
from glareclient.osc.v1 import TypeMapperAction


LOG = logging.getLogger(__name__)


class ListArtifacts(command.Lister):
    """List of artifacts"""

    def get_parser(self, prog_name):
        parser = super(ListArtifacts, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        )
        parser.add_argument(
            '--limit',
            default=20,
            metavar='<LIMIT>',
            help='Maximum number of artifacts to get.',
        )
        parser.add_argument(
            '--page-size',
            default=20,
            metavar='<SIZE>',
            help='Number of artifacts to request in each paginated request.',
        )
        parser.add_argument(
            '--filter',
            default=[],
            action='append',
            metavar='<KEY=VALUE>',
            help='Filtering artifact list by a user-defined property.',
        )
        parser.add_argument(
            '--sort',
            default='name:asc',
            metavar='<key>[:<direction>]',
            help='Comma-separated list of sort keys and directions in the '
                 'form of <key>[:<asc|desc>].',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        params = {'limit': parsed_args.limit,
                  'filters': [f.split('=', 1) for f in parsed_args.filter],
                  'sort': parsed_args.sort,
                  'page_size': parsed_args.page_size}

        data = client.artifacts.list(type_name=parsed_args.type_name,
                                     **params)

        columns = ('id', 'name', 'version', 'owner', 'visibility', 'status')
        column_headers = [c.capitalize() for c in columns]
        table = []
        for af in data:
            table.append(glare_utils.get_item_properties(af, columns))
        return (column_headers,
                table)


class ShowArtifact(command.ShowOne):
    """Show details artifact"""

    def get_parser(self, prog_name):
        parser = super(ShowArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.get(parsed_args.id,
                                    type_name=parsed_args.type_name)
        return self.dict2columns(data)


class CreateArtifact(command.ShowOne):
    """Create a new artifact"""

    def get_parser(self, prog_name):
        parser = super(CreateArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'name',
            default='',
            metavar='<NAME>',
            help='Name of the artifact.',
        ),
        parser.add_argument(
            '--artifact-version',
            default='0.0.0',
            metavar='<VERSION>',
            help='Version of the artifact.',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Artifact property.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))

        prop = {}
        for datum in parsed_args.property:
            key, value = datum.split('=', 1)
            prop[key] = value

        client = self.app.client_manager.artifact
        data = client.artifacts.create(parsed_args.name,
                                       type_name=parsed_args.type_name,
                                       version=parsed_args.artifact_version,
                                       **prop)
        return self.dict2columns(data)


class UpdateArtifact(command.ShowOne):
    """Update the properties of the artifact"""

    def get_parser(self, prog_name):
        parser = super(UpdateArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        parser.add_argument(
            '--name',
            metavar='<NAME>',
            help='Name of the artifact',
        ),
        parser.add_argument(
            '--remove-property',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Property that will be removed.'
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Update property values.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))

        remove_props = {}
        for datum in parsed_args.remove_property:
            key, value = datum.split('=', 1)
            remove_props[key] = value

        prop = {}
        for datum in parsed_args.property:
            key, value = datum.split('=', 1)
            prop[key] = value

        client = self.app.client_manager.artifact
        data = client.artifacts.update(parsed_args.id,
                                       type_name=parsed_args.type_name,
                                       remove_props=remove_props,
                                       **prop)
        return self.dict2columns(data)


class DeleteArtifact(command.ShowOne):
    """Delete the artifact"""

    def get_parser(self, prog_name):
        parser = super(DeleteArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.delete(parsed_args.id,
                                       type_name=parsed_args.type_name)
        return self.dict2columns(data)


class ActivateArtifact(command.ShowOne):
    """Activate the artifact"""

    def get_parser(self, prog_name):
        parser = super(ActivateArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.active(parsed_args.id,
                                       type_name=parsed_args.type_name)
        return self.dict2columns(data)


class DeactivateArtifact(command.ShowOne):
    """Deactivate the artifact"""

    def get_parser(self, prog_name):
        parser = super(DeactivateArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.deactivete(parsed_args.id,
                                           type_name=parsed_args.type_name)
        return self.dict2columns(data)


class ReactivateArtifact(command.ShowOne):
    """Reactivate the artifact"""

    def get_parser(self, prog_name):
        parser = super(ReactivateArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.reactivete(parsed_args.id,
                                           type_name=parsed_args.type_name)
        return self.dict2columns(data)


class PublishArtifact(command.ShowOne):
    """Publish  the artifact"""

    def get_parser(self, prog_name):
        parser = super(PublishArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'id',
            metavar='<ID>',
            help='ID of the artifact to update',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.publish(parsed_args.id,
                                        type_name=parsed_args.type_name)
        return self.dict2columns(data)
