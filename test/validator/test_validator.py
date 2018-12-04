
import os
import re
import sys
from copy import deepcopy
from decimal import Decimal
from typing import Dict
from unittest import mock
from unittest.mock import MagicMock

import pytest

module_dir = os.path.dirname(os.path.abspath(__file__)) + '/../..'
sys.path.insert(0, module_dir)
from falcon_openapi import OpenApiValidator  # isort:skip
from falcon_openapi import validator  # isort:skip


class TestValidator():
    def init_with_mock(self, mockOpenApi: MagicMock, spec: Dict) -> OpenApiValidator:
        mock_instance = mockOpenApi.return_value
        mock_instance.spec = test_spec1
        validator = OpenApiValidator()
        assert isinstance(validator.openapi, MagicMock)
        return validator

    @mock.patch('falcon_openapi.validator.OpenApi')
    def test_init(self, mockOpenApi: MagicMock):

        validator = self.init_with_mock(mockOpenApi, test_spec1)

        # parameters array remapped to dict
        params = validator.spec['/foo']['get']['request']
        assert 'test' in params

        # pattern string replaced with Pattern
        pattern = params['test']['schema']['pattern']
        assert isinstance(pattern, re.Pattern)
        assert pattern.search('kjahsd') is not None
        assert pattern.search('kjahsd123') is None

    def test_is_required(self):
        spec_def = {}
        assert validator.is_required(spec_def) == False

        spec_def = {'required': False}
        assert validator.is_required(spec_def) == False

        spec_def = {'required': True}
        assert validator.is_required(spec_def) == True

    def test_validate_string(self):
        schema = {}
        assert validator.validate_string('FooBar', schema)

        schema = {'minLength': 3}
        assert validator.validate_string('FooBar', schema)

        schema = {'maxLength': 10}
        assert validator.validate_string('FooBar', schema)

        schema = {'pattern': re.compile("^[a-zA-Z]+$")}
        assert validator.validate_string('FooBar', schema)

        with pytest.raises(Exception):
            assert validator.validate_string(1, schema)

        with pytest.raises(Exception):
            schema = {'minLength': 10}
            assert validator.validate_string('FooBar', schema)

        with pytest.raises(Exception):
            schema = {'maxLength': 3}
            assert validator.validate_string('FooBar', schema)

        with pytest.raises(Exception):
            schema = {'pattern': re.compile("^[a-z]+$")}
            assert validator.validate_string('FooBar', schema)

    def test_validate_number(self):
        schema = {}
        assert isinstance(validator.validate_number(10, schema), int)
        assert isinstance(validator.validate_number(10.0, schema), float)

        schema = {'format': 'float'}
        assert isinstance(validator.validate_number(10, schema), float)
        assert isinstance(validator.validate_number(10.0, schema), float)

        schema = {'format': 'double'}
        assert isinstance(validator.validate_number(10, schema), Decimal)
        assert isinstance(validator.validate_number(10.0, schema), Decimal)

        with pytest.raises(Exception):
            validator.validate_number('hello', schema)

    def test_validate_int(self):
        schema = {'format': 'int32'}
        assert validator.validate_int(10, schema)

        schema = {'format': 'int64'}
        assert validator.validate_int(validator.INT32_MAX + 10, schema)

        with pytest.raises(Exception):
            schema = {'format': 'int32'}
            validator.validate_int(validator.INT32_MIN - 10, schema)

        with pytest.raises(Exception):
            schema = {'format': 'int32'}
            validator.validate_int(validator.INT32_MAX + 10, schema)

        with pytest.raises(Exception):
            schema = {'format': 'int64'}
            validator.validate_int(validator.INT64_MIN - 10, schema)

        with pytest.raises(Exception):
            schema = {'format': 'int64'}
            validator.validate_int(validator.INT64_MAX + 10, schema)

    def test_validate_float(self):
        schema = {}
        assert isinstance(validator.validate_float(1.0, schema), float)

        schema = {}
        assert isinstance(validator.validate_float(1, schema, force_convert=True), float)

        schema = {'format': 'double'}
        assert isinstance(validator.validate_float(1.0, schema), Decimal)

        schema = {'format': 'double'}
        assert isinstance(validator.validate_float(1, schema, force_convert=True), Decimal)

    def test_validate_min_max_mult(self):
        schema = {'multipleOf': 5}
        assert validator.validate_int(10, schema)

        schema = {'minimum': 3}
        assert validator.validate_int(5, schema)

        schema = {'minimum': 3, 'exclusiveMinimum': True}
        assert validator.validate_int(4, schema)

        schema = {'maximux': 5}
        assert validator.validate_int(3, schema)

        schema = {'maximux': 5, 'exclusiveMaximux': True}
        assert validator.validate_int(4, schema)

        schema = {'format': 'int32'}
        assert validator.validate_int(4, schema)

        with pytest.raises(Exception):
            schema = {'multipleOf': 5}
            validator.validate_int(8, schema)

        with pytest.raises(Exception):
            schema = {'minimum': 10}
            validator.validate_int(5, schema)

        with pytest.raises(Exception):
            schema = {'minimum': 4, 'exclusiveMinimum': True}
            validator.validate_int(4, schema)

        with pytest.raises(Exception):
            schema = {'maximum': 5}
            validator.validate_int(10, schema)

        with pytest.raises(Exception):
            schema = {'maximum': 4, 'exclusiveMaximum': True}
            validator.validate_int(4, schema)

    def test_validate_boolean(self):
        assert validator.validate_boolean(True) == True
        assert validator.validate_boolean(False) == False

        with pytest.raises(Exception):
            validator.validate_boolean(None)

        with pytest.raises(Exception):
            validator.validate_boolean(0)

        with pytest.raises(Exception):
            validator.validate_boolean('')

    def test_validate_enum(self):
        schema = {'enum': [1, 2]}
        assert validator.validate_enum(1, schema)

        schema = {'enum': [1.0, 2.0]}
        assert validator.validate_enum(1.0, schema)

        schema = {'enum': [1.0, 2.0]}
        assert validator.validate_enum(Decimal(1), schema)

        schema = {'enum': ['foo', 'bar']}
        assert validator.validate_enum('foo', schema)

        with pytest.raises(Exception):
            schema = {'enum': [1, 2]}
            assert validator.validate_enum(3, schema)

        with pytest.raises(Exception):
            schema = {'enum': [1.0, 2.0]}
            assert validator.validate_enum(3.0, schema)

        with pytest.raises(Exception):
            schema = {'enum': [1.0, 2.0]}
            assert validator.validate_enum(Decimal(3), schema)

        with pytest.raises(Exception):
            schema = {'enum': ['foo', 'bar']}
            assert validator.validate_enum('baz', schema)

    def test_validate_array(self):
        schema = {'type': 'array', 'items': {'type': 'string'}}
        assert validator.validate_array(['foo', 'bar'], schema)

        schema = {'type': 'array', 'items': {'type': 'integer'}}
        assert validator.validate_array([1, 2], schema)

        schema = {'type': 'array', 'items': {'type': 'number'}}
        assert validator.validate_array([1, 2], schema)

        schema = {'type': 'array', 'items': {'type': 'number'}}
        assert validator.validate_array([1.0, 2.1], schema)

        schema = {'type': 'array', 'items': {'type': 'boolean'}}
        assert validator.validate_array([True, False], schema)

        schema = {'type': 'array', 'items': {'type': 'integer', 'enum': [1, 2]}}
        assert validator.validate_array([1, 2], schema)

        schema = {'type': 'array', 'items': a_big_object_schema}
        assert validator.validate_array([good_object_param, good_object_param], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': {'type': 'string'}}
            assert validator.validate_array(['foo', 1], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': {'type': 'integer'}}
            assert validator.validate_array([1, 2.1], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': {'type': 'number'}}
            assert validator.validate_array([1, 'bar'], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': {'type': 'number'}}
            assert validator.validate_array([1.0, True], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': {'type': 'boolean'}}
            assert validator.validate_array([True, 'bar'], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': {'type': 'integer', 'enum': [1, 2]}}
            assert validator.validate_array([1, 5], schema)

        with pytest.raises(Exception):
            schema = {'type': 'array', 'items': a_big_object_schema}
            assert validator.validate_array([bad_object_param, bad_object_param], schema)

    def test_validate_object(self):
        assert validator.validate_object(good_object_param, a_big_object_schema)

        schema = deepcopy(a_big_object_schema)
        param = good_object_param
        param['unknown_property'] = 1
        schema['additionalProperties'] = True # anything allowed
        assert validator.validate_object(param, schema)

        schema = deepcopy(a_big_object_schema)
        param = good_object_param
        param['unknown_property'] = 'foo'
        schema['additionalProperties'] = {'type': 'string'}
        assert validator.validate_object(param, schema)

        schema = deepcopy(a_big_object_schema)
        param = good_object_param
        param['unknown_property'] = 1
        schema['additionalProperties'] = {'type': 'integer'}
        assert validator.validate_object(param, schema)

        with pytest.raises(Exception):
            assert validator.validate_object(bad_object_param, a_big_object_schema)

        with pytest.raises(Exception):
            schema = deepcopy(a_big_object_schema)
            schema['additionalProperties'] = False # defaults to false but this makes test clear
            param = good_object_param
            param['unknown_property'] = 1
            assert validator.validate_object(param, schema)

        with pytest.raises(Exception):
            schema = deepcopy(a_big_object_schema)
            param = good_object_param
            param['unknown_property'] = 1
            schema['additionalProperties'] = {'type': 'string'}
            assert validator.validate_object(param, schema)

        with pytest.raises(Exception):
            schema = deepcopy(a_big_object_schema)
            param = good_object_param
            param['unknown_property'] = 'foo'
            schema['additionalProperties'] = {'type': 'integer'}
            assert validator.validate_object(param, schema)


test_spec1 = {
    'paths': {
        '/foo': {
            'get': {
                'parameters': [{
                    'name': 'test',
                    'type': 'string',
                    'schema': {
                        'pattern': "^[a-z]+$"
                    }
                }]
            }
        }
    }
}

a_big_object_schema = {
    'type': 'object',
    'properties': {
        'id': {
            'type': 'integer'
        },
        'name': {
            'type': 'string'
        },
        'active': {
            'type': 'boolean'
        },
        'percent': {
            'type': 'number',
            'schema': {
                'format': 'float'
            }
        },
        'another_object': {
            'type': 'object',
            'properties': {
                'id': {
                    'type': 'integer'
                },
                'name': {
                    'type': 'string'
                },
                'active': {
                    'type': 'boolean'
                },
                'percent': {
                    'type': 'number',
                    'schema': {
                        'format': 'float'
                    }
                }
            }
        }
    }
}

good_object_param = {
    'id': 1,
    'name': 'foo',
    'active': True,
    'percent': 0.42,
}
good_object_param['another_object'] = deepcopy(good_object_param)

bad_object_param = {
    'id': 'foo',
    'name': 1,
    'active': 'yes',
    'percent': '0.42',
    'another_object': 'bar'
}
