from unittest import mock

import pytest

from .common import make_response, to_dict
from .setup import build_client

build_client("python-tree")
if True:
    from ._build.api import API
    from ._build.security import BearerToken


def test_create_successfully():
    """Creates an API instance successfully."""
    api = API(host="test-api.com")
    assert api.host == "https://test-api.com"


@pytest.mark.parametrize("verify", [True, False])
def test_make_request(verify):
    """
    Makes a request to the API.
    """
    req_payload = {"foo": "bar"}
    expected_resp_payload = {"key1": 123, "key2": "hey!"}

    expected_resp = make_response(200, expected_resp_payload)

    with mock.patch("requests.request", return_value=expected_resp) as m:
        resp = API(host="test-api.com", verify=verify).make_request(
            "POST", "/info", json=req_payload, auth=False
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/info",
        params={},
        headers={},
        data=[],
        files=None,
        json=to_dict(req_payload),
        timeout=3,
        verify=verify,
    )

    assert resp.status_code == 200
    assert resp.json() == expected_resp_payload


@pytest.mark.parametrize("verify", [True, False])
def test_make_request_with_security(verify):
    """
    Makes a request to the API setting a security scheme.
    """
    req_payload = {"foo": "bar"}
    expected_resp_payload = {"key1": 123, "key2": "hey!"}

    expected_resp = make_response(200, expected_resp_payload)

    api = API(host="test-api.com", verify=verify).with_security(BearerToken("my_token"))

    with mock.patch("requests.request", return_value=expected_resp) as m:
        resp = api.make_request("POST", "/info", json=req_payload)

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/info",
        params={},
        headers={"Authorization": "Bearer my_token"},
        data=[],
        files=None,
        json=to_dict(req_payload),
        timeout=3,
        verify=verify,
    )

    assert resp.status_code == 200
    assert resp.json() == expected_resp_payload


@pytest.mark.parametrize("verify", [True, False])
def test_make_request_form_data(verify):
    """
    Makes a request to the API with a form data payload.
    """
    req_payload = {"foo": "bar"}
    expected_resp_payload = {"key1": 123, "key2": "hey!"}

    expected_resp = make_response(200, expected_resp_payload)

    api = API(host="test-api.com", verify=verify).with_security(BearerToken("my_token"))

    with mock.patch("requests.request", return_value=expected_resp) as m:
        resp = api.make_request("POST", "/info", data=req_payload)

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/info",
        params={},
        headers={"Authorization": "Bearer my_token"},
        data=req_payload,
        files=None,
        json=None,
        timeout=3,
        verify=verify,
    )

    assert resp.status_code == 200
    assert resp.json() == expected_resp_payload


@pytest.mark.parametrize("verify", [True, False])
def test_make_request_xml(verify):
    """
    Makes a request to the API with an XML payload.
    """
    req_payload = "<foo>bar</foo>"
    expected_resp_payload = {"key1": 123, "key2": "hey!"}

    expected_resp = make_response(200, expected_resp_payload)

    api = API(host="test-api.com", verify=verify).with_security(BearerToken("my_token"))

    with mock.patch("requests.request", return_value=expected_resp) as m:
        resp = api.make_request(
            "POST",
            "/info",
            data=req_payload,
            headers={"Content-Type": "application/xml"},
        )

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/info",
        params={},
        headers={"Authorization": "Bearer my_token", "Content-Type": "application/xml"},
        data=req_payload,
        files=None,
        json=None,
        timeout=3,
        verify=verify,
    )

    assert resp.status_code == 200
    assert resp.json() == expected_resp_payload


@pytest.mark.parametrize(
    ("host", "url"),
    [
        ("test-api.com", "/info"),
        ("test-api.com", "info"),
        ("test-api.com/", "/info"),
        ("test-api.com/", "info"),
        ("https://test-api.com", "/info"),
        ("https://test-api.com", "info"),
        ("https://test-api.com/", "/info"),
        ("https://test-api.com/", "info"),
    ],
)
def test_make_request_url_join(host, url):
    """
    Ensures that the URL is correctly joined with the host.
    """
    req_payload = {"foo": "bar"}

    with mock.patch("requests.request") as m:
        API(host=host).make_request("POST", url, json=req_payload, auth=False)

    m.assert_called_once_with(
        "POST",
        "https://test-api.com/info",
        params={},
        headers={},
        data=[],
        files=None,
        json=to_dict(req_payload),
        timeout=3,
        verify=True,
    )
