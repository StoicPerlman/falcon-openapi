from wsgiref import simple_server

import falcon

from falcon_openapi import OpenApiSyncRouter

api = application = falcon.API(router=OpenApiSyncRouter(file_path="openapi-spec.yaml"))

if __name__ == "__main__":
    httpd = simple_server.make_server("127.0.0.1", 8000, api)
    httpd.serve_forever()
