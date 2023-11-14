import pytest

from utils.strings import to_pascal_case


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
])
def test_to_pascal_case(name, expected):
    actual = to_pascal_case(name)
    assert actual == expected
