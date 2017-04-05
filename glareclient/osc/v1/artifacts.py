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
from oslo_utils import strutils
from pprint import pformat
import six

from glareclient.common import utils as glare_utils
from glareclient.osc.v1 import TypeMapperAction

LOG = logging.getLogger(__name__)


def print_artifact(client, data, type_name):
        schema = \
            client.artifacts.get_type_schema(type_name=type_name)['properties']

        columns = ('field', 'value', 'glare type')
        column_headers = [c.capitalize() for c in columns]
        table = []

        for key, value in six.iteritems(data):
            if schema[key]['glareType'] == 'Blob':
                value = pformat(value)
            table.append((key, value, schema[key]['glareType']))

        return (column_headers,
                table)


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
            '--limit', '-l',
            default=20,
            metavar='<LIMIT>',
            type=int,
            help='Maximum number of artifacts to get.',
        )
        parser.add_argument(
            '--page-size', '-p',
            default=20,
            metavar='<SIZE>',
            type=int,
            help='Number of artifacts to request in each paginated request.',
        )
        parser.add_argument(
            '--filter', '-F',
            default=[],
            action='append',
            metavar='<KEY=VALUE>',
            help='Filtering artifact list by a user-defined property.',
        )
        parser.add_argument(
            '--sort', '-s',
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

        type_name = parsed_args.type_name

        data = client.artifacts.list(type_name=type_name, **params)

        columns = ['id', 'name', 'version', 'owner', 'visibility', 'status']
        if type_name == 'all':
            columns.insert(3, 'type_name')
        column_headers = [c.capitalize().replace("_", " ") for c in columns]
        table = []
        for af in data:
            table.append(glare_utils.get_item_properties(af, columns))
        return (column_headers,
                table)


class ShowArtifact(command.Lister):
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
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to show.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact

        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.get(af_id,
                                    type_name=parsed_args.type_name)

        return print_artifact(client, data, parsed_args.type_name)


class CreateArtifact(command.Lister):
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
            metavar='<NAME>',
            help='Name of the artifact.',
        ),
        parser.add_argument(
            '--artifact-version', '-V',
            default='0.0.0',
            metavar='<VERSION>',
            help='Version of the artifact.',
        )
        parser.add_argument(
            '--property', '-p',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Simple artifact property.'
        )
        parser.add_argument(
            '--list', '-l',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Artifact list property.'
        )
        parser.add_argument(
            '--dict', '-d',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Artifact dict property.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))

        prop = {}
        for datum in parsed_args.property:
            key, value = datum.split('=', 1)
            prop[key] = value

        for datum in parsed_args.list:
            key, value = datum.split('=', 1)
            value = strutils.split_by_commas(value)
            prop[key] = value

        for datum in parsed_args.dict:
            key, value = datum.split('=', 1)
            value = strutils.split_by_commas(value)
            prop[key] = {}
            for elem in value:
                k, v = elem.split(':', 1)
                prop[key][k] = v

        client = self.app.client_manager.artifact
        data = client.artifacts.create(parsed_args.name,
                                       type_name=parsed_args.type_name,
                                       version=parsed_args.artifact_version,
                                       **prop)
        return print_artifact(client, data, parsed_args.type_name)


class UpdateArtifact(command.Lister):
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
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to update.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        parser.add_argument(
            '--remove-property', '-r',
            metavar='<key>',
            action='append',
            default=[],
            help='Property that will be removed.'
        ),
        parser.add_argument(
            '--property', '-p',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Simple artifact property.'
        )
        parser.add_argument(
            '--list', '-l',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Artifact list property.'
        )
        parser.add_argument(
            '--dict', '-d',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Artifact dict property.'
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))

        prop = {}
        for datum in parsed_args.property:
            key, value = datum.split('=', 1)
            prop[key] = value

        for datum in parsed_args.list:
            key, value = datum.split('=', 1)
            value = strutils.split_by_commas(value)
            prop[key] = value

        for datum in parsed_args.dict:
            key, value = datum.split('=', 1)
            value = strutils.split_by_commas(value)
            prop[key] = {}
            for elem in value:
                k, v = elem.split(':', 1)
                prop[key][k] = v

        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.update(
            af_id, type_name=parsed_args.type_name,
            remove_props=parsed_args.remove_property, **prop)

        return print_artifact(client, data, parsed_args.type_name)


class DeleteArtifact(command.Command):
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
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to delete.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        client.artifacts.delete(af_id,
                                type_name=parsed_args.type_name)


class ActivateArtifact(command.Lister):
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
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to activate.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.activate(af_id,
                                         type_name=parsed_args.type_name)
        return print_artifact(client, data, parsed_args.type_name)


class DeactivateArtifact(command.Lister):
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
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to deactivate.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.deactivate(af_id,
                                           type_name=parsed_args.type_name)
        return print_artifact(client, data, parsed_args.type_name)


class ReactivateArtifact(command.Lister):
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
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to reactivate.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.reactivate(af_id,
                                           type_name=parsed_args.type_name)
        return print_artifact(client, data, parsed_args.type_name)


class PublishArtifact(command.Lister):
    """Publish the artifact"""

    def get_parser(self, prog_name):
        parser = super(PublishArtifact, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        ),
        parser.add_argument(
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to publish.',
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
            help='Flag indicates to use artifact id instead of its name.',
        ),
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.publish(af_id,
                                        type_name=parsed_args.type_name)
        return print_artifact(client, data, parsed_args.type_name)


class AddTag(command.Lister):
    """Add tag to artifact"""

    def get_parser(self, prog_name):
        parser = super(AddTag, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        )
        parser.add_argument(
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to publish.',
        )
        parser.add_argument(
            'tag',
            metavar='<TAG>',
            help='Value of the tag to add to the artifact.',
        )
        parser.add_argument(
            '--artifact-version', '-V',
            metavar='<VERSION>',
            default='latest',
            help='Version of the artifact.',
        )
        parser.add_argument(
            '--id', '-i',
            action='store_true',
            help='Flag indicates to use artifact id instead of its name.',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.add_tag(
            af_id, tag_value=parsed_args.tag, type_name=parsed_args.type_name)
        return print_artifact(client, data, parsed_args.type_name)


class RemoveTag(command.Lister):
    """Remove tag from the artifact"""

    def get_parser(self, prog_name):
        parser = super(RemoveTag, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        )
        parser.add_argument(
            'name',
            metavar='<NAME>',
            help='Name or id of the artifact to publish.',
        )
        parser.add_argument(
            'tag',
            metavar='<TAG>',
            help='Value of the tag to remove from the artifact.',
        )
        parser.add_argument(
            '--artifact-version', '-V',
            metavar='<VERSION>',
            default='latest',
            help='Version of the artifact.',
        )
        parser.add_argument(
            '--id', '-i',
            action='store_true',
            help='Flag indicates to use artifact id instead of its name.',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        af_id = glare_utils.get_artifact_id(client, parsed_args)
        data = client.artifacts.remove_tag(
            af_id, tag_value=parsed_args.tag, type_name=parsed_args.type_name)
        return print_artifact(client, data, parsed_args.type_name)


class TypeList(command.Lister):
    """List of type names"""

    def get_parser(self, prog_name):
        parser = super(TypeList, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.get_type_list()

        columns = ('name', 'version')
        column_headers = [c.capitalize() for c in columns]
        return (column_headers,
                data)


class TypeSchema(command.Lister):
    """Schema of type name."""

    def get_parser(self, prog_name):
        parser = super(TypeSchema, self).get_parser(prog_name)
        parser.add_argument(
            'type_name',
            metavar='<TYPE_NAME>',
            action=TypeMapperAction,
            help='Name of artifact type.',
        )
        return parser

    def take_action(self, parsed_args):
        LOG.debug('take_action({0})'.format(parsed_args))
        client = self.app.client_manager.artifact
        data = client.artifacts.get_type_schema(
            type_name=parsed_args.type_name)['properties']

        columns = ('name', 'glare_type', 'mutable', 'required',
                   'sortable', 'filters', 'available_values')
        column_headers = [c.capitalize() for c in columns]

        table = []

        for name, values in six.iteritems(data):
            row = (
                name,
                values.get('glareType'),
                values.get('mutable', False),
                values.get('required_on_activate', True),
                values.get('sortable', False),
                values.get('filter_ops'),
                values.get('enum', '')
            )
            table.append(row)

        return (column_headers,
                table)
