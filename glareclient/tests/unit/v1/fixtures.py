# Copyright 2016 OpenStack Foundation
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

data_fixtures = {
    '/artifacts/sample_artifact?limit=20': {
        'GET': (
            # headers
            {},
            # response
            {'sample_artifact': [
                {
                    'name': 'art1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92d1',
                    'version': '0.0.0'
                },
                {
                    'name': 'art2',
                    'id': 'db721fb0-5b85-4738-9401-f161d541de5e',
                    'version': '0.0.0'
                },
                {
                    'name': 'art3',
                    'id': 'e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                    'version': '0.0.0'
                },
            ]},
        ),
    },
    '/artifacts/sample_artifact&limit=2': {
        'GET': (
            {},
            {'sample_artifact': [
                {
                    'name': 'art1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92d1',
                    'version': '0.0.0'
                },
                {
                    'name': 'art2',
                    'id': 'e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                    'version': '0.0.0'
                }],
             'next': '/artifacts/sample_artifact?'
                     'marker=e1090471-1d12-4935-a8d8-a9351266ece8&limit=2'},
        ),
    },
}
