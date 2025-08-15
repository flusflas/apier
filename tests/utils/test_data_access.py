import pytest

from apier.utils.data_access import get_nested


class Dummy:
    def __init__(self):
        self.foo = {"bar": [1, {"baz": 2}]}
        self.value = 42


@pytest.mark.parametrize(
    "data,key,expected",
    [
        ({"a": {"b": 1}}, "a.b", 1),
        ({"a": [0, {"b": 2}]}, "a.1.b", 2),
        ([{"x": 5}], "0.x", 5),
        (Dummy(), "foo.bar.1.baz", 2),
        (Dummy(), "value", 42),
    ],
)
def test_get_nested(data, key, expected):
    assert get_nested(data, key) == expected


@pytest.mark.parametrize(
    "data,key,default,expected",
    [
        ({"a": {}}, "a.b", 99, 99),
        ([{"x": 5}], "1.x", "not found", "not found"),
        (Dummy(), "foo.missing", None, None),
    ],
)
def test_get_nested_default(data, key, default, expected):
    assert get_nested(data, key, default=default) == expected


def test_get_nested_keyerror():
    with pytest.raises(KeyError):
        get_nested({}, "missing.key")


def test_get_nested_indexerror():
    with pytest.raises(IndexError):
        get_nested([1, 2], "5")
