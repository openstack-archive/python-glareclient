# Copyright 2015 - StackStorm, Inc.
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

"""
Command-line interface to the Glare APIs
"""

import argparse
import logging
import sys

from cliff import app
from cliff import commandmanager
from osc_lib.command import command

from glareclient import client
from glareclient.common import utils
import glareclient.osc.v1.artifacts
import glareclient.osc.v1.blobs


class OpenStackHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog, indent_increment=2, max_help_position=32,
                 width=None):
        super(OpenStackHelpFormatter, self).__init__(
            prog,
            indent_increment,
            max_help_position,
            width
        )

    def start_section(self, heading):
        # Title-case the headings.
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


class HelpAction(argparse.Action):
    """Custom help action.

    Provide a custom action so the -h and --help options
    to the main app will print a list of the commands.
    The commands are determined by checking the CommandManager
    instance, passed in as the "default" value for the action.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        outputs = []
        max_len = 0
        app = self.default
        parser.print_help(app.stdout)
        app.stdout.write('\nCommands for API v1 :\n')

        for name, ep in sorted(app.command_manager):
            factory = ep.load()
            cmd = factory(self, None)
            one_liner = cmd.get_description().split('\n')[0]
            outputs.append((name, one_liner))
            max_len = max(len(name), max_len)

        for (name, one_liner) in outputs:
            app.stdout.write('  %s  %s\n' % (name.ljust(max_len), one_liner))

        sys.exit(0)


class BashCompletionCommand(command.Command):
    """Prints all of the commands and options for bash-completion."""

    def take_action(self, parsed_args):
        commands = set()
        options = set()

        for option, _action in self.app.parser._option_string_actions.items():
            options.add(option)

        for command_name, _cmd in self.app.command_manager:
            commands.add(command_name)

        print(' '.join(commands | options))


class GlareShell(app.App):

    def __init__(self):
        super(GlareShell, self).__init__(
            description=__doc__.strip(),
            version=glareclient.__version__,
            command_manager=commandmanager.CommandManager('glare.cli'),
        )
        self._set_shell_commands(self._get_commands())

    def configure_logging(self):
        log_lvl = logging.DEBUG if self.options.debug else logging.WARNING
        logging.basicConfig(
            format="%(levelname)s (%(module)s) %(message)s",
            level=log_lvl
        )
        logging.getLogger('iso8601').setLevel(logging.WARNING)

        if self.options.verbose_level <= 1:
            logging.getLogger('requests').setLevel(logging.WARNING)

    def build_option_parser(self, description, version,
                            argparse_kwargs=None):
        """Return an argparse option parser for this application.

        Subclasses may override this method to extend
        the parser with more global options.
        :param description: full description of the application
        :paramtype description: str
        :param version: version number for the application
        :paramtype version: str
        :param argparse_kwargs: extra keyword argument passed to the
                                ArgumentParser constructor
        :paramtype extra_kwargs: dict
        """
        argparse_kwargs = argparse_kwargs or {}

        parser = argparse.ArgumentParser(
            description=description,
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
            **argparse_kwargs
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s {0}'.format(version),
            help='Show program\'s version number and exit.'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='count',
            dest='verbose_level',
            default=self.DEFAULT_VERBOSE_LEVEL,
            help='Increase verbosity of output. Can be repeated.',
        )
        parser.add_argument(
            '--log-file',
            action='store',
            default=None,
            help='Specify a file to log output. Disabled by default.',
        )
        parser.add_argument(
            '-q', '--quiet',
            action='store_const',
            dest='verbose_level',
            const=0,
            help='Suppress output except warnings and errors.',
        )
        parser.add_argument(
            '-h', '--help',
            action=HelpAction,
            nargs=0,
            default=self,  # tricky
            help="Show this help message and exit.",
        )
        parser.add_argument(
            '--debug',
            default=False,
            action='store_true',
            help='Show tracebacks on errors.',
        )
        parser.add_argument(
            '--os-glare-url',
            action='store',
            dest='glare_url',
            default=utils.env('OS_GLARE_URL'),
            help='Glare API host (Env: OS_GLARE_URL)'
        )
        parser.add_argument(
            '--os-glare-version',
            action='store',
            dest='glare_version',
            default=utils.env('OS_GLARE_VERSION', default='v1'),
            help='Glare API version (default = v1) (Env: '
                 'OS_GLARE_VERSION)'
        )
        parser.add_argument(
            '--keycloak-auth-url',
            action='store',
            dest='keycloak_auth_url',
            default=utils.env('KEYCLOAK_AUTH_URL'),
            help='Keycloak auth url (Env: KEYCLOAK_AUTH_URL)')
        parser.add_argument(
            '--openid-client-id',
            action='store',
            dest='openid_client_id',
            default=utils.env('OPENID_CLIENT_ID') or 'admin-cli',
            help='Client ID (according to OpenID Connect)'
                 ' (Env: OPENID_CLIENT_ID)')
        parser.add_argument(
            '--auth-token',
            action='store',
            dest='auth_token',
            default=utils.env('AUTH_TOKEN'),
            help='Authentication token (Env: AUTH_TOKEN)')
        parser.add_argument(
            '--keycloak-realm-name',
            action='store',
            dest='keycloak_realm_name',
            default=utils.env('KEYCLOAK_REALM_NAME'),
            help='With keycloak glare auth type: Realm name to scope to'
                 ' (Env: KEYCLOAK_REALM_NAME)')
        parser.add_argument(
            '--keycloak-username',
            action='store',
            dest='keycloak_username',
            default=utils.env('KEYCLOAK_USERNAME'),
            help='Keycloak username (Env: KEYCLOAK_USERNAME)')
        parser.add_argument(
            '--keycloak-password',
            action='store',
            dest='keycloak_password',
            default=utils.env('KEYCLOAK_PASSWORD'),
            help='Keycloak user password (Env: KEYCLOAK_PASSWORD)')

        return parser

    def initialize_app(self, argv):
        self._clear_shell_commands()
        self._set_shell_commands(self._get_commands())

        do_help = ('help' in argv) or ('-h' in argv) or not argv

        # Set default for auth_url if not supplied. The default is not
        # set at the parser to support use cases where auth is not enabled.
        # An example use case would be a developer's environment.

        # bash-completion should not require authentification.
        if do_help or ('bash-completion' in argv):
            self.options.auth_url = None

        self.client = client.Client(
            endpoint=self.options.glare_url,
            auth_token=self.options.auth_token,
            keycloak_auth_url=self.options.keycloak_auth_url,
            openid_client_id=self.options.openid_client_id,
            keycloak_realm_name=self.options.keycloak_realm_name,
            keycloak_username=self.options.keycloak_username,
            keycloak_password=self.options.keycloak_password,
        )

        # Adding client_manager variable to make glare client work with
        # unified OpenStack client.
        ClientManager = type(
            'ClientManager',
            (object,),
            dict(artifact=self.client)
        )

        self.client_manager = ClientManager()

    def _set_shell_commands(self, cmds_dict):
        for k, v in cmds_dict.items():
            self.command_manager.add_command(k, v)

    def _clear_shell_commands(self):
        exclude_cmds = ['help', 'complete']

        cmds = self.command_manager.commands.copy()
        for k, v in cmds.items():
            if k not in exclude_cmds:
                self.command_manager.commands.pop(k)

    @staticmethod
    def _get_commands():
        return {
            'bash-completion': BashCompletionCommand,
            'list': glareclient.osc.v1.artifacts.ListArtifacts,
            'show': glareclient.osc.v1.artifacts.ShowArtifact,
            'create': glareclient.osc.v1.artifacts.CreateArtifact,
            'delete': glareclient.osc.v1.artifacts.DeleteArtifact,
            'update': glareclient.osc.v1.artifacts.UpdateArtifact,
            'activate': glareclient.osc.v1.artifacts.ActivateArtifact,
            'deactivate': glareclient.osc.v1.artifacts.DeactivateArtifact,
            'reactivate': glareclient.osc.v1.artifacts.ReactivateArtifact,
            'publish': glareclient.osc.v1.artifacts.PublishArtifact,
            'add-tag': glareclient.osc.v1.artifacts.AddTag,
            'remove-tag': glareclient.osc.v1.artifacts.RemoveTag,
            'type-list': glareclient.osc.v1.artifacts.TypeList,
            'schema': glareclient.osc.v1.artifacts.TypeSchema,
            'upload': glareclient.osc.v1.blobs.UploadBlob,
            'download': glareclient.osc.v1.blobs.DownloadBlob,
            'location': glareclient.osc.v1.blobs.AddLocation
        }


def main(argv=sys.argv[1:]):
    return GlareShell().run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
