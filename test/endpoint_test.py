import pytest

from endpoints import (Endpoint, EndpointLayer, EndpointParameter,
                       parse_endpoint, split_endpoint_layers, parse_parameters, EndpointMethod)
from openapi import Definition

openapi_definition = Definition.load('definitions/companies_api.yaml')


@pytest.mark.parametrize("path, expected", [
    ("/companies/{company_id}", Endpoint(
        path="/companies/{company_id}",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                ],
                next=[],
                methods=[],
            )
        ],
    )),
    ("/companies/{company_id}/employees/{employee_num}", Endpoint(
        path="/companies/{company_id}/employees/{employee_num}",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                ],
                next=[],
                methods=[],
            ),
            EndpointLayer(
                path="/employees/{employee_num}",
                api_levels=["employees"],
                parameters=[
                    EndpointParameter(name="employee_num", in_location="path", type="string", required=True),
                ],
                next=[],
                methods=[],
            )
        ]
    )),
    # ("/{first_id}/{second_id}/info", Endpoint(
    #     path="/{first_id}/{second_id}/info",
    #     definition=openapi_definition.paths["/{first_id}/{second_id}/info"],
    #     layers=[
    #         EndpointLayer(
    #             path="/{first_id}/{second_id}",
    #             api_levels=[],
    #             parameters=[
    #                 EndpointParameter(name="first_id", type="string", required=True),
    #                 EndpointParameter(name="second_id", type="string", required=True),
    #             ],
    #             next=[],
    #             methods=[],
    #         ),
    #         EndpointLayer(
    #             path="/info",
    #             api_levels=["info"],
    #             parameters=[],
    #             next=[],
    #             methods=[],
    #         )
    #     ]
    # )),
])
def test_parse_endpoint(path, expected):
    """ Tests parsing an endpoint. """
    assert parse_endpoint(path, openapi_definition) == expected


@pytest.mark.parametrize("endpoint, expected", [
    (
            Endpoint("/companies/{company_id}"),
            Endpoint(path="/companies/{company_id}",
                     layers=[
                         EndpointLayer(
                             path="/companies/{company_id}",
                             api_levels=["companies"],
                             parameters=[
                                 EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                             ],
                         )
                     ])
    ),
    (
            Endpoint("/companies/{company_id}/employees/{employee_num}"),
            Endpoint(path="/companies/{company_id}/employees/{employee_num}",
                     layers=[
                         EndpointLayer(
                             path="/companies/{company_id}",
                             api_levels=["companies"],
                             parameters=[
                                 EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                             ],
                         ),
                         EndpointLayer(
                             path="/employees/{employee_num}",
                             api_levels=["employees"],
                             parameters=[
                                 EndpointParameter(name="employee_num", in_location="path", type="string",
                                                   required=True),
                             ],
                         )
                     ])
    ),
    (
            Endpoint("/{first_id}/{second_id}/info"),
            Endpoint(path="/{first_id}/{second_id}/info",
                     layers=[
                         EndpointLayer(
                             path="/{first_id}/{second_id}",
                             parameters=[
                                 EndpointParameter(name="first_id", in_location="path", type="string", required=True),
                                 EndpointParameter(name="second_id", in_location="path", type="string", required=True),
                             ],
                         ),
                         EndpointLayer(
                             path="/info",
                             api_levels=["info"],
                         )
                     ])
    ),
])
def test_split_endpoint_layers(endpoint, expected):
    """ Tests splitting an endpoint into its layers. """
    split_endpoint_layers(endpoint)
    assert endpoint == expected


@pytest.mark.parametrize("endpoint, expected", [
    (
            Endpoint("/companies/{company_id}/{number}", definition=openapi_definition),
            Endpoint(path="/companies/{company_id}/{number}",
                     definition=openapi_definition,
                     layers=[
                         EndpointLayer(
                             path="/companies/{company_id}/{number}",
                             api_levels=["companies"],
                             parameters=[
                                 EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                                 EndpointParameter(name="number", in_location="path", type="string", required=True),
                             ],
                             methods=[
                                 EndpointMethod(
                                     name="get",
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                         EndpointParameter(name="number", in_location="path",
                                                           type="integer", required=True),
                                     ]
                                 )
                             ]
                         )
                     ])
    ),
    (
            Endpoint("/companies/{company_id}", definition=openapi_definition),
            Endpoint(path="/companies/{company_id}",
                     definition=openapi_definition,
                     layers=[
                         EndpointLayer(
                             path="/companies/{company_id}",
                             api_levels=["companies"],
                             parameters=[
                                 EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                             ],
                             methods=[
                                 EndpointMethod(
                                     name="get",
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                     ]
                                 ),
                                 EndpointMethod(
                                     name="put",
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                     ]
                                 ),
                                 EndpointMethod(
                                     name="delete",
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                     ]
                                 )
                             ]
                         )
                     ])
    ),
    (
            Endpoint("/companies/{company_id}/employees/{employee_num}", definition=openapi_definition),
            Endpoint(path="/companies/{company_id}/employees/{employee_num}",
                     definition=openapi_definition,
                     layers=[
                         EndpointLayer(
                             path="/companies/{company_id}",
                             api_levels=["companies"],
                             parameters=[
                                 EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                             ],
                         ),
                         EndpointLayer(
                             path="/employees/{employee_num}",
                             api_levels=["employees"],
                             parameters=[
                                 EndpointParameter(name="employee_num", in_location="path", type="string",
                                                   required=True),
                             ],
                             methods=[
                                 EndpointMethod(
                                     name="get",
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                         EndpointParameter(name="employee_num", in_location="path",
                                                           type="integer", required=True),
                                     ]
                                 )
                             ]
                         )
                     ])
    ),
])
def test_parse_parameters(endpoint, expected):
    """
    Tests processing an OpenAPI definition to fill the endpoint parameters
    information.
    """
    split_endpoint_layers(endpoint)

    parse_parameters(endpoint)
    assert endpoint == expected


@pytest.mark.parametrize("layer, expected_param_names, expected_param_types", [
    (
            EndpointLayer(
                path="/companies/{company_id}",
                parameters=[
                    EndpointParameter(name="company_id", in_location="path", type="string", required=True),
                ]),
            ["company_id"],
            ["string"]
    ),
    (
            EndpointLayer(
                path="/employees/{employee_num}",
                parameters=[
                    EndpointParameter(name="employee_num", in_location="path", type="string", required=True),
                ],
            ),
            ["employee_num"],
            ["string"]
    ),
    (
            EndpointLayer(
                path="/{first_id}/{second_id}",
                parameters=[
                    EndpointParameter(name="first_id", in_location="path", type="integer", required=True),
                    EndpointParameter(name="second_id", in_location="path", type="boolean", required=True),
                ],
            ),
            ["first_id", "second_id"],
            ["integer", "boolean"]
    ),
])
def test_endpoint_layer_param_functions(layer: EndpointLayer, expected_param_names, expected_param_types):
    """
    Tests the convenience methods EndpointLayer.param_names() and
    EndpointLayer.param_types().
    """
    assert layer.param_names() == expected_param_names
    assert layer.param_types() == expected_param_types
