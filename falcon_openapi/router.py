import json
from importlib.util import module_from_spec, spec_from_file_location
from inspect import stack
from logging import getLogger
from os.path import abspath, dirname
from pathlib import Path
from urllib.parse import urlparse

import yaml
from falcon.routing.compiled import CompiledRouter

from falcon_openapi.openapi import OpenApi


class OpenApiRouter(CompiledRouter):
    def __init__(self, file_path='', raw_json='', raw_yaml=''):
        super().__init__()

        self.openapi = OpenApi(file_path=file_path, raw_json=raw_json, raw_yaml=raw_yaml)

        for path, http_methods in self.openapi.spec['paths'].items():
            path = self.openapi.base_path + path
            openapi_map = {}

            for http_method, definition in http_methods.items():
                try:
                    (
                        dest_module,
                        dest_method,
                        dest_class,
                        dest_file,
                    ) = self.__get_destination_info(definition, http_method)
                except:
                    continue

                http_method = http_method.upper()
                class_name = f'{dest_module}.{dest_class}'

                if class_name not in openapi_map:
                    mod_spec = spec_from_file_location(dest_module, dest_file)
                    module = module_from_spec(mod_spec)
                    mod_spec.loader.exec_module(module)
                    Class = getattr(module, dest_class)()

                    openapi_map[class_name] = {}
                    openapi_map[class_name]['class'] = Class
                    openapi_map[class_name]['method_map'] = {}

                method_map = openapi_map[class_name]['method_map']
                Class = openapi_map[class_name]['class']
                Method = getattr(Class, dest_method)
                method_map[http_method] = Method

            for router_map in openapi_map.values():
                Class = router_map['class']
                method_map = router_map['method_map']
                self.add_route(path, method_map, Class)

    def __get_destination_info(self, definition, fallback):
        """Gets destination module, class, method, and filename from openapi 
        method definition. Looks for either operationId or x-falcon 
        properties. If both are defined operationId takes precedence.

        fallback should be the http method this definition is responsible for.
        This is used to route to on_get, on_post, etc if no method defined in
        x-falcon.
        
        Returns tuple (module, class, method, file_name)"""

        if 'operationId' in definition:
            operationId = definition['operationId']
            parts = operationId.split('.')
            op_method = parts.pop()
            op_class = parts.pop()
            op_module = '.'.join(parts)
            op_file = self.openapi.app_dir + '/'.join(parts) + '.py'

        elif 'x-falcon' in definition:
            falcon_router = definition['x-falcon']
            op_module = falcon_router['module']
            op_class = falcon_router['class']
            parts = op_module.split('.')
            op_file = self.openapi.app_dir + '/'.join(parts) + '.py'

            if 'method' not in falcon_router:
                op_method = 'on_' + fallback.lower()
            else:
                op_method = falcon_router['method']

        else:
            raise ValueError("No operationId or x-falcon found in definition")

        return (op_module, op_method, op_class, op_file)
