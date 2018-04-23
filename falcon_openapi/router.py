import json
import yaml
from inspect import stack
from os.path import abspath, dirname
from importlib.util import spec_from_file_location, module_from_spec
from falcon.routing.compiled import CompiledRouter

class OpenApiRouter(CompiledRouter):
    def __init__(self, file_path='openapi-spec.yml', raw_json='', raw_yaml=''):
        super().__init__()

        if raw_json != '':
            self.openapi = json.loads(raw_json)
        elif raw_yaml != '':
            self.openapi = yaml.load(raw_yaml)
        else:
            with open(file_path) as f:
                if file_path.endswith('json'):
                        self.openapi = json.load(f)
                else:
                    self.openapi = yaml.load(f)

        for path, http_methods in self.openapi['paths'].items():
            openapi_map = {}

            for http_method, definition in http_methods.items():
                try:
                    (dest_module,
                    dest_method, 
                    dest_class,
                    dest_file) = self.__get_destination_info(definition, http_method)
                except:
                    continue

                http_method = http_method.upper()
                class_name = dest_module + dest_class

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
    
    @staticmethod
    def __get_destination_info(definition, fallback):
        """Gets destination module, class, method, and filename from openapi 
        method definition. Looks for either operationId or x-falcon-router 
        properties. If both are defined operationId takes precedence.

        fallback should be the http method this definition is responsible for.
        This is used to route to on_get, on_post, etc if no method defined in
        x-falcon-router.
        
        Returns tuple (module, class, method, file_name)"""

        # gets the file and dir of whomever instantiated this object
        caller_file = abspath((stack()[2])[1])
        caller_dir = dirname(caller_file) + '/'

        if 'operationId' in definition:
            operationId = definition['operationId']
            parts = operationId.split('.')
            op_method = parts.pop()
            op_class = parts.pop()
            op_module = '.'.join(parts)
            op_file = caller_dir + '/'.join(parts) + '.py'
            return (op_module, op_method, op_class, op_file)
        elif 'x-falcon-router' in definition:
            falcon_router = definition['x-falcon-router']
            op_module = falcon_router['module']
            op_class = falcon_router['class']
            parts = op_module.split('.')
            op_file = caller_dir + '/'.join(parts) + '.py'

            if 'method' not in falcon_router:
                op_method = 'on_' + fallback.lower()
            else:
                op_method = falcon_router['method']

            return (op_module, op_method, op_class, op_file)
        else:
            raise ValueError("No operationId or x-falcon-router found in definition")
