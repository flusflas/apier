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
    from ._build.models.exceptions import ResponseError
    from ._build.models.models import (
        CompanyCreate,
        Company,
        CompanyList,
        CompanyUpdate,
        ErrorResponse,
        AnyValue,
    )
    from ._build.models.primitives import NoResponse

test_req_create01 = CompanyCreate(
    id="shiny_stickers",
    name="Shiny Stickers",
    category="stickers",
)

test_req_update01 = CompanyUpdate(
    id="shiny_stickers",
    name="Shiny Stickers",
    category="stickers",
)

test_resp_company01 = Company(
    id="shiny_stickers",
    name="Shiny Stickers Corporation",
    category="stickers",
    created="2023-06-19T21:00:00Z",
    modified="2023-06-19T21:30:00Z",
)

test_resp_company02 = Company(
    id="happy_pharma",
    name="Happy Pharmaceutical Corp.",
    category="evil",
    created="2017-10-08T10:30:00Z",
    modified="2021-08-30T12:15:00Z",
)

test_resp_company03 = Company(
    id="company_03",
    name="Company 3",
    category="technology",
    created="2023-06-19T21:00:00Z",
    modified="2023-06-19T21:30:00Z",
)

test_resp_company04 = Company(
    id="company_04",
    name="Company 3",
    category="clothing",
    created="2017-10-08T10:30:00Z",
    modified="2021-08-30T12:15:00Z",
)

test_company_not_found = ErrorResponse(status=404, message="Company not found!")


@pytest.mark.parametrize(
    "req, expected_resp, req_headers",
    [
        (test_req_create01, test_resp_company01, {}),
        (to_dict(test_req_create01), test_resp_company01, {}),
        (test_req_create01, test_resp_company01, {"content-type": "application/xml"}),
    ],
)
def test_create(req, expected_resp, req_headers):
    """
    Tests a successful request to create a Company.
    """
    from ._build.api import API

    req_headers = CaseInsensitiveDict(req_headers)
    expected_raw_resp = make_response(201, expected_resp)

    expected_req_headers = {"Authorization": "Bearer token"}
    expected_req_headers.update(req_headers)
    if req_headers.get("content-type") == "application/xml":
        expected_req_data = xmltodict.unparse({"root": to_dict(req)})
        expected_req_json = None
    else:
        expected_req_data = []
        expected_req_json = to_dict(req)

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies()
            .create(req, params={"foo": "bar"}, headers=req_headers)
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/companies",
        params={"foo": "bar"},
        headers=expected_req_headers,
        data=expected_req_data,
        files=None,
        json=expected_req_json,
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 201
    assert resp == expected_resp
    assert isinstance(resp, Company)


def test_create_default_status_code():
    """
    Tests a request to create a Company that returns an undefined status code.
    """
    from ._build.api import API

    expected_raw_resp = make_response(200, "OK")

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies()
            .create(test_req_create01, params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/companies",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=to_dict(test_req_create01),
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == AnyValue.parse_obj("OK")
    assert isinstance(resp, AnyValue)


def test_get():
    """
    Tests a successful request to get a Company.
    """
    expected_resp = make_response(200, test_resp_company01)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies("shiny_stickers")
            .get(params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "GET",
        "https://test-api.com/companies/shiny_stickers",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=None,
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == test_resp_company01
    assert isinstance(resp, Company)


def test_list():
    """
    Tests a successful request to get the list of Companies.
    """
    expected_list = CompanyList(
        results=[
            test_resp_company01,
            test_resp_company02,
            test_resp_company03,
            test_resp_company04,
        ],
        cursors={
            "next": None,
            "previous": None,
        },
    )
    expected_resp = make_response(200, expected_list)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies()
            .list_companies(params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "GET",
        "https://test-api.com/companies",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=None,
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == expected_list
    assert isinstance(resp, CompanyList)


@pytest.mark.parametrize(
    "req, expected_resp",
    [
        (test_req_update01, test_resp_company01),
        (to_dict(test_req_update01), test_resp_company01),
    ],
)
def test_update(req, expected_resp):
    """
    Tests a successful request to update a Company.
    """
    expected_raw_resp = make_response(200, expected_resp)

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies("shiny_stickers")
            .put(req, params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "PUT",
        "https://test-api.com/companies/shiny_stickers",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=to_dict(req),
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == expected_resp
    assert isinstance(resp, Company)


def test_delete():
    """
    Tests a successful request to delete a Company.
    """
    expected_resp = make_response(204)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies("shiny_stickers")
            .delete(params={"foo": "bar"}, timeout=5.5)
        )

    m.assert_called_once_with(
        "DELETE",
        "https://test-api.com/companies/shiny_stickers",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=None,
        timeout=5.5,
        verify=True,
    )

    assert resp.http_response().status_code == 204
    assert resp == NoResponse()
    assert isinstance(resp, NoResponse)


def test_get_multi_param():
    """
    Tests a successful request to get a Company using two URL parameters in
    the same layer.
    """
    expected_resp = make_response(200, test_resp_company01)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = (
            API(host="test-api.com")
            .with_security(BearerToken("token"))
            .companies("shiny_stickers", 7)
            .get(params={"foo": "bar"})
        )

    m.assert_called_once_with(
        "GET",
        "https://test-api.com/companies/shiny_stickers/7",
        params={"foo": "bar"},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=None,
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 200
    assert resp == test_resp_company01
    assert isinstance(resp, Company)


def test_get_error():
    """
    Tests a request to get a Company that returns a 404 error response.
    """
    expected_resp = make_response(404, test_company_not_found)

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        with pytest.raises(ResponseError) as e:
            (
                API(host="test-api.com")
                .with_security(BearerToken("token"))
                .companies("shiny_stickers")
                .get()
            )

    m.assert_called_once_with(
        "GET",
        "https://test-api.com/companies/shiny_stickers",
        params={},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=None,
        timeout=3,
        verify=True,
    )

    exc = e.value
    assert exc.http_response().status_code == 404
    assert exc.error == test_company_not_found
    assert isinstance(exc.error, ErrorResponse)


def test_get_error_not_raised():
    """
    Tests a request to get a Company that returns a 404 error response but
    is not raised by the client.
    """
    expected_resp = make_response(404, test_company_not_found)

    api = API(host="test-api.com")
    api._raise_errors = False  # Disable automatic error raising

    with mock.patch(request_mock_pkg, return_value=expected_resp) as m:
        resp = api.with_security(BearerToken("token")).companies("shiny_stickers").get()

    m.assert_called_once_with(
        "GET",
        "https://test-api.com/companies/shiny_stickers",
        params={},
        headers={"Authorization": "Bearer token"},
        data=[],
        files=None,
        json=None,
        timeout=3,
        verify=True,
    )

    assert resp.http_response().status_code == 404
    assert resp == test_company_not_found
    assert isinstance(resp, ErrorResponse)
