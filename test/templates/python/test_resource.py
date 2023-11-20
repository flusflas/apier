import pytest

from templates.python.base.internal.resource import _validate_request_payload
from templates.python.base.models.basemodel import APIBaseModel
from templates.python.base.models.exceptions import ExceptionList


class Person(APIBaseModel):
    name: str
    age: int


class String(APIBaseModel):
    __root__: str


@pytest.mark.parametrize("data, expected", [
    (
            {
                'body': 'Lorem ipsum dolor',
                'req_content_types': [],
                'headers': {},
            },
            {
                'body': 'Lorem ipsum dolor',
                'headers': {}
            }
    ),
    (
            {
                'body': 'Lorem ipsum dolor',
                'req_content_types': [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                'headers': {},
            },
            {
                'body': 'Lorem ipsum dolor',
                'headers': {
                    'Content-Type': 'text/plain'
                }
            }
    ),
    (
            {
                'body': '{"name": "Alice", "age": 24}',
                'req_content_types': [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                'headers': None,
            },
            {
                'body': '{"name": "Alice", "age": 24}',
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    ),
    (
            {
                'body': {"name": "Alice", "age": 24},
                'req_content_types': [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                'headers': None,
            },
            {
                'body': '{"name": "Alice", "age": 24}',
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    ),
    (
            {
                'body': Person(name="Alice", age=24),
                'req_content_types': [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                'headers': None,
            },
            {
                'body': '{"name": "Alice", "age": 24}',
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    ),
    (
            {
                'body': '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<root><name>Alice</name><age>24</age></root>',
                'req_content_types': [
                    ("application/xml", Person),
                    ("application/json", Person),
                    ("text/plain", String),
                ],
                'headers': None,
            },
            {
                'body': '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<root><name>Alice</name><age>24</age></root>',
                'headers': {
                    'Content-Type': 'application/xml'
                }
            }
    ),
    (
            {
                'body': {"name": "Alice", "age": 24},
                'req_content_types': [
                    ("application/xml", Person),
                    ("application/json", Person),
                    ("text/plain", String),
                ],
                'headers': None,
            },
            {
                'body': '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<root><name>Alice</name><age>24</age></root>',
                'headers': {
                    'Content-Type': 'application/xml'
                }
            }
    ),
    (
            {
                'body': Person(name="Alice", age=24),
                'req_content_types': [
                    ("application/json", Person),
                    ("application/xml", Person),
                    ("text/plain", String),
                ],
                'headers': {'content-type': 'application/xml; charset=utf-8'},
            },
            {
                'body': '<?xml version="1.0" encoding="utf-8"?>\n'
                        '<root><name>Alice</name><age>24</age></root>',
                'headers': {
                    'content-type': 'application/xml; charset=utf-8'
                }
            }
    ),
])
def test__validate_request_payload(data, expected):
    body = data['body']
    req_content_types = data['req_content_types']
    headers = data['headers']
    actual_body, actual_headers = _validate_request_payload(body,
                                                            req_content_types,
                                                            headers)
    assert actual_body == expected['body']
    assert actual_headers == expected['headers']


@pytest.mark.parametrize("data, expected_exception", [
    (
            {
                'body': True,
                'req_content_types': [
                    ("application/json", Person),
                    ("application/xml", Person),
                ],
                'headers': {},
            },
            ExceptionList('nooo', [
                ValueError('Value type "bool" cannot be converted to JSON'),
                ValueError('Value type "bool" cannot be converted to XML'),
            ])
    ),
    (
            {
                'body': True,
                'req_content_types': [
                    ("application/xml", Person),
                    ("application/json", Person),
                ],
                'headers': {},
            },
            ExceptionList('nooo', [
                ValueError('Value type "bool" cannot be converted to XML'),
                ValueError('Value type "bool" cannot be converted to JSON'),
            ])
    ),
])
def test__validate_request_payload_errors(data, expected_exception):
    body = data['body']
    req_content_types = data['req_content_types']
    headers = data['headers']
    with pytest.raises(type(expected_exception)) as e:
        _validate_request_payload(body, req_content_types, headers)

    assert str(e.value) == str(expected_exception)
    assert len(e.value.exceptions) == len(expected_exception.exceptions)
    for i, e in enumerate(e.value.exceptions):
        assert type(e) == type(expected_exception.exceptions[i])
        assert str(e) == str(expected_exception.exceptions[i])
