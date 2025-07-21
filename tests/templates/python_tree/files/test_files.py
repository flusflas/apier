from collections import OrderedDict
from io import BytesIO, StringIO
from unittest import mock

import pytest
import requests
from pydantic import ValidationError

from apier.utils.path import abs_path_from_current_script
from .setup import build_client
from ..common import make_response

build_client("python-tree")

pkg_name = __name__.rsplit(".", 1)[0]
request_mock_pkg = f"{pkg_name}._build.api.requests.request"
send_mock_pkg = f"{pkg_name}._build.api.requests.Session.send"

if True:
    from ._build.api import API
    from ._build.models.models import BookUploadRequest, BooksResponse201
    from ._build.models.primitives import FilePayload

test_file_path = abs_path_from_current_script("data/pdf.pdf")


@pytest.mark.parametrize(
    ("filename", "file", "req_type", "expected_name", "expected_content_type"),
    [
        (
            test_file_path,
            open(test_file_path, "rb"),
            BookUploadRequest,
            "pdf.pdf",
            "application/pdf",
        ),
        (
            test_file_path,
            open(test_file_path, "r"),
            BookUploadRequest,
            "pdf.pdf",
            "application/pdf",
        ),
        (
            test_file_path,
            open(test_file_path, "rb").read(),
            BookUploadRequest,
            "file",
            "application/octet-stream",
        ),
        (
            test_file_path,
            BytesIO(open(test_file_path, "rb").read()),
            BookUploadRequest,
            "file",
            "application/octet-stream",
        ),
        (
            test_file_path,
            StringIO(open(test_file_path, "r").read()),
            BookUploadRequest,
            "file",
            "application/octet-stream",
        ),
        (
            test_file_path,
            open(test_file_path, "rb"),
            dict,
            "pdf.pdf",
            "application/pdf",
        ),
        (
            test_file_path,
            open(test_file_path, "r"),
            dict,
            "pdf.pdf",
            "application/pdf",
        ),
        (
            test_file_path,
            open(test_file_path, "rb").read(),
            dict,
            "file",
            "application/octet-stream",
        ),
        (
            test_file_path,
            BytesIO(open(test_file_path, "rb").read()),
            dict,
            "file",
            "application/octet-stream",
        ),
        (
            test_file_path,
            StringIO(open(test_file_path, "r").read()),
            dict,
            "file",
            "application/octet-stream",
        ),
        (
            abs_path_from_current_script("data/pdf.pdf"),
            FilePayload.from_path(path=abs_path_from_current_script("data/pdf.pdf")),
            BookUploadRequest,
            "pdf.pdf",
            "application/pdf",
        ),
    ],
)
def test_upload_file(filename, file, req_type, expected_name, expected_content_type):
    """
    Tests a successful file upload request using a multipart/form-data request.
    """
    data = {
        "title": "El Quijote",
        "author": "Miguel de Cervantes",
        "publication_year": 1605,
    }

    if req_type is BookUploadRequest:
        req_data = BookUploadRequest(
            title=data["title"],
            author=data["author"],
            publication_year=data["publication_year"],
            file=file,
        )
    elif req_type is dict:
        req_data = {
            "title": data["title"],
            "author": data["author"],
            "publication_year": data["publication_year"],
            "file": file,
        }
    else:
        raise ValueError("Unsupported request type")

    expected_raw_resp = make_response(201, BooksResponse201())

    with mock.patch(send_mock_pkg, return_value=expected_raw_resp) as m:
        resp = API(host="test-api.com").books().post(req_data, params={"foo": "bar"})

    expected_content = open(filename, "rb").read()

    expected_prepared_req = requests.PreparedRequest()
    expected_prepared_req.prepare(
        method="POST",
        url="https://test-api.com/books",
        params={"foo": "bar"},
        data=data,
        files={
            "file": (
                expected_name,
                expected_content,
                expected_content_type,
            )
        },
        json=None,
    )

    m.assert_called_once_with(
        mock.ANY,
        timeout=3,
        allow_redirects=True,
        proxies=OrderedDict(),
        stream=False,
        verify=True,
        cert=None,
    )

    actual_prepared_req = m.call_args[0][0]
    assert actual_prepared_req.method == expected_prepared_req.method
    assert actual_prepared_req.url == expected_prepared_req.url
    assert len(actual_prepared_req.body) == len(expected_prepared_req.body)
    assert actual_prepared_req.hooks == expected_prepared_req.hooks

    actual_headers = actual_prepared_req.headers
    expected_headers = expected_prepared_req.headers
    assert actual_headers["Content-Length"] == expected_headers["Content-Length"]
    assert actual_headers.get("Content-Type", "").startswith("multipart/form-data;")

    assert resp.http_response().status_code == 201
    assert resp == BooksResponse201()


def test_invalid_model_file_value():
    """
    Tests that a validation error is raised when an invalid file value is set to a model.
    """
    with pytest.raises(ValidationError):
        BookUploadRequest(
            title="El Quijote",
            author="Miguel de Cervantes",
            publication_year=1605,
            file=[],  # Invalid file value
        )
