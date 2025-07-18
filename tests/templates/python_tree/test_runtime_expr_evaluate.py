from typing import Union

import pytest
from requests import Request, Response

from apier.templates.python_tree.base.internal.runtime_expr import evaluate, RuntimeExpressionError
from .common import make_response

test_dict = {
    "prev_offset": 0,
    "next_offset": 2,
    "users": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
}

test_request = Request(url='https://api.test/companies/ibm/department/17/users?foo=bar&limit=10&foo=abc',
                       headers={
                           'Authorization': 'Bearer abc',
                           'X-Number': '7.35',
                       },
                       method='GET').prepare()
test_response = make_response(200, test_dict, test_request)


@pytest.mark.parametrize("resp, expression, expected", [
    (test_dict, 'next_offset', 2),
    (test_dict, 'users', test_dict['users']),
    (test_dict, 'users.0', test_dict['users'][0]),
    (test_dict, 'users.1.name', 'Bob'),
    (test_response, 'next_offset', 2),
    (test_response, 'users', test_dict['users']),
    (test_response, 'users.0', test_dict['users'][0]),
    (test_response, 'users.1.name', 'Bob'),
    (test_response, '$url', 'https://api.test/companies/ibm/department/17/users?foo=bar&limit=10&foo=abc'),
    (test_response, '$method', 'GET'),
    (test_response, '$request.query.limit', '10'),
    (test_response, '$request.query.foo', ['bar', 'abc']),
    (test_response, '$request.header.Authorization', 'Bearer abc'),
    (test_response, '$request.body', ''),
    (test_response, '$statusCode', 200),
    (test_response, '$response.header.Content-Type', 'application/json'),
    (test_response, '$response.body', test_response.text),
    (test_response, '$response.body#/users/1/name', 'Bob'),
    (test_response, '$response.body#/next_offset', 2),
    (test_response, 'foo{$response.body#/next_offset}bar', 'foo2bar'),
    (test_response, 'Alice: {$response.body#/users/0/id}, Bob: {$response.body#/users/1/id}', 'Alice: 1, Bob: 2'),
])
def test_evaluate(resp: Union[dict, Request, Response], expression: str, expected):
    result = evaluate(resp, expression)
    assert result == expected


@pytest.mark.parametrize("resp, expression, expected", [
    (test_response, '$request.path.company-id', 'ibm'),
    (test_response, '$request.path.department_num', 17),
])
def test_evaluate_with_path_values(resp: Union[dict, Request, Response], expression: str, expected):
    path_values = {
        'company-id': 'ibm',
        'department_num': 17
    }
    result = evaluate(resp, expression, path_values=path_values)
    assert result == expected


@pytest.mark.parametrize("resp, expression, expected", [
    (test_response, '$request.query.limit', 10),
    (test_response, '$request.header.x-number', 7.35),
])
def test_evaluate_with_type_casting(resp: Union[dict, Request, Response], expression: str, expected):
    query_param_types = {'limit': int}
    header_param_types = {'X-Number': float}
    result = evaluate(resp, expression,
                      query_param_types=query_param_types,
                      header_param_types=header_param_types)
    assert result == expected
    assert isinstance(result, type(expected))


@pytest.mark.parametrize("resp, expression, expected_exception_type", [
    (test_request, 'foo.bar', ValueError),
    (test_response, 'foo.bar', KeyError),
    (test_dict, 'users.2.name', IndexError),
    (test_response, '$request.body#/foo', TypeError),
    (test_response, '$my_request.body', RuntimeExpressionError),
    (test_response, '$request.query.not_found', RuntimeExpressionError),
    (test_response, '$request.path.foo', RuntimeExpressionError),
])
def test_evaluate_with_errors(resp: Union[dict, Request, Response],
                              expression: str, expected_exception_type):
    with pytest.raises(RuntimeExpressionError) as e:
        evaluate(resp, expression)

    if expected_exception_type != RuntimeExpressionError:
        assert isinstance(e.value.caused_by, expected_exception_type)
    else:
        assert e.value.caused_by is None
