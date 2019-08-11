from look.model.model import model1


class controller1(object):
    def on_get(self, req, resp):
        resp.body = "test"
