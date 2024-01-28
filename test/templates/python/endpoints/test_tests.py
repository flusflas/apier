from unittest import mock

from .setup import build_client
from ..common import make_response, to_json

build_client()
request_mock_pkg = 'test.templates.python.endpoints._build.api.requests.request'
if True:
    from ._build.api import API
    from ._build.models.models import (Employee)

test_resp_employee01 = Employee(
    number=123,
    name="Johny"
)


def test_post_employee_input_parameters():
    """
    Tests a successful request to create a new employee using a test endpoint
    that uses the input-parameters extension.
    """
    from ._build.api import API

    expected_req = {
        "number": 123,
        "name": "Johny",
        "Johny": "shiny_stickers"
    }

    expected_raw_resp = make_response(201, test_resp_employee01)

    with mock.patch(request_mock_pkg, return_value=expected_raw_resp) as m:
        resp = (API(host="test-api.com").
                tests("shiny_stickers").
                employees().
                post(123, "Johny", params={'foo': 'bar'}))

    m.assert_called_once_with("POST",
                              "https://test-api.com/tests/shiny_stickers/employees",
                              params={'foo': 'bar'},
                              headers={'Content-Type': 'application/json'},
                              data=to_json(expected_req),
                              timeout=3)

    assert resp.http_response().status_code == 201
    assert resp == test_resp_employee01
    assert isinstance(resp, Employee)
