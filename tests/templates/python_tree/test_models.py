from typing import Any, Dict, Optional

from apier.templates.python_tree.base.models.basemodel import APIBaseModel


class ClassTest1(APIBaseModel):
    value: Any


class ClassTest2(APIBaseModel):
    __root__: Optional[Dict[str, Any]] = None


def test_api_base_model_dict():
    """
    Tests an APIBaseModel with a dict as __root__.
    """

    class DictClass(APIBaseModel):
        __root__: Optional[Dict[str, Any]] = None

    user_info = {
        "name": "Alice",
        "age": 22,
        "info": {"favourite_color": "Yellow"},
        "lucky_numbers": [1, 2, 3],
    }

    c = DictClass.parse_obj(user_info)

    # dict
    assert c.dict() == user_info
    assert c == user_info

    c._set_http_response(123)
    # assert c._http_response == 123

    c._enable_pagination("123")
    assert c._pagination.results_attribute == "123"


def test_api_base_model_obj():
    """
    Tests an IterBaseModel with a structured object.
    """

    class ObjClass(APIBaseModel):
        name: str
        age: int
        info: Any = None

    user_info = {"name": "Alice", "age": 22, "info": {"favourite_color": "Yellow"}}

    c = ObjClass.parse_obj(user_info)

    # dict
    assert c.dict() == user_info
    assert c == user_info

    c._set_http_response(123)
    assert c.http_response() == 123

    c._enable_pagination("123")
    assert c._pagination.results_attribute == "123"
