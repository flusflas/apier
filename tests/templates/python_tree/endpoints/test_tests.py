from unittest import mock

import pytest
import xmltodict
from requests.structures import CaseInsensitiveDict

from .setup import build_client
from ..common import make_response, to_dict

build_client("python-tree")

pkg_name = __name__.rsplit(".", 1)[0]
request_mock_pkg = f"{pkg_name}._build.api.requests.request"

if True:
    from ._build.api import API
    from ._build.security import BearerToken
    from ._build.models.models import (
        Employee,
        Company,
        PostTestsOneOfRequest,
        PostTestsOneOfResponse200,
    )

test_resp_company01 = Company(
    id="shiny_stickers",
    name="Shiny Stickers Corporation",
    category="stickers",
    created="2023-06-19T21:00:00Z",
    modified="2023-06-19T21:30:00Z",
)

test_resp_employee01 = Employee(number=123, name="Johny")


@pytest.mark.parametrize(
    "employee_id, name, extra_info",
    [
        (123, "Johny", 1000),
        (17, "Alice", "Lorem ipsum dolor"),
    ],
)
def test_post_employee_input_parameters(employee_id, name, extra_info):
    """
    Tests a successful request to create a new employee using a test endpoint
    that uses the input-parameters extension.
    """
    expected_req = {
        "number": employee_id,
        "name": name,
        name: "shiny_stickers",
        "extra": extra_info,
    }

    expected_raw_resp = make_response(201, test_resp_employee01)

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .tests("shiny_stickers")
            .employees()
            .post(employee_id, name, extra_info, params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/tests/shiny_stickers/employees",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=to_dict(expected_req),
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 201
    assert resp == test_resp_employee01
    assert isinstance(resp, Employee)


@pytest.mark.parametrize(
    "req, expected_resp",
    [
        (test_resp_company01, PostTestsOneOfResponse200.parse_obj("OK")),
        (test_resp_employee01, PostTestsOneOfResponse200.parse_obj("OK")),
    ],
)
def test_one_of(req, expected_resp):
    """Tests a successful request using a model defined with oneOf."""
    expected_req = PostTestsOneOfRequest.parse_obj(req)

    expected_raw_resp = make_response(200, "OK")

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .tests()
            .one_of()
            .post(PostTestsOneOfRequest.parse_obj(req), params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/tests/oneOf",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=to_dict(expected_req),
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == expected_resp
    assert isinstance(resp, PostTestsOneOfResponse200)


@pytest.mark.parametrize(
    "req, expected_resp, expected_resp_xml",
    [
        (
            test_resp_company01,
            test_resp_company01,
            xmltodict.unparse({"Company": to_dict(test_resp_company01)}),
        ),
        (
            to_dict(test_resp_company01),
            test_resp_company01,
            xmltodict.unparse({"Company": to_dict(test_resp_company01)}),
        ),
    ],
)
def test_xml(req, expected_resp, expected_resp_xml):
    """Tests sending a request with XML content type."""
    expected_req = Company.parse_obj(req)
    expected_req_xml = xmltodict.unparse({"root": to_dict(expected_req)})

    expected_raw_resp = make_response(
        200,
        expected_resp_xml,
        headers=CaseInsensitiveDict({"Content-Type": "application/xml"}),
    )

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .tests()
            .echo_xml()
            .post(expected_req, params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/tests/echo_xml",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token", "Content-Type": "application/xml"},
        data=expected_req_xml,
        files=None,
        json=None,
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == expected_resp
    assert isinstance(resp, Company)
