from __future__ import annotations

from typing import List, Optional, Union, Literal

from pydantic import BaseModel, Field, root_validator


class NextOperationParameters(BaseModel):
    """Represents a parameters for the next API operation in a pagination flow."""

    name: str = Field(
        ...,
        min_length=1,
        description="The name of the parameter, as defined in the OpenAPI spec.",
    )
    value: str = Field(
        ...,
        min_length=1,
        description="A runtime expression that evaluates to the value of the parameter.",
    )


class NextOperation(BaseModel):
    """Represents the next API operation to be executed in a pagination flow."""

    name: str = Field(
        ...,
        description="The name of the next operation, as defined in the OpenAPI spec.",
    )
    parameters: Optional[List[NextOperationParameters]] = Field(
        [],
        description="Parameters to be passed to the next operation. If required "
        "parameters are not provided, such as path parameters, the operation "
        "will fail.",
    )


class PaginationModifier(BaseModel):
    """Represents a request modifier to update parameters for the next request."""

    op: Optional[str] = "set"
    param: str
    value: str


class PaginationDescription(BaseModel):
    """Represents a pagination mode that uses modifiers to control the pagination flow."""

    class Config:
        allow_population_by_field_name = True

    operation: Optional[NextOperation] = Field(
        None, description="The next operation to execute for pagination."
    )
    reuse_previous_request: bool = Field(
        default=False,
        description="Whether the next request should reuse the previous request's parameters.",
    )
    modifiers: List[PaginationModifier] = Field(
        default_factory=list,
        description="List of request modifiers to update parameters for the next request.",
    )
    result: str = Field(
        ...,
        description="A dynamic expression that evaluates to the list of results in the response.",
    )
    has_more: str = Field(
        ...,
        description="A dynamic expression that evaluates to a boolean indicating if there are more results.",
    )

    @root_validator
    def check_mutually_exclusive_fields(cls, values):
        next_op = values.get("operation")
        reuse = values.get("reuse_previous_request")
        modifiers = values.get("modifiers")

        if next_op and (reuse or modifiers):
            raise ValueError(
                "'operation' cannot be set with 'reuse_previous_request' or 'modifiers'."
            )

        return values


class PaginationModifier(BaseModel):
    op: Optional[str] = "set"
    param: str
    value: str


PaginationDescription.update_forward_refs()
