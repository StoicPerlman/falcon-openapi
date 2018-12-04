import os
import sys
from wsgiref import simple_server

import falcon

module_dir = os.path.dirname(os.path.abspath(__file__)) + '/..'
sys.path.insert(0, module_dir)
from falcon_openapi import OpenApiRouter, OpenApiValidator  # isort:skip

# load from file
app = falcon.API(
    router=OpenApiRouter(),
    middleware=[OpenApiValidator()],
)

if __name__ == '__main__':
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()
