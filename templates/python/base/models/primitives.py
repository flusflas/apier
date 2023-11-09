from .basemodel import IterBaseModel


class StringResponse(IterBaseModel):
    __root__: str


class IntegerResponse(IterBaseModel):
    __root__: int


class FloatResponse(IterBaseModel):
    __root__: float


class BooleanResponse(IterBaseModel):
    __root__: bool


class ObjectResponse(IterBaseModel):
    __root__: object


class ArrayResponse(IterBaseModel):
    __root__: list


class NoResponse(IterBaseModel):
    pass
