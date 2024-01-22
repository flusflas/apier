from unittest import mock

import pytest

from .setup import build_client
from ..common import make_json_response, to_dict, to_json

build_client()
request_mock_pkg = 'test.templates.python.endpoints._build.api.requests.request'
if True:
    from ._build.api import API
    from ._build.models.exceptions import ResponseError
    from ._build.models.models import (EmployeeCreate, Employee, EmployeeList,
                                       ErrorResponse)

test_req_create01 = EmployeeCreate(
    name="Alice",
    number=1000
)

test_resp_employee01 = Employee(
    name="Alice",
    number=1000
)

test_resp_employee02 = Employee(
    name="Bob",
    number=1001
)

test_resp_employee03 = Employee(
    name="Charlie",
    number=1002
)

test_resp_employee04 = Employee(
    name="Dylan",
    number=1003
)

test_employee_not_found = ErrorResponse(
    status=404,
    message="Employee not found!"
)


@pytest.mark.parametrize("req, expected_resp", [
    (test_req_create01, test_resp_employee01),
    (to_dict(test_req_create01), test_resp_employee01),
])
def test_create(req, expected_resp):
    """
    Tests a successful request to create a Employee.
    """
    from ._build.api import API

    expected_raw_resp = make_json_response(201, expected_resp)

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (API(host="test-api.com").
                companies("shiny_stickers").
                employees().
                post(req, params={'foo': 'bar'}))

    m.assert_called_once_with("POST",
                              "https://test-api.com/companies/shiny_stickers/employees",
                              params={'foo': 'bar'},
                              headers={'Content-Type': 'application/json'},
                              data=to_json(req),
                              timeout=3)

    assert resp.http_response().status_code == 201
    assert resp == expected_resp
    assert isinstance(resp, Employee)


def test_get():
    """
    Tests a successful request to get a Employee.
    """
    expected_resp = make_json_response(200, test_resp_employee01)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = (API(host="test-api.com").
                companies("shiny_stickers").
                employees(1000).
                get(params={'foo': 'bar'}))

    m.assert_called_once_with("GET",
                              "https://test-api.com/companies/shiny_stickers/employees/1000",
                              params={'foo': 'bar'},
                              headers={},
                              data=None,
                              timeout=3)

    assert resp.http_response().status_code == 200
    assert resp == test_resp_employee01
    assert isinstance(resp, Employee)


def test_list():
    """
    Tests a successful request to get the list of Companies.
    """
    expected_list = EmployeeList(
        results=[
            test_resp_employee01,
            test_resp_employee02,
            test_resp_employee03,
            test_resp_employee04,
        ],
        cursors={
            'next': None,
            'previous': None,
        }
    )
    expected_resp = make_json_response(200, expected_list)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = (API(host="test-api.com").
                companies("shiny_stickers").
                employees().
                get(params={'foo': 'bar'}))

    m.assert_called_once_with("GET",
                              "https://test-api.com/companies/shiny_stickers/employees",
                              params={'foo': 'bar'},
                              headers={},
                              data=None,
                              timeout=3)

    assert resp.http_response().status_code == 200
    assert resp == expected_list
    assert isinstance(resp, EmployeeList)


def test_get_error():
    """
    Tests a request to get a Employee that returns a 404 error response.
    """
    expected_resp = make_json_response(404, test_employee_not_found)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        with pytest.raises(ResponseError) as e:
            API(host="test-api.com").companies("shiny_stickers").get()

    m.assert_called_once_with("GET",
                              "https://test-api.com/companies/shiny_stickers",
                              params=None,
                              headers={},
                              data=None,
                              timeout=3)

    exc = e.value
    assert exc.http_response().status_code == 404
    assert exc.error == test_employee_not_found
    assert isinstance(exc.error, ErrorResponse)
