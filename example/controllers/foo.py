import falcon

class Foo(object):
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.json = {
            "bar": "hello",
            "baz": "world"
        }

    def on_post(self, req, resp):
        """Handles POST requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.json = {
            "bar": "hello",
            "baz": "world"
        }
