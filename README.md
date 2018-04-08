# Falcon OpenApi

Falcon OpenApi is a set of plugins for the [Falcon Web Framework](https://github.com/falconry/falcon). This project is currently in alpha and still under development.

### Install

Not yet on pypi.

```bash
git clone https://github.com/StoicPerlman/falcon-openapi.git
cd falcon-openapi
python3 setup.py install
```

## OpenApi Router

Reads an openapi spec and provides automatic routing to Falcon resources. This is achieved by defining either an operationId or x-falcon-router property on an endpoint. This removes the need to define all endpoints in your main Falcon file. Instead just set the router to OpenApiRouter.

Currently supports json and yaml files. If no openapi file is specified the plugin will attempt to find `openapi-spec.yml` in the same directory.

```python
import falcon
from falcon_openapi import OpenApiRouter

app = falcon.API(
    router=OpenApiRouter(openapi='openapi-spec.yml')
)
```

This router inherits from the default Falcon CompiledRouter class, so it supports all methods available to the default router.

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

I am unsure if operationId will make it into the final version. I may change this to only check for the x-falcon-router property. I plan on doing more research to determine if this an appropriate way to use the [operationId property](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md#operationObject).

### x-falcon-router

The example below will route all `POST` `/foo` requests to the module `controllers.foo`, the class `Foo`, and the method `post_foo`. Note: the standard in Falcon is to use the naming scheme on_get, on_post, etc. This plugin will allow any method name to be used to handle the request. If no method name is defined in x-falcon-router, the plugin will attempt to route to the appropriate on_* method. Meaning in the example below, removing the `method: post_foo` would cause the router to attempt to find an `on_post` method in `Foo`.

```yaml
openapi: "3.0.0"
info:
  version: 1.0.0
  title: Falcon Openapi Demo
paths:
  /foo:
    post:
      summary: Do foo things
      x-falcon-router:
        module: controllers.foo
        class: Foo
        method: post_foo
```
## OpenApi Validator

This plugin is still a work in progress.
