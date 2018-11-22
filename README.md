# Falcon OpenApi

Falcon OpenApi is a plugin for the [Falcon Web Framework](https://github.com/falconry/falcon).

### Install

```bash
pip3 install falcon-openapi
```

## OpenApi Router

Reads an openapi spec and provides automatic routing to Falcon resources. This is achieved by defining either an operationId or x-falcon property on an endpoint. This removes the need to define all endpoints in your main Falcon file. Instead just set the router to OpenApiRouter.

This router inherits from the default Falcon CompiledRouter class, so it supports all methods available to the default router.

Supports json files, yaml files, raw json strings, and raw yaml strings. If no params are specified the plugin will attempt to find `openapi-spec.yml` in the same directory.

```python
import falcon
import json
import yaml
from falcon_openapi import OpenApiRouter

spec = {
    'paths': {
        '/foo': {
            'get': {
                'operationId': 'controllers.foo.Foo.on_get'
            }
        }
    }
}

# load from file
app = falcon.API(
    router=OpenApiRouter(file_path='openapi-spec.yml')
)

# load from raw json
app = falcon.API(
    router=OpenApiRouter(raw_json=json.dumps(spec))
)

# load from raw yaml
app = falcon.API(
    router=OpenApiRouter(raw_yaml=yaml.dump(spec))
)
```

### operationId

The example below will route all `GET` `/foo` requests to `controllers.foo.Foo.on_get`. Where `controllers.foo` is the module name, `Foo` is the class name, and `on_get` is the method name. Every operationId in your spec should be unique (See [openapi operationId](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject)). All three parts of the operationId must be specified for the router to work.

```yaml
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Falcon Openapi Demo
paths:
  /foo:
    get:
      summary: Do foo things
      operationId: controllers.foo.Foo.on_get
```

I am unsure if operationId will make it into the final version. I may change this to only check for the x-falcon property. I plan on doing more research to determine if this an appropriate way to use the [operationId property](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject).

### x-falcon

The example below will route all `POST` `/foo` requests to the module `controllers.foo`, the class `Foo`, and the method `post_foo`. Note: the standard in Falcon is to use the naming scheme on_get, on_post, etc. This plugin will allow any method name to be used to handle the request. If no method name is defined in x-falcon, the plugin will attempt to route to the appropriate on_* method. Meaning in the example below, removing the `method: post_foo` would cause the router to attempt to find an `on_post` method in `Foo`.

```yaml
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Falcon Openapi Demo
paths:
  /foo:
    post:
      summary: Do foo things
      x-falcon:
        module: controllers.foo
        class: Foo
        method: post_foo
```
