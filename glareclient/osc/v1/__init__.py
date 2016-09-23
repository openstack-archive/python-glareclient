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

import argparse


class TypeMapperAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, self._type_name_mapper(values))

    @staticmethod
    def _type_name_mapper(type_name):
        if type_name in ['images', 'image']:
            return 'images'
        elif type_name in ['heat-templates', 'heat-template',
                           'heat_templates', 'heat_template']:
            return 'heat_templates'
        elif type_name in ['heat-environments', 'heat-environment',
                           'heat_environments', 'heat_environment']:
            return 'heat_environments'
        elif type_name in ['tosca-templates', 'tosca-template',
                           'tosca_templates', 'tosca_template']:
            return 'tosca_templates'
        elif type_name in ['murano-packages', 'murano-package',
                           'murano_packages', 'murano_package']:
            return 'murano_packages'
        return type_name
