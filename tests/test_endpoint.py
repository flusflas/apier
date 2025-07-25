import copy

import pytest

from apier.core.consts import NO_RESPONSE_ID
from apier.core.api.endpoints import (
    EndpointsParser,
    Endpoint,
    EndpointLayer,
    EndpointOperation,
    EndpointParameter,
    ContentSchema,
    parse_parameters,
    split_endpoint_layers,
)
from apier.extensions.extensions import Extensions
from apier.extensions.method_name import MethodNameDescription
from apier.core.api.openapi import Definition

openapi_definition = Definition.load("tests/definitions/companies_api.yaml")

ERROR_RESPONSE_DEFINITION = {
    "properties": {
        "message": {"example": "Oh, no!", "type": "string"},
        "status": {"example": 400, "type": "integer"},
    },
    "required": ["status", "message"],
    "title": "Error Response",
    "type": "object",
}

expected_endpoints = {
    "/companies/{company_id}": Endpoint(
        path="/companies/{company_id}",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(
                        name="company_id",
                        description="Company!!!",
                        in_location="path",
                        type="string",
                        required=True,
                    ),
                ],
                next=[],
                operations=[
                    EndpointOperation(
                        name="get",
                        definition=openapi_definition.paths["/companies/{company_id}"][
                            "get"
                        ],
                        description="Returns a company by its ID.",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                                format="",
                            )
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name="Company",
                                content_type="application/json",
                                schema={
                                    "allOf": [
                                        {"$ref": "#/components/schemas/CompanyBase"},
                                        {
                                            "properties": {
                                                "created": {
                                                    "example": "2023-06-19T21:00:00Z",
                                                    "format": "date-time",
                                                    "type": "string",
                                                },
                                                "modified": {
                                                    "example": "2023-06-19T21:00:00Z",
                                                    "format": "date-time",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    ],
                                    "title": "Company",
                                    "type": "object",
                                },
                                code=200,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=404,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                        extensions=Extensions(
                            method_name=MethodNameDescription(
                                default="", templates={"go": "Get"}
                            )
                        ),
                    ),
                    EndpointOperation(
                        name="put",
                        definition=openapi_definition.paths["/companies/{company_id}"][
                            "put"
                        ],
                        description="Updates an exising company.",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                                format="",
                            )
                        ],
                        request_schemas=[
                            ContentSchema(
                                name="CompanyUpdate",
                                content_type="application/json",
                                schema={
                                    "allOf": [
                                        {"$ref": "#/components/schemas/CompanyBase"}
                                    ],
                                    "title": "Company Update Request",
                                    "type": "object",
                                },
                                code=-1,
                            )
                        ],
                        response_schemas=[
                            ContentSchema(
                                name="Company",
                                content_type="application/json",
                                schema={
                                    "allOf": [
                                        {"$ref": "#/components/schemas/CompanyBase"},
                                        {
                                            "properties": {
                                                "created": {
                                                    "example": "2023-06-19T21:00:00Z",
                                                    "format": "date-time",
                                                    "type": "string",
                                                },
                                                "modified": {
                                                    "example": "2023-06-19T21:00:00Z",
                                                    "format": "date-time",
                                                    "type": "string",
                                                },
                                            },
                                            "type": "object",
                                        },
                                    ],
                                    "title": "Company",
                                    "type": "object",
                                },
                                code=200,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=400,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=409,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                    ),
                    EndpointOperation(
                        name="delete",
                        definition=openapi_definition.paths["/companies/{company_id}"][
                            "delete"
                        ],
                        description="Deletes a company :(",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                                format="",
                            )
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name=NO_RESPONSE_ID,
                                content_type="",
                                schema={},
                                code=204,
                                is_inline=True,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=404,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                    ),
                ],
            )
        ],
    ),
    "/companies/{company_id}/employees": Endpoint(
        path="/companies/{company_id}/employees",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(
                        name="company_id",
                        description="Company!!!",
                        in_location="path",
                        type="string",
                        required=True,
                        format="",
                    )
                ],
                next=[],
                operations=[],
            ),
            EndpointLayer(
                path="/employees",
                api_levels=["employees"],
                parameters=[],
                next=[],
                operations=[
                    EndpointOperation(
                        name="post",
                        definition=openapi_definition.paths[
                            "/companies/{company_id}/employees"
                        ]["post"],
                        description="Hires a new employee!",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                        request_schemas=[
                            ContentSchema(
                                name="EmployeeCreate",
                                code=-1,
                                content_type="application/json",
                                schema=openapi_definition.definition["components"][
                                    "schemas"
                                ]["EmployeeCreate"],
                            ),
                        ],
                        response_schemas=[
                            ContentSchema(
                                name="Employee",
                                code=201,
                                content_type="application/json",
                                schema=openapi_definition.definition["components"][
                                    "schemas"
                                ]["Employee"],
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=400,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=409,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                    ),
                    EndpointOperation(
                        name="get",
                        definition=openapi_definition.paths[
                            "/companies/{company_id}/employees"
                        ]["get"],
                        description="Returns all your employees.",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name="EmployeeList",
                                code=200,
                                content_type="application/json",
                                schema=openapi_definition.definition["components"][
                                    "schemas"
                                ]["EmployeeList"],
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=400,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=409,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                        extensions=Extensions.parse_obj(
                            {
                                "pagination": {
                                    "next": {
                                        "reuse-previous-request": True,
                                        "modifiers": [
                                            {
                                                "param": "$request.query.next_cursor",
                                                "value": "$response.body#/cursors/next",
                                            }
                                        ],
                                        "result": "results",
                                        "has_more": "$response.body#/cursors/next",
                                    }
                                }
                            }
                        ),
                    ),
                ],
            ),
        ],
    ),
    "/companies/{company_id}/employees/{employee-num}": Endpoint(
        path="/companies/{company_id}/employees/{employee-num}",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(
                        name="company_id",
                        description="Company!!!",
                        in_location="path",
                        type="string",
                        required=True,
                    ),
                ],
                next=[],
                operations=[],
            ),
            EndpointLayer(
                path="/employees/{employee-num}",
                api_levels=["employees"],
                parameters=[
                    EndpointParameter(
                        name="employee-num",
                        in_location="path",
                        type="integer",
                        required=True,
                    ),
                ],
                next=[],
                operations=[
                    EndpointOperation(
                        name="get",
                        definition=openapi_definition.paths[
                            "/companies/{company_id}/employees/{employee-num}"
                        ]["get"],
                        description="Returns one of your company employees",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                                format="",
                            ),
                            EndpointParameter(
                                name="employee-num",
                                in_location="path",
                                type="integer",
                                required=True,
                                format="",
                            ),
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name="Employee",
                                content_type="application/json",
                                schema={
                                    "allOf": [
                                        {"$ref": "#/components/schemas/EmployeeBase"}
                                    ],
                                    "title": "Employee",
                                    "type": "object",
                                },
                                code=200,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=404,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                    )
                ],
            ),
        ],
    ),
    "/companies/{company_id}/{number}": Endpoint(
        path="/companies/{company_id}/{number}",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}/{number}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(
                        name="company_id",
                        description="Company!!!",
                        in_location="path",
                        type="string",
                        required=True,
                        format="",
                    ),
                    EndpointParameter(
                        name="number",
                        in_location="path",
                        type="integer",
                        required=True,
                        format="",
                    ),
                ],
                next=[],
                operations=[
                    EndpointOperation(
                        name="get",
                        definition=openapi_definition.paths[
                            "/companies/{company_id}/{number}"
                        ]["get"],
                        description="An endpoint used to test multiple path parameters in the same layer.",
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                            EndpointParameter(
                                name="number",
                                in_location="path",
                                type="integer",
                                required=True,
                            ),
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name="Company",
                                code=200,
                                content_type="application/json",
                                schema=openapi_definition.definition["components"][
                                    "schemas"
                                ]["Company"],
                            ),
                            ContentSchema(
                                name="Company",
                                code=200,
                                content_type="application/xml",
                                schema=openapi_definition.definition["components"][
                                    "schemas"
                                ]["Company"],
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=404,
                            ),
                            ContentSchema(
                                name="ErrorResponse",
                                content_type="application/json",
                                schema=ERROR_RESPONSE_DEFINITION,
                                code=500,
                            ),
                        ],
                    )
                ],
            )
        ],
    ),
}


@pytest.mark.parametrize(
    "layer, expected_param_names, expected_param_types",
    [
        (
            EndpointLayer(
                path="/companies/{company_id}",
                parameters=[
                    EndpointParameter(
                        name="company_id",
                        description="Company!!!",
                        in_location="path",
                        type="string",
                        required=True,
                    ),
                ],
            ),
            ["company_id"],
            ["string"],
        ),
        (
            EndpointLayer(
                path="/employees/{employee-num}",
                parameters=[
                    EndpointParameter(
                        name="employee-num",
                        in_location="path",
                        type="integer",
                        required=True,
                    ),
                ],
            ),
            ["employee-num"],
            ["integer"],
        ),
        (
            EndpointLayer(
                path="/{first_id}/{second_id}",
                parameters=[
                    EndpointParameter(
                        name="first_id",
                        in_location="path",
                        type="integer",
                        required=True,
                    ),
                    EndpointParameter(
                        name="second_id",
                        in_location="path",
                        type="boolean",
                        required=True,
                    ),
                ],
            ),
            ["first_id", "second_id"],
            ["integer", "boolean"],
        ),
    ],
)
def test_endpoint_layer_param_functions(
    layer: EndpointLayer, expected_param_names, expected_param_types
):
    """
    Tests the convenience methods EndpointLayer.param_names() and
    EndpointLayer.param_types().
    """
    assert layer.param_names() == expected_param_names
    assert layer.param_types() == expected_param_types


@pytest.mark.parametrize(
    "path, expected",
    [
        ("/companies/{company_id}", expected_endpoints["/companies/{company_id}"]),
        (
            "/companies/{company_id}/employees/{employee-num}",
            expected_endpoints["/companies/{company_id}/employees/{employee-num}"],
        ),
        (
            "/companies/{company_id}/employees",
            expected_endpoints["/companies/{company_id}/employees"],
        ),
    ],
)
def test_parse_endpoint(path, expected):
    """Tests parsing an endpoint."""
    parser = EndpointsParser(openapi_definition)
    assert parser.parse_endpoint(path) == expected


@pytest.mark.parametrize(
    "endpoint, expected",
    [
        (
            Endpoint("/companies/{company_id}"),
            Endpoint(
                path="/companies/{company_id}",
                layers=[
                    EndpointLayer(
                        path="/companies/{company_id}",
                        api_levels=["companies"],
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                    )
                ],
            ),
        ),
        (
            Endpoint("/companies/{company_id}/employees/{employee-num}"),
            Endpoint(
                path="/companies/{company_id}/employees/{employee-num}",
                layers=[
                    EndpointLayer(
                        path="/companies/{company_id}",
                        api_levels=["companies"],
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                    ),
                    EndpointLayer(
                        path="/employees/{employee-num}",
                        api_levels=["employees"],
                        parameters=[
                            EndpointParameter(
                                name="employee-num",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                    ),
                ],
            ),
        ),
        (
            Endpoint("/{first_id}/{second_id}/info"),
            Endpoint(
                path="/{first_id}/{second_id}/info",
                layers=[
                    EndpointLayer(
                        path="/{first_id}/{second_id}",
                        parameters=[
                            EndpointParameter(
                                name="first_id",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                            EndpointParameter(
                                name="second_id",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                    ),
                    EndpointLayer(
                        path="/info",
                        api_levels=["info"],
                    ),
                ],
            ),
        ),
    ],
)
def test_split_endpoint_layers(endpoint, expected):
    """Tests splitting an endpoint into its layers."""
    split_endpoint_layers(endpoint)
    assert endpoint == expected


@pytest.mark.parametrize(
    "endpoint, expected",
    [
        (
            Endpoint("/companies/{company_id}/{number}", definition=openapi_definition),
            Endpoint(
                path="/companies/{company_id}/{number}",
                definition=openapi_definition,
                layers=[
                    EndpointLayer(
                        path="/companies/{company_id}/{number}",
                        api_levels=["companies"],
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                            EndpointParameter(
                                name="number",
                                in_location="path",
                                type="integer",
                                required=True,
                            ),
                        ],
                        operations=[
                            EndpointOperation(
                                name="get",
                                definition=openapi_definition.paths[
                                    "/companies/{company_id}/{number}"
                                ]["get"],
                                description="An endpoint used to test multiple path parameters in the same layer.",
                                parameters=[
                                    EndpointParameter(
                                        name="company_id",
                                        description="Company!!!",
                                        in_location="path",
                                        type="string",
                                        required=True,
                                    ),
                                    EndpointParameter(
                                        name="number",
                                        in_location="path",
                                        type="integer",
                                        required=True,
                                    ),
                                ],
                            )
                        ],
                    )
                ],
            ),
        ),
        (
            Endpoint("/companies/{company_id}", definition=openapi_definition),
            Endpoint(
                path="/companies/{company_id}",
                definition=openapi_definition,
                layers=[
                    EndpointLayer(
                        path="/companies/{company_id}",
                        api_levels=["companies"],
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                        operations=[
                            EndpointOperation(
                                name="get",
                                definition=openapi_definition.paths[
                                    "/companies/{company_id}"
                                ]["get"],
                                description="Returns a company by its ID.",
                                parameters=[
                                    EndpointParameter(
                                        name="company_id",
                                        description="Company!!!",
                                        in_location="path",
                                        type="string",
                                        required=True,
                                    ),
                                ],
                            ),
                            EndpointOperation(
                                name="put",
                                definition=openapi_definition.paths[
                                    "/companies/{company_id}"
                                ]["put"],
                                description="Updates an exising company.",
                                parameters=[
                                    EndpointParameter(
                                        name="company_id",
                                        description="Company!!!",
                                        in_location="path",
                                        type="string",
                                        required=True,
                                    ),
                                ],
                            ),
                            EndpointOperation(
                                name="delete",
                                definition=openapi_definition.paths[
                                    "/companies/{company_id}"
                                ]["delete"],
                                description="Deletes a company :(",
                                parameters=[
                                    EndpointParameter(
                                        name="company_id",
                                        description="Company!!!",
                                        in_location="path",
                                        type="string",
                                        required=True,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ),
        (
            Endpoint(
                "/companies/{company_id}/employees/{employee-num}",
                definition=openapi_definition,
            ),
            Endpoint(
                path="/companies/{company_id}/employees/{employee-num}",
                definition=openapi_definition,
                layers=[
                    EndpointLayer(
                        path="/companies/{company_id}",
                        api_levels=["companies"],
                        parameters=[
                            EndpointParameter(
                                name="company_id",
                                description="Company!!!",
                                in_location="path",
                                type="string",
                                required=True,
                            ),
                        ],
                    ),
                    EndpointLayer(
                        path="/employees/{employee-num}",
                        api_levels=["employees"],
                        parameters=[
                            EndpointParameter(
                                name="employee-num",
                                in_location="path",
                                type="integer",
                                required=True,
                            ),
                        ],
                        operations=[
                            EndpointOperation(
                                name="get",
                                definition=openapi_definition.paths[
                                    "/companies/{company_id}"
                                    "/employees/{employee-num}"
                                ]["get"],
                                description="Returns one of your company employees",
                                parameters=[
                                    EndpointParameter(
                                        name="company_id",
                                        description="Company!!!",
                                        in_location="path",
                                        type="string",
                                        required=True,
                                    ),
                                    EndpointParameter(
                                        name="employee-num",
                                        in_location="path",
                                        type="integer",
                                        required=True,
                                    ),
                                ],
                            )
                        ],
                    ),
                ],
            ),
        ),
    ],
)
def test_parse_parameters(endpoint, expected):
    """
    Tests processing an OpenAPI definition to fill the endpoint parameters
    information.
    """
    EndpointsParser(openapi_definition)
    split_endpoint_layers(endpoint)

    parse_parameters(endpoint)
    assert endpoint == expected


@pytest.mark.parametrize(
    "endpoint, expected_methods",
    [
        (
            Endpoint("/companies/{company_id}/{number}", definition=openapi_definition),
            expected_endpoints["/companies/{company_id}/{number}"].operations,
        ),
        (
            Endpoint(
                "/companies/{company_id}/employees", definition=openapi_definition
            ),
            expected_endpoints["/companies/{company_id}/employees"].operations,
        ),
    ],
)
def test_process_endpoint_config(endpoint, expected_methods):
    """
    Tests processing an Endpoint to fill their content schemas for request and
    responses.
    """
    expected_methods = copy.deepcopy(expected_methods)
    for m in expected_methods:
        m.extensions = None

    parser = EndpointsParser(openapi_definition)

    split_endpoint_layers(endpoint)
    parse_parameters(endpoint)

    parser.parse_content_schemas(endpoint)
    assert endpoint.operations == expected_methods
