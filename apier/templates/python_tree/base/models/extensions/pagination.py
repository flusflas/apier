from __future__ import annotations

from typing import List, Optional

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


class PaginationDescription(BaseModel):
    """Describes the pagination configuration for an API endpoint."""

    class Config:
        allow_population_by_field_name = True

    operation: Optional[NextOperation] = Field(
        None,
        description="The next operation to execute. If not provided, the next "
        "pagination step will use the current operation.",
    )
    reuse_previous_request: bool = Field(
        default=False,
        alias="reuse_previous_request",
        description="Whether to reuse the previous request for pagination.",
    )
    method: str = ""
    url: str = ""
    modifiers: List[PaginationModifier] = Field(default_factory=list)
    result: str
    has_more: str

    # TODO: Validate that operation is not set with reuse_previous_request or modifiers
    # TODO: Remove method and url, as they can be assigned by modifiers

    # @root_validator
    # def validate_fields(cls, values: dict):
    #     if isinstance(values, PaginationDescription):
    #         values = values.dict()
    #     reuse = values.get("reuse_previous_request") or values.get(
    #         "reuse_previous_request"
    #     )
    #     for attr in ["method", "url"]:
    #         if not reuse and not values[attr]:
    #             raise ValueError(
    #                 f"The field '{attr}' is required if 'reuse_previous_request' is False"
    #             )
    #     return values


class PaginationModifier(BaseModel):
    op: Optional[str] = "set"
    param: str
    value: str


PaginationDescription.update_forward_refs()
