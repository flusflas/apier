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


class PaginationModifier(BaseModel):
    """Represents a request modifier to update parameters for the next request."""

    op: Optional[str] = "set"
    param: str
    value: str


class PaginationDescription(BaseModel):
    """Represents a pagination mode that uses modifiers to control the pagination flow."""

    class Config:
        allow_population_by_field_name = True

    # TODO: Split modes into separate classes

    # Operation mode
    operation_id: Optional[str] = Field(
        None,
        description="The operation ID of the next API operation, as defined in the OpenAPI spec.",
    )
    parameters: Optional[List[NextOperationParameters]] = Field(
        [],
        description="Parameters to be passed to the next operation. If required "
        "parameters are not provided, such as path parameters, the operation "
        "will fail.",
    )

    # Modifiers mode
    reuse_previous_request: bool = Field(
        default=False,
        description="Whether the next request should reuse the previous request's parameters.",
    )
    modifiers: List[PaginationModifier] = Field(
        default_factory=list,
        description="List of request modifiers to update parameters for the next request.",
    )

    # Common fields
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
        """
        Validates that the modes are mutually exclusive.
         - If either `operation_id` or `parameters` is set, use 'operation' mode.
           Otherwise, use 'modifiers' mode.
         - In 'operation' mode, `operation_id` must be present.
        """

        operation_id = values.get("operation_id")
        operation_params = values.get("parameters")

        mode = "operation" if operation_id or operation_params else "modifiers"
        if mode == "operation" and not operation_id:
            raise ValueError("'operation_id' is required in operation mode.")

        if mode == "operation" and not operation_id:
            raise ValueError(
                "'operation_id' is required if 'operation_params' are set."
            )

        return values


PaginationDescription.update_forward_refs()
