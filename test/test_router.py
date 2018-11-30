import json
import os
import sys

import pytest
import yaml

sys.path.insert(0, '..')
from falcon_openapi import OpenApiRouter  # isort:skip

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


class TestResponse():
    json = ''
    status = ''


class TestRouter():
    def test_file_path(self):
        router = OpenApiRouter()
        (resource, method_map, _, uri) = router.find('/foo')

        assert 'controllers.foo.Foo' in str(resource)

        assert len(method_map) == 3
        assert 'GET' in method_map
        assert 'POST' in method_map
        assert 'PUT' in method_map

        get_method = method_map['GET']
        post_method = method_map['POST']
        put_method = method_map['PUT']

        get_resp = TestResponse()
        post_resp = TestResponse()
        put_resp = TestResponse()

        get_method({}, get_resp)
        post_method({}, post_resp)
        put_method({}, put_resp)

        assert get_resp.status == '200 OK'
        assert post_resp.status == '200 OK'
        assert put_resp.status == "418 I'm a teapot"

        assert get_resp.json == {"method": "get"}
        assert post_resp.json == {"method": "post"}
        assert put_resp.json == {"method": "put"}

        assert uri == '/foo'

    def test_raw_json(self):
        spec = {
            'paths': {
                '/foo': {
                    'get': {
                        'operationId': 'controllers.foo.Foo.on_get'
                    }
                }
            }
        }

        router = OpenApiRouter(raw_json=json.dumps(spec))
        (resource, method_map, _, uri) = router.find('/foo')

        assert 'controllers.foo.Foo' in str(resource)
        assert len(method_map) == 1
        assert 'GET' in method_map

        get_method = method_map['GET']
        get_resp = TestResponse()
        get_method({}, get_resp)

        assert get_resp.status == '200 OK'
        assert get_resp.json == {"method": "get"}

        assert uri == '/foo'

    def test_raw_yaml(self):
        spec = {
            'paths': {
                '/foo': {
                    'get': {
                        'operationId': 'controllers.foo.Foo.on_get'
                    }
                }
            }
        }

        router = OpenApiRouter(raw_yaml=yaml.dump(spec))
        (resource, method_map, _, uri) = router.find('/foo')

        assert 'controllers.foo.Foo' in str(resource)

        assert len(method_map) == 1
        assert 'GET' in method_map

        get_method = method_map['GET']
        get_resp = TestResponse()
        get_method({}, get_resp)

        assert get_resp.status == '200 OK'
        assert get_resp.json == {"method": "get"}

        assert uri == '/foo'

    def test_base_path_v3(self):
        spec = {
            'servers': [{
                'url': 'http://localhost/v1'
            }],
            'paths': {
                '/foo': {
                    'get': {
                        'operationId': 'controllers.foo.Foo.on_get'
                    }
                }
            }
        }

        router = OpenApiRouter(raw_json=json.dumps(spec))
        (resource, method_map, _, uri) = router.find('/v1/foo')

        assert 'controllers.foo.Foo' in str(resource)
        assert len(method_map) == 1
        assert 'GET' in method_map

        get_method = method_map['GET']
        get_resp = TestResponse()
        get_method({}, get_resp)

        assert get_resp.status == '200 OK'
        assert get_resp.json == {"method": "get"}

        assert uri == '/v1/foo'

    def test_base_path_v2(self):
        spec = {
            'basePath': '/v1',
            'paths': {
                '/foo': {
                    'get': {
                        'operationId': 'controllers.foo.Foo.on_get'
                    }
                }
            }
        }

        router = OpenApiRouter(raw_json=json.dumps(spec))
        (resource, method_map, _, uri) = router.find('/v1/foo')

        assert 'controllers.foo.Foo' in str(resource)
        assert len(method_map) == 1
        assert 'GET' in method_map

        get_method = method_map['GET']
        get_resp = TestResponse()
        get_method({}, get_resp)

        assert get_resp.status == '200 OK'
        assert get_resp.json == {"method": "get"}

        assert uri == '/v1/foo'
