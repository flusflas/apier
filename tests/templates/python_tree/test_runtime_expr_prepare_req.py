import copy
import json

import pytest
from requests import Request, Response, PreparedRequest

from apier.templates.python_tree.base.internal.runtime_expr import (
    RuntimeExpressionError,
    prepare_request,
)

test_payload = {
    "prev_offset": 0,
    "next_offset": 2,
    "users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
}

test_request = Request(
    url="https://api.test/companies/ibm/department/17/users?foo=bar&limit=10&foo=abc",
    headers={
        "Authorization": "Bearer abc",
        "X-Number": "7.35",
    },
    method="GET",
    json=test_payload,
)


def test_prepare_request_set_payload_dotted():
    # Set entire payload
    req = copy.deepcopy(test_request)
    req.json = None
    result = prepare_request(req, "", {"foo": 123})
    assert isinstance(result, PreparedRequest)
    assert result.body == json.dumps({"foo": 123}).encode("utf-8")

    # Set attribute in empty payload
    req = copy.deepcopy(test_request)
    req.json = None
    result = prepare_request(req, "id", 123)
    assert isinstance(result, PreparedRequest)
    assert result.body == json.dumps({"id": 123}).encode("utf-8")

    # Override array value
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "users.1", 123)
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["users"][1] = 123
    assert result.body == json.dumps(expected_body).encode("utf-8")

    # Insert value in array
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "users.-", {"id": 3, "name": "Charlie"})
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["users"].append({"id": 3, "name": "Charlie"})
    assert result.body == json.dumps(expected_body).encode("utf-8")

    # Insert nested dict in array
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "users.-.foo.bar", 123)
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["users"].append({"foo": {"bar": 123}})
    assert result.body == json.dumps(expected_body).encode("utf-8")

    # Replace value
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "users", [1, 2, 3])
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["users"] = [1, 2, 3]
    assert result.body == json.dumps(expected_body).encode("utf-8")

    # Convert non-dict value into a dict
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "next_offset.value", 2)
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["next_offset"] = {"value": 2}
    assert result.body == json.dumps(expected_body).encode("utf-8")

    # Override value inside list
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "users.1.name", "Bobby")
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["users"][1]["name"] = "Bobby"
    assert result.body == json.dumps(expected_body).encode("utf-8")


def test_prepare_request_set_payload():
    # Set entire payload
    req = copy.deepcopy(test_request)
    req.json = None
    result = prepare_request(req, "$request.body", {"foo": 123})
    assert isinstance(result, PreparedRequest)
    assert result.body == json.dumps({"foo": 123}).encode("utf-8")

    # Set attribute in empty payload
    req = copy.deepcopy(test_request)
    req.json = None
    result = prepare_request(req, "$request.body#/id", 123)
    assert isinstance(result, PreparedRequest)
    assert result.body == json.dumps({"id": 123}).encode("utf-8")

    # Override array value
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "$request.body#/users/1", 123)
    assert isinstance(result, PreparedRequest)
    expected_body = copy.deepcopy(test_payload)
    expected_body["users"][1] = 123
    assert result.body == json.dumps(expected_body).encode("utf-8")


def test_prepare_query_params():
    # Replace limit value
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "$request.query.limit", 20)
    assert isinstance(result, PreparedRequest)
    assert (
        result.url
        == "https://api.test/companies/ibm/department/17/users?foo=bar&foo=abc&limit=20"
    )

    # Set new query param
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "$request.query.value", "123")
    assert isinstance(result, PreparedRequest)
    assert (
        result.url
        == "https://api.test/companies/ibm/department/17/users?foo=bar&foo=abc&limit=10&value=123"
    )


def test_prepare_header():
    # Replace header
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "$request.header.authorization", "Bearer 123")
    assert isinstance(result, PreparedRequest)
    del result.headers["Content-Type"]
    del result.headers["Content-Length"]
    assert result.headers == {"authorization": "Bearer 123", "X-Number": "7.35"}


def test_prepare_method():
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "$method", "POST")
    assert isinstance(result, PreparedRequest)
    assert result.method == "POST"


def test_prepare_url():
    req = copy.deepcopy(test_request)
    result = prepare_request(req, "$url", "https://v2.api.test/companies?id=123")
    assert isinstance(result, PreparedRequest)
    assert result.url == "https://v2.api.test/companies?id=123"


@pytest.mark.parametrize(
    "req, expression, expected_exception_type",
    [
        (Response(), "foo.bar", ValueError),
        (copy.deepcopy(test_request), "users.2.name", IndexError),
        (copy.deepcopy(test_request), "$response.body", RuntimeExpressionError),
    ],
)
def test_evaluate_with_errors(req: Request, expression: str, expected_exception_type):
    with pytest.raises(RuntimeExpressionError) as e:
        prepare_request(req, expression, "value")

    if expected_exception_type != RuntimeExpressionError:
        assert isinstance(e.value.caused_by, expected_exception_type)
    else:
        assert e.value.caused_by is None
