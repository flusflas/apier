from collections import OrderedDict
from io import BytesIO, StringIO, IOBase
from unittest import mock

import pytest
import requests
from pydantic import ValidationError
from pytest_httpserver import HTTPServer
from requests_toolbelt import MultipartEncoder

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
@pytest.mark.parametrize("stream_file", [True, False])
def test_upload_file(
    filename, file, req_type, expected_name, expected_content_type, stream_file
):
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

    def make_request():
        expected_raw_resp = make_response(201, BooksResponse201())
        with mock.patch(send_mock_pkg, return_value=expected_raw_resp) as mock_send:
            api = API(host="test-api.com")
            return api.books().post(req_data, params={"foo": "bar"}), mock_send

    if stream_file:
        resp, m = make_request()
    else:
        # Simulate ImportError for requests_toolbelt so that the request
        # is handled without file streaming support
        def simulate_import_error(module_name):
            original_import = __import__

            def side_effect(name, *args, **kwargs):
                if name == module_name:
                    raise ImportError(f"No module named '{name}'")
                return original_import(name, *args, **kwargs)

            return side_effect

        with mock.patch(
            "builtins.__import__",
            side_effect=simulate_import_error("requests_toolbelt"),
        ):
            resp, m = make_request()

    ### Assert request was made correctly

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

    if stream_file:
        assert isinstance(actual_prepared_req.body, MultipartEncoder)
    else:
        assert len(actual_prepared_req.body) == len(expected_prepared_req.body)

    assert actual_prepared_req.hooks == expected_prepared_req.hooks

    actual_headers = actual_prepared_req.headers
    expected_headers = expected_prepared_req.headers
    assert actual_headers["Content-Length"] == expected_headers["Content-Length"]
    assert actual_headers.get("Content-Type", "").startswith("multipart/form-data;")

    ### Assert response

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


@pytest.mark.parametrize("stream", [True, False, None])
@pytest.mark.parametrize(
    ("expected_content_type", "expected_content_disposition", "expected_filename"),
    [
        (
            "application/pdf",
            'attachment; filename="document.pdf"',
            "document.pdf",
        ),
        (
            "application/pdf",
            "attachment; filename*=UTF-8''%e2%82%ac%20rates.csv",
            "€ rates.csv",
        ),
    ],
)
def test_book_download(
    httpserver: HTTPServer,
    stream: bool,
    expected_content_type,
    expected_content_disposition,
    expected_filename,
):
    """Tests downloading a file from the API."""
    file_content = b"PDF content\n" * 1000

    httpserver.expect_request("/books/123/download", method="GET").respond_with_data(
        response_data=file_content,
        status=200,
        content_type=expected_content_type,
        headers={"Content-Disposition": expected_content_disposition},
    )

    # Set the 'stream' parameter to control whether the response is streamed
    # or not. If 'stream' is None, it will not be set to test the default behavior.
    get_kwargs = {"stream": stream} if stream is not None else {}
    expected_stream = stream if stream is not None else True

    # Instead of returning a value, I want the mock to just capture the call but act as normal. I just want to check that the function was called with the expected parameters.
    #
    # Using side_effect=None doesn't work as the call returns a MagicMock instance.
    with mock.patch(request_mock_pkg, wraps=requests.request) as mock_request:
        resp = API(host=httpserver.url_for("")).books("123").download().get(**get_kwargs)

    # Assert that the request was made with the expected stream parameter
    assert mock_request.call_args.kwargs['stream'] == expected_stream

    http_response = resp.http_response()

    assert http_response.status_code == 200
    assert http_response.headers["Content-Type"] == expected_content_type
    assert http_response.headers["Content-Disposition"] == expected_content_disposition

    assert http_response._content_consumed != stream

    assert isinstance(resp.__root__, FilePayload)

    file_payload = resp.__root__
    assert file_payload.filename == expected_filename
    assert file_payload.content_type == expected_content_type

    # If stream is None, it should behave like True since the stream extension
    # is set to true for this endpoint
    if stream or stream is None:
        assert isinstance(file_payload.content, IOBase)
        actual_content = b""
        while chunk := file_payload.content.read(100):
            actual_content += chunk
    else:
        assert isinstance(file_payload.content, bytes)
        actual_content = file_payload.content

    assert actual_content == file_content
