from .basemodel import APIBaseModel


class StringResponse(APIBaseModel):
    __root__: str


class IntegerResponse(APIBaseModel):
    __root__: int


class FloatResponse(APIBaseModel):
    __root__: float


class BooleanResponse(APIBaseModel):
    __root__: bool


class ObjectResponse(APIBaseModel):
    __root__: object


class ArrayResponse(APIBaseModel):
    __root__: list


class NoResponse(APIBaseModel):
    pass
