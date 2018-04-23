import json
import yaml
import unittest

import sys
sys.path.insert(0, '..')
from falcon_openapi import OpenApiRouter

class TestResponse():
    def __init__(self):
        self.json = ''
        self.status = ''

class TestRouter(unittest.TestCase):

    def test_file_path(self):
        router = OpenApiRouter()
        (resource, method_map, _, uri) = router.find('/foo')
        self.assertTrue('controllers.foo.Foo' in str(resource))

        self.assertEqual(len(method_map), 3)
        self.assertTrue('GET' in method_map)
        self.assertTrue('POST' in method_map)
        self.assertTrue('PUT' in method_map)

        get_method = method_map['GET']
        post_method = method_map['POST']
        put_method = method_map['PUT']
        
        get_resp = TestResponse()
        post_resp = TestResponse()
        put_resp = TestResponse()

        get_method({}, get_resp)
        post_method({}, post_resp)
        put_method({}, put_resp)

        self.assertEqual(get_resp.status, '200 OK')
        self.assertEqual(post_resp.status, '200 OK')
        self.assertEqual(put_resp.status, "418 I'm a teapot")

        self.assertEqual(get_resp.json, {"method": "get"})
        self.assertEqual(post_resp.json, {"method": "post"})
        self.assertEqual(put_resp.json, {"method": "put"})

        self.assertEqual(uri, '/foo')
    
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
        self.assertTrue('controllers.foo.Foo' in str(resource))
        self.assertEqual(len(method_map), 1)
        self.assertTrue('GET' in method_map)

        get_method = method_map['GET']
        get_resp = TestResponse()
        get_method({}, get_resp)
        self.assertEqual(get_resp.status, '200 OK')
        self.assertEqual(get_resp.json, {"method": "get"})

        self.assertEqual(uri, '/foo')

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
        self.assertTrue('controllers.foo.Foo' in str(resource))
        
        self.assertEqual(len(method_map), 1)
        self.assertTrue('GET' in method_map)
        get_method = method_map['GET']
        get_resp = TestResponse()
        get_method({}, get_resp)
        self.assertEqual(get_resp.status, '200 OK')
        self.assertEqual(get_resp.json, {"method": "get"})

        self.assertEqual(uri, '/foo')

if __name__ == '__main__':
    unittest.main()