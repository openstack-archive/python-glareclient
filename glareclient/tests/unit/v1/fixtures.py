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
    '/artifacts/images?limit=20': {
        'GET': (
            # headers
            {},
            # response
            {'images': [
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
    '/artifacts/images?page_size=2': {
        'GET': (
            {},
            {'images': [
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
            ]},
        ),
    },
    '/artifacts/images?limit=2': {
        'GET': (
            {},
            {'images': [
                {
                    'name': 'art1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92d1',
                    'version': '0.0.0'
                },
                {
                    'name': 'art2',
                    'id': 'db721fb0-5b85-4738-9401-f161d541de5e',
                    'version': '0.0.0'
                }],
             'next': '/artifacts/images?'
                     'marker=e1090471-1d12-4935-a8d8-a9351266ece8&limit=2'},
        ),
    },
    '/artifacts/images?'
    'limit=2&marker=e1090471-1d12-4935-a8d8-a9351266ece8': {
        'GET': (
            {},
            {'images': [
                {
                    'name': 'art3',
                    'id': 'e1090471-1d12-4935-a8d8-a9351266ece8',
                    'version': '0.0.0'
                }
            ]},
        ),
    },
    '/artifacts/images?limit=20&sort=name%3Adesc': {
        'GET': (
            {},
            {'images': [
                {
                    'name': 'art2',
                    'id': 'e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                    'version': '0.0.0'
                },
                {
                    'name': 'art1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92d1',
                    'version': '0.0.0'
                }
            ],
                'next': '/artifacts/images?'
                'marker=3a4560a1-e585-443e-9b39-553b46ec92d1&limit=20'},
        ),
    },
    '/artifacts/images?limit=20&sort=name': {
        'GET': (
            {},
            {'images': [
                {
                    'name': 'art2',
                    'id': 'e4f027d2-bff3-4084-a2ba-f31cb5e3067f',
                    'version': '0.0.0'
                },
                {
                    'name': 'art1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92d1',
                    'version': '0.0.0'
                }
            ],
                'next': '/artifacts/images?'
                'marker=3a4560a1-e585-443e-9b39-553b46ec92d1&limit=20'},
        ),
    },
    '/artifacts/images?'
    'limit=20&marker=3a4560a1-e585-443e-9b39-553b46ec92d1': {
        'GET': (
            {},
            {'images': [
                {
                    'name': 'art1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92d1',
                    'version': '0.0.0'
                }
            ]}
        ),
    },
    '/artifacts/images': {
        'POST': (
            {},
            {'images': [
                {
                    'name': 'art_1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92a3',
                    'version': '0.0.0'
                }
            ]}
        ),
    },
    '/artifacts/images/3a4560a1-e585-443e-9b39-553b46ec92a3': {
        'DELETE': (
            {},
            {}
        ),
        'PATCH': (
            {},
            ''
        ),
        'GET': (
            {},
            {'images': [
                {
                    'name': 'art_1',
                    'id': '3a4560a1-e585-443e-9b39-553b46ec92a3',
                    'version': '0.0.0'
                }
            ]}
        )
    },
    '/artifacts/images/3a4560a1-e585-443e-9b39-553b46ec92a3/image': {
        'PUT': (
            {},
            ''
        ),
        'GET': (
            {'content-md5': '5cc4bebc-db27-11e1-a1eb-080027cbe205'},
            {}
        )
    },
    '/artifacts/images/3a4560a1-e585-443e-9b39-553b46ec92a2/image': {
        'PUT': (
            {},
            ''
        ),
        'GET': (
            {'content-md5': '5cc4bebc-db27-11e1-a1eb-080027cbe205'},
            {}
        )
    },
    '/schemas': {
        'GET': (
            {},
            {'schemas': {
                'images': {'name': 'images', 'version': '1.0'},
                'heat_environments': {'name': 'heat_environments',
                                      'version': '1.0'}}}
        )
    },
    '/schemas/images': {
        'GET': (
            {},
            {'schemas': {
                'images': {'name': 'images',
                           'version': '1.0',
                           'properties': {'foo': 'bar'}
                           }}}
        )
    }

}
