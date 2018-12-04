import json

from falcon import Request, Response

dummy = [
    {
        'id': 1,
        'name': 'foo'
    },
    {
        'id': 2,
        'name': 'bar'
    },
    {
        'id': 3,
        'name': 'baz'
    },
    {
        'id': 4,
        'name': 'spam'
    },
    {
        'id': 5,
        'name': 'ham'
    },
    {
        'id': 6,
        'name': 'eggs'
    },
]


class Demo():
    def get_all(self, req: Request, resp: Response):
        resp.body = json.dumps(dummy)

    def get_id(self, req: Request, resp: Response):
        resp.body = json.dumps(dummy[0])
