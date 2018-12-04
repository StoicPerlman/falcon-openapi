import logging
import re
from copy import deepcopy
from decimal import Decimal
from typing import Dict

from falcon import Request, Response

from falcon_openapi.openapi import OpenApi

log = logging.getLogger(__file__)

INT32_MIN = -2147483647
INT32_MAX = 2147483647
INT64_MIN = -9223372036854775807
INT64_MAX = 9223372036854775807


class OpenApiValidator():
    def __init__(self, **kwargs):
        self.openapi = OpenApi(**kwargs)

        self.spec = {}

        # convert array of parameters to dict for faster lookup in process_* methods
        for uri, methods in self.openapi.spec['paths'].items():

            if uri not in self.spec:
                self.spec[uri] = {}

            for method, definition in methods.items():

                if method not in self.spec[uri]:
                    self.spec[uri][method] = {}

                for param in definition.get('parameters', {}):
                    param = deepcopy(param)
                    name = param.pop('name')

                    if 'schema' in param and 'pattern' in param['schema']:
                        pattern = param['schema']['pattern']
                        param['schema']['pattern'] = re.compile(pattern)

                    if 'request' not in self.spec[uri][method]:
                        self.spec[uri][method]['request'] = {}

                    self.spec[uri][method]['request'][name] = param

    def process_request(self, req: Request, resp: Response):
        pass

    def process_resource(self, req: Request, resp: Response, resource, params: Dict):
        method = req.method.lower()
        params = req.params
        uri_template = req.uri_template

        definitions = self.spec.get(uri_template, {})
        methods = definitions.get(method, {})
        spec_defs = methods.get('request', None)

        if not spec_defs:
            return

        for spec_param, spec_def in spec_defs.items():
            param = params.get(spec_param, None)
            required = is_required(spec_def)

            if not param and required:
                raise Exception('Param not passed')  # TODO: make exeption classes
            elif not param:
                continue

            validate_param(param, spec_def=spec_def)

    def process_response(self, req: Request, resp: Response, resource, req_succeeded: bool):
        pass


def validate_param(param, spec_def: Dict = None, schema: Dict = None):

    param_type = schema.get('type', None)

    if spec_def:
        schema = spec_def.get('schema', {})
    elif not schema:
        raise Exception('schema or spec_def needed')

    if param_type == 'string':
        validate_string(param, schema)
    elif param_type in ['integer', 'number']:
        param = validate_number(param, schema)
    elif param_type == 'boolean':
        validate_boolean(param)
    elif param_type == 'array':
        param = validate_array(param, schema)
    elif param_type == 'object':
        param = validate_object(param, schema)
    else:
        raise Exception('unknown type')

    return param


def is_required(spec_def: Dict) -> bool:
    return 'required' in spec_def and spec_def['required']


def validate_string(param, schema: Dict):

    if not isinstance(param, str):
        raise Exception('Not a str')

    if 'minLength' in schema and len(param) < schema['minLength']:
        raise Exception('too short')

    if 'maxLength' in schema and len(param) > schema['maxLength']:
        raise Exception('too long')

    if 'pattern' in schema and not schema['pattern'].search(param):
        raise Exception('does not match regex')

    return validate_enum(param, schema)


def validate_number(param, schema: Dict):
    val_type = schema.get('type', None)
    val_format = schema.get('format', None)
    p_type = type(param)

    if p_type is float and val_type != 'integer':
        param = validate_float(param, schema)
    elif p_type is int and val_format in ['float', 'double']:
        param = validate_float(param, schema, force_convert=True)
    elif p_type is int:
        validate_int(param, schema)
    elif p_type is float and val_type == 'integer':
        raise Exception('not an integer')
    else:
        raise Exception('Not a number')

    return validate_enum(param, schema)


def validate_int(param, schema: Dict):
    """Does not check if is instance of int. Call validate_number directly"""

    if 'format' in schema:
        if 'minimum' not in schema and schema['format'] == 'int32':
            schema['minimum'] = INT32_MIN

        if 'maximum' not in schema and schema['format'] == 'int32':
            schema['maximum'] = INT32_MAX

        if 'minimum' not in schema and schema['format'] == 'int64':
            schema['minimum'] = INT64_MIN

        if 'maximum' not in schema and schema['format'] == 'int64':
            schema['maximum'] = INT64_MAX

    return validate_min_max_mult(param, schema)


def validate_float(param, schema: Dict, force_convert: bool = False):
    """Does not check if is instance of float. Call validate_number directly"""

    if 'format' in schema and schema['format'] == 'double':
        param = Decimal(param)
    elif force_convert:
        param = float(param)

    return validate_min_max_mult(param, schema)


def validate_min_max_mult(param, schema: Dict):
    exclusive_min = schema.get('exclusiveMinimum', False)
    exclusive_max = schema.get('exclusiveMaximum', False)

    if exclusive_max and 'maximum' in schema and param >= schema['maximum']:
        raise Exception('too big')
    elif 'maximum' in schema and param > schema['maximum']:
        raise Exception('too big')

    if exclusive_min and 'minimum' in schema and param <= schema['minimum']:
        raise Exception('too small')
    elif 'minimum' in schema and param < schema['minimum']:
        raise Exception('too small')

    if 'multipleOf' in schema and param % schema['multipleOf'] != 0:
        raise Exception('not multipleOf')

    return param


def validate_boolean(param):
    if not isinstance(param, bool):
        raise Exception('not a bool')
    return param


def validate_enum(param, schema: Dict):
    if 'enum' in schema and param not in schema['enum']:
        raise Exception('param not in enum')
    return param


def validate_array(param, schema: Dict):
    if not isinstance(param, list):
        raise Exception('not a list')

    itemsInSchema = 'items' in schema

    for i, p in enumerate(param):
        if itemsInSchema:
            param[i] = validate_param(p, schema=schema['items'])

    return param


def validate_object(param, schema: Dict):
    if not isinstance(param, dict):
        raise Exception('not an object')

    propertiesInSchema = 'properties' in schema
    additionalProperties = schema.get('additionalProperties', False)
    strictAdditionalProperties = isinstance(additionalProperties, dict)

    for p, value in param.items():
        if propertiesInSchema and p in schema['properties']:
            param[p] = validate_param(value, schema=schema['properties'][p])
        elif strictAdditionalProperties:
            param[p] = validate_param(value, schema=additionalProperties)
        elif not additionalProperties:
            raise Exception('unknown property')

    return param
