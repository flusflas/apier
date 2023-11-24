import pytest

from utils.strings import to_pascal_case, to_snake_case


@pytest.mark.parametrize("name, expected", [
    ("foobar", "Foobar"),
    ("Foobar", "Foobar"),
    ("foo_bar", "FooBar"),
    ("foo-bar", "FooBar"),
    ("foo bar", "FooBar"),
    ("FooBar", "FooBar"),
    ("foo__bar", "FooBar"),
    ("foo--bar", "FooBar"),
    ("foo  bar", "FooBar"),
    ("foo_-bar", "FooBar"),
    ("foo-_bar", "FooBar"),
    ("foo -bar", "FooBar"),
    ("foo _bar", "FooBar"),
    ("foo - bar", "FooBar"),
    ("foo1 - bar2", "Foo1Bar2"),
    ("foo1_bar2", "Foo1Bar2"),
    ("_foo_bar", "FooBar"),
])
def test_to_pascal_case(name, expected):
    actual = to_pascal_case(name)
    assert actual == expected


@pytest.mark.parametrize("name, expected", [
    ("foobar", "foobar"),
    ("Foobar", "foobar"),
    ("foo_bar", "foo_bar"),
    ("foo-bar", "foo_bar"),
    ("foo bar", "foo_bar"),
    ("FooBar", "foo_bar"),
    ("FooBAr", "foo_bar"),
    ("foo__bar", "foo_bar"),
    ("foo--bar", "foo_bar"),
    ("foo  bar", "foo_bar"),
    ("foo_-bar", "foo_bar"),
    ("foo-_bar", "foo_bar"),
    ("foo -bar", "foo_bar"),
    ("foo _bar", "foo_bar"),
    ("foo - bar", "foo_bar"),
    ("foo1 - bar2", "foo1_bar2"),
    ("foo1_bar2", "foo1_bar2"),
    ("_fooBar", "_foo_bar"),
])
def test_to_snake_case(name, expected):
    actual = to_snake_case(name)
    assert actual == expected
