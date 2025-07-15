from unittest import mock

import pytest

from .common import make_response, to_json
from .setup import build_client

build_client("python-tree")
if True:
    from ._build.api import API
    from ._build.security import BearerToken


def test_create_successfully():
    """ Creates an API instance successfully. """
    api = API(host="test-api.com")
    assert api.host == "https://test-api.com"


@pytest.mark.parametrize("verify", [True, False])
def test_make_request(verify):
    """
    Makes a request to the API.
    """
    req_payload = {"foo": "bar"}
    expected_resp_payload = {
        "key1": 123,
        "key2": "hey!"
    }

    expected_resp = make_response(200, expected_resp_payload)

    with mock.patch("requests.request", return_value=expected_resp) as m:
        resp = (API(host="test-api.com", verify=verify).
                make_request("POST", "/info", body=req_payload, auth=False))

    m.assert_called_once_with("POST",
                              "https://test-api.com/info",
                              params={},
                              headers={'Content-Type': 'application/json'},
                              data=to_json(req_payload),
                              timeout=3,
                              verify=verify)

    assert resp.status_code == 200
    assert resp.json() == expected_resp_payload


@pytest.mark.parametrize("verify", [True, False])
def test_make_request_with_security(verify):
    """
    Makes a request to the API setting a security scheme.
    """
    req_payload = {"foo": "bar"}
    expected_resp_payload = {
        "key1": 123,
        "key2": "hey!"
    }

    expected_resp = make_response(200, expected_resp_payload)

    api = API(host="test-api.com", verify=verify).with_security(BearerToken('my_token'))

    with mock.patch("requests.request", return_value=expected_resp) as m:
        resp = (api.
                make_request("POST", "/info", body=req_payload))

    m.assert_called_once_with("POST",
                              "https://test-api.com/info",
                              params={},
                              headers={
                                  'Authorization': 'Bearer my_token',
                                  'Content-Type': 'application/json',
                              },
                              data=to_json(req_payload),
                              timeout=3,
                              verify=verify)

    assert resp.status_code == 200
    assert resp.json() == expected_resp_payload
