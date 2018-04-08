import falcon
import falcon_jsonify
from falcon_openapi import OpenApiRouter

app = falcon.API(
    middleware=[falcon_jsonify.Middleware()],
    router=OpenApiRouter()
)
