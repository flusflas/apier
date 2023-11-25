from typing import Union

import pytest
from requests import Request, Response

from templates.python.base.internal.runtime_expr import decode_expression, RuntimeExpressionError
from test.templates.python.common import make_json_response

test_dict = {
    "prev_offset": 0,
    "next_offset": 2,
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
}

test_request = Request(url='https://runtime-expressions.test/my-url?foo=bar&limit=10&foo=abc',
                       headers={'Authorization': 'Bearer abc'},
                       method='GET').prepare()
test_response = make_json_response(200, test_dict, test_request)


@pytest.mark.parametrize("obj, expression, expected", [
    (test_dict, 'next_offset', 2),
    (test_dict, 'users', test_dict['users']),
    (test_dict, 'users.0', test_dict['users'][0]),
    (test_dict, 'users.1.name', 'Bob'),
    (test_response, 'next_offset', 2),
    (test_response, 'users', test_dict['users']),
    (test_response, 'users.0', test_dict['users'][0]),
    (test_response, 'users.1.name', 'Bob'),
    (test_response, '$url', 'https://runtime-expressions.test/my-url?foo=bar&limit=10&foo=abc'),
    (test_response, '$method', 'GET'),
    (test_response, '$request.query.limit', '10'),
    (test_response, '$request.query.foo', ['bar', 'abc']),
    # TODO: (test_response, '$request.path.*', ''),
    (test_response, '$request.header.Authorization', 'Bearer abc'),
    (test_response, '$request.body', ''),
    (test_response, '$statusCode', 200),
    (test_response, '$response.header.Content-Type', 'application/json'),
    (test_response, '$response.body', test_response.text),
    (test_response, '$response.body#users/1/name', 'Bob'),
    (test_response, '$response.body#next_offset', 2),
])
def test_runtime_expression(obj: Union[dict, Request, Response], expression: str, expected):
    result = decode_expression(expression, obj)
    assert result == expected


@pytest.mark.parametrize("obj, expression, expected_exception_type", [
    (test_request, 'foo.bar', ValueError),
    (test_response, 'foo.bar', KeyError),
    (test_dict, 'users.2.name', IndexError),
    (test_response, '$request.body#foo', TypeError),
    (test_response, '$my_request.body', RuntimeExpressionError),
    (test_response, '$request.query.not_found', RuntimeExpressionError),
])
def test_runtime_expression_errors(obj: Union[dict, Request, Response],
                                   expression: str, expected_exception_type):
    with pytest.raises(RuntimeExpressionError) as e:
        decode_expression(expression, obj)

    if expected_exception_type != RuntimeExpressionError:
        assert isinstance(e.value.caused_by, expected_exception_type)
    else:
        assert e.value.caused_by is None
