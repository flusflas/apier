import pytest
from apier.templates.python_tree.base.internal.content_type import (
    parse_content_type,
    content_types_compatible,
)


@pytest.mark.parametrize(
    "content_type, expected",
    [
        (
            "application/json",
            {
                "media_type": "application/json",
                "type": "application",
                "subtype": "json",
                "suffix": None,
                "parameters": {},
            },
        ),
        (
            "application/json; charset=utf-8",
            {
                "media_type": "application/json",
                "type": "application",
                "subtype": "json",
                "suffix": None,
                "parameters": {"charset": "utf-8"},
            },
        ),
        (
            "application/vnd.api+json",
            {
                "media_type": "application/vnd.api+json",
                "type": "application",
                "subtype": "vnd.api",
                "suffix": "json",
                "parameters": {},
            },
        ),
        (
            "application/vnd.api+json; version=1",
            {
                "media_type": "application/vnd.api+json",
                "type": "application",
                "subtype": "vnd.api",
                "suffix": "json",
                "parameters": {"version": "1"},
            },
        ),
        (
            "application/vnd.api+json; version=1; charset=utf-8",
            {
                "media_type": "application/vnd.api+json",
                "type": "application",
                "subtype": "vnd.api",
                "suffix": "json",
                "parameters": {"version": "1", "charset": "utf-8"},
            },
        ),
    ],
)
def test_parse_content_type(content_type, expected):
    assert parse_content_type(content_type) == expected


@pytest.mark.parametrize(
    "type1, type2, expected",
    [
        ("application/json", "text/plain", False),
        ("application/json", "application/json", True),
        ("application/json", "application/xml", False),
        ("application/json", "application/*", True),
        ("application/*", "application/json", True),
        ("application/vnd.api+json", "application/vnd.api+json", True),
        ("application/vnd.api+json", "application/vnd.api+xml", False),
        ("application/vnd.api+json", "application/vnd.api+json; charset=utf-8", True),
        ("application/vnd.api+json; charset=utf-8", "application/vnd.api+json", True),
        (
            "application/vnd.api+json; charset=utf-8",
            "application/vnd.api+xml; charset=utf-8",
            False,
        ),
        (
            "application/vnd.api+json; version=1",
            "application/vnd.api+json; version=2",
            True,
        ),
        (
            "application/vnd.api+json; version=1",
            "application/vnd.api+xml; version=1",
            False,
        ),
        ("application/json; version=1", "application/json-patch+json; version=2", True),
        ("application/json-patch+json; version=1", "application/json; version=2", True),
    ],
)
def test_content_types_are_compatible(type1, type2, expected):
    assert content_types_compatible(type1, type2) == expected
