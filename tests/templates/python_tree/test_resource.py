from io import IOBase
from typing import Union, IO

import pytest
from requests import Response
from requests.structures import CaseInsensitiveDict

from apier.templates.python_tree.base.internal.resource import (
    ContentTypeValidationResult,
)
from apier.templates.python_tree.base.internal.resource import (
    _validate_request_payload,
    _parse_response_content,
)
from apier.templates.python_tree.base.models.basemodel import APIBaseModel
from apier.templates.python_tree.base.models.exceptions import ExceptionList
from apier.templates.python_tree.base.models.primitives import FilePayload


class Person(APIBaseModel):
    name: str
    age: int


class String(APIBaseModel):
    __root__: str


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            {
                "body": "Lorem ipsum dolor",
                "req_content_types": [],
                "headers": {},
            },
            ContentTypeValidationResult(
                type="",
                data="Lorem ipsum dolor",
                json=None,
                headers=CaseInsensitiveDict(),
            ),
        ),
        (
            {
                "body": "Lorem ipsum dolor",
                "req_content_types": [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                "headers": {},
            },
            ContentTypeValidationResult(
                type="text/plain",
                data="Lorem ipsum dolor",
                json=None,
                headers=CaseInsensitiveDict({"Content-Type": "text/plain"}),
            ),
        ),
        (
            {
                "body": '{"name": "Alice", "age": 24}',
                "req_content_types": [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                "headers": None,
            },
            ContentTypeValidationResult(
                type="application/json",
                data=None,
                json={"name": "Alice", "age": 24},
                headers=CaseInsensitiveDict({"Content-Type": "application/json"}),
            ),
        ),
        (
            {
                "body": {"name": "Alice", "age": 24},
                "req_content_types": [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                "headers": None,
            },
            ContentTypeValidationResult(
                type="application/json",
                data=None,
                json={"name": "Alice", "age": 24},
                headers=CaseInsensitiveDict({"Content-Type": "application/json"}),
            ),
        ),
        (
            {
                "body": Person(name="Alice", age=24),
                "req_content_types": [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                "headers": None,
            },
            ContentTypeValidationResult(
                type="application/json",
                data=None,
                json={"name": "Alice", "age": 24},
                headers=CaseInsensitiveDict({"Content-Type": "application/json"}),
            ),
        ),
        (
            {
                "body": '<?xml version="1.0" encoding="utf-8"?>\n'
                "<root><name>Alice</name><age>24</age></root>",
                "req_content_types": [
                    ("application/xml", Person),
                    ("application/json", Person),
                    ("text/plain", String),
                ],
                "headers": None,
            },
            ContentTypeValidationResult(
                type="application/xml",
                data='<?xml version="1.0" encoding="utf-8"?>\n'
                "<root><name>Alice</name><age>24</age></root>",
                headers=CaseInsensitiveDict({"Content-Type": "application/xml"}),
            ),
        ),
        (
            {
                "body": {"name": "Alice", "age": 24},
                "req_content_types": [
                    ("application/xml", Person),
                    ("application/json", Person),
                    ("text/plain", String),
                ],
                "headers": None,
            },
            ContentTypeValidationResult(
                type="application/xml",
                data='<?xml version="1.0" encoding="utf-8"?>\n'
                "<root><name>Alice</name><age>24</age></root>",
                headers=CaseInsensitiveDict({"Content-Type": "application/xml"}),
            ),
        ),
        (
            {
                "body": Person(name="Alice", age=24),
                "req_content_types": [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                "headers": {"content-type": "application/xml; charset=utf-8"},
            },
            ContentTypeValidationResult(
                type="application/xml",
                data='<?xml version="1.0" encoding="utf-8"?>\n'
                "<root><name>Alice</name><age>24</age></root>",
                headers=CaseInsensitiveDict(
                    {"content-type": "application/xml; charset=utf-8"}
                ),
            ),
        ),
        (
            # This test case checks that even if a content type is supported,
            # it will not be used if the body is not compatible with it
            {
                "body": Person(name="Alice", age=24),
                "req_content_types": [
                    ("application/json", String),
                    ("multipart/form-data; charset=utf-8", Person),
                ],
                "headers": {},
            },
            ContentTypeValidationResult(
                type="multipart/form-data",
                data={"name": "Alice", "age": 24},
                files={},
                headers=CaseInsensitiveDict({"content-type": "multipart/form-data"}),
            ),
        ),
    ],
)
def test__validate_request_payload(data, expected):
    body = data["body"]
    req_content_types = data["req_content_types"]
    headers = data["headers"]
    result = _validate_request_payload(body, req_content_types, headers)
    assert result == expected


@pytest.mark.parametrize(
    "data, expected_exception",
    [
        (
            {
                "body": True,
                "req_content_types": [
                    ("application/json", Person),
                    ("application/xml", Person),
                ],
                "headers": {},
            },
            ExceptionList(
                "Unexpected data format",
                [
                    ValueError('Value type "bool" cannot be converted to JSON'),
                    ValueError('Value type "bool" cannot be converted to XML'),
                ],
            ),
        ),
        (
            {
                "body": True,
                "req_content_types": [
                    ("application/xml", Person),
                    ("application/json", Person),
                ],
                "headers": {},
            },
            ExceptionList(
                "Unexpected data format",
                [
                    ValueError('Value type "bool" cannot be converted to XML'),
                    ValueError('Value type "bool" cannot be converted to JSON'),
                ],
            ),
        ),
    ],
)
def test__validate_request_payload_errors(data, expected_exception):
    body = data["body"]
    req_content_types = data["req_content_types"]
    headers = data["headers"]
    with pytest.raises(type(expected_exception)) as e:
        _validate_request_payload(body, req_content_types, headers)

    assert str(e.value) == str(expected_exception)
    assert len(e.value.exceptions) == len(expected_exception.exceptions)
    for i, e in enumerate(e.value.exceptions):
        assert type(e) is type(expected_exception.exceptions[i])
        assert str(e) == str(expected_exception.exceptions[i])


class File(APIBaseModel):
    __root__: Union[bytes, IO, IOBase, FilePayload]

    class Config:
        arbitrary_types_allowed = True


class FileBytes(APIBaseModel):
    __root__: bytes


class FileIO(APIBaseModel):
    __root__: IOBase

    class Config:
        arbitrary_types_allowed = True


def make_response(**kwargs) -> Response:
    """Creates a mock response object with the given parameters."""
    response = Response()
    for key, value in kwargs.items():
        if key == "content":
            key = "_content"
        elif key == "headers":
            value = CaseInsensitiveDict(value)
        setattr(response, key, value)

    return response


@pytest.mark.parametrize(
    ("response", "resp_class", "expected"),
    [
        (
            make_response(
                headers={"content-type": "application/json"},
                content=b'{"name": "Alice", "age": 24}',
            ),
            Person,
            {"name": "Alice", "age": 24},
        ),
        (
            make_response(
                headers={"content-type": "application/xml"},
                content=b'<?xml version="1.0" encoding="utf-8"?><root><name>Alice</name><age>24</age></root>',
            ),
            Person,
            {"name": "Alice", "age": "24"},
        ),
        (
            make_response(
                headers={"content-type": "text/plain"},
                content=b"Hello, World!",
            ),
            String,
            "Hello, World!",
        ),
        (
            make_response(
                headers={
                    "content-type": "application/pdf",
                    "content-disposition": 'attachment; filename="file.pdf"',
                },
                raw=b"PDF-1.4\n%...",
            ),
            File,
            FilePayload(
                filename="file.pdf",
                content=b"PDF-1.4\n%...",
                content_type="application/pdf",
            ),
        ),
        (
            make_response(
                headers={
                    "content-type": "text/csv",
                    "content-disposition": "attachment; filename*=UTF-8''%e2%82%ac%20rates.csv",
                },
                raw=b"currency,rate\nEUR,1.2345\nUSD,0.9876",
            ),
            File,
            FilePayload(
                filename="€ rates.csv",
                content=b"currency,rate\nEUR,1.2345\nUSD,0.9876",
                content_type="text/csv",
            ),
        ),
        (
            make_response(
                headers={
                    "content-type": "text/csv",
                    "content-disposition": "attachment; filename*=UTF-8''%e2%82%ac%20rates.csv",
                },
                raw=b"currency,rate\nEUR,1.2345\nUSD,0.9876",
            ),
            FileIO,
            b"currency,rate\nEUR,1.2345\nUSD,0.9876",
        ),
        (
            make_response(
                headers={
                    "content-type": "text/csv",
                    "content-disposition": "attachment; filename*=UTF-8''%e2%82%ac%20rates.csv",
                },
                content=b"currency,rate\nEUR,1.2345\nUSD,0.9876",
            ),
            FileBytes,
            b"currency,rate\nEUR,1.2345\nUSD,0.9876",
        ),
    ],
)
def test_parse_response_content(response: Response, resp_class, expected):
    """
    Tests the _parse_response_content function.
    """
    result = _parse_response_content(response, resp_class)
    assert result == expected
    assert type(result) is type(expected)
