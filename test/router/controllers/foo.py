import falcon

class Foo(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200
        resp.json = {"method": "get"}

    def on_post(self, req, resp):
        """Handles POST requests"""
        resp.status = falcon.HTTP_200
        resp.json = {"method": "post"}

    def do_a_put(self, req, resp):
        """Handles PUT requests"""
        resp.status = falcon.HTTP_418
        resp.json = {"method": "put"}
