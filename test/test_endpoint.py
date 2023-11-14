import pytest

from consts import NO_RESPONSE_ID
from endpoints import (Endpoint, EndpointLayer, EndpointParameter,
                       parse_endpoint, split_endpoint_layers, parse_parameters, EndpointMethod, ContentSchema,
                       parse_content_schemas)
from openapi import Definition

openapi_definition = Definition.load('definitions/companies_api.yaml')

expected_endpoints = {
    "/companies/{company_id}": Endpoint(
        path="/companies/{company_id}",
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path="/companies/{company_id}",
                api_levels=["companies"],
                parameters=[
                    EndpointParameter(name="company_id",
                                      in_location="path",
                                      type="string",
                                      required=True),
                ],
                next=[],
                methods=[
                    EndpointMethod(
                        name='get',
                        description='Returns a company by its ID.',
                        parameters=[
                            EndpointParameter(name='company_id',
                                              in_location='path',
                                              type='string',
                                              required=True,
                                              format='')
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(name='Company',
                                          content_type='application/json',
                                          definition={'allOf': [
                                              {'$ref': '#/components/schemas/CompanyBase'},
                                              {'properties': {'created': {
                                                  'example': '2023-06-19T21:00:00Z',
                                                  'format': 'date-time',
                                                  'type': 'string'},
                                                  'modified': {
                                                      'example': '2023-06-19T21:00:00Z',
                                                      'format': 'date-time',
                                                      'type': 'string'}},
                                                  'type': 'object'}],
                                              'title': 'Company',
                                              'type': 'object'},
                                          code=200),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=404,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=500,
                                          is_inline=True)
                        ]
                    ),
                    EndpointMethod(
                        name='put',
                        description='Updates an exising company.',
                        parameters=[
                            EndpointParameter(name='company_id',
                                              in_location='path',
                                              type='string',
                                              required=True,
                                              format='')
                        ],
                        request_schemas=[
                            ContentSchema(name='CompanyUpdate',
                                          content_type='application/json',
                                          definition={'allOf': [
                                              {'$ref': '#/components/schemas/CompanyBase'}],
                                              'title': 'Company Update Request',
                                              'type': 'object'},
                                          code=0)
                        ],
                        response_schemas=[
                            ContentSchema(name='Company',
                                          content_type='application/json',
                                          definition={
                                              'allOf': [
                                                  {'$ref': '#/components/schemas/CompanyBase'},
                                                  {
                                                      'properties': {
                                                          'created': {
                                                              'example': '2023-06-19T21:00:00Z',
                                                              'format': 'date-time',
                                                              'type': 'string'
                                                          },
                                                          'modified': {
                                                              'example': '2023-06-19T21:00:00Z',
                                                              'format': 'date-time',
                                                              'type': 'string'}
                                                      },
                                                      'type': 'object'
                                                  }],
                                              'title': 'Company',
                                              'type': 'object'
                                          },
                                          code=200),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=400,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=409,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=500,
                                          is_inline=True),
                        ]
                    ),
                    EndpointMethod(name='delete',
                                   description='Deletes a company :(',
                                   parameters=[
                                       EndpointParameter(name='company_id',
                                                         in_location='path',
                                                         type='string',
                                                         required=True,
                                                         format='')
                                   ],
                                   request_schemas=[],
                                   response_schemas=[
                                       ContentSchema(name=NO_RESPONSE_ID,
                                                     content_type='',
                                                     definition={},
                                                     code=204,
                                                     is_inline=True),
                                       ContentSchema(name=NO_RESPONSE_ID,
                                                     content_type='',
                                                     definition={},
                                                     code=404,
                                                     is_inline=True),
                                       ContentSchema(name=NO_RESPONSE_ID,
                                                     content_type='',
                                                     definition={},
                                                     code=500,
                                                     is_inline=True),
                                   ])
                ],
            )
        ],
    ),
    "/companies/{company_id}/employees": Endpoint(
        path='/companies/{company_id}/employees',
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path='/companies/{company_id}',
                api_levels=['companies'],
                parameters=[
                    EndpointParameter(
                        name='company_id',
                        in_location='path',
                        type='string',
                        required=True,
                        format='')
                ],
                next=[],
                methods=[]
            ),
            EndpointLayer(
                path='/employees',
                api_levels=['employees'],
                parameters=[],
                next=[],
                methods=[
                    EndpointMethod(
                        name="post",
                        description='Hires a new employee!',
                        parameters=[
                            EndpointParameter(name="company_id",
                                              in_location="path",
                                              type="string",
                                              required=True),
                        ],
                        request_schemas=[
                            ContentSchema(
                                name="EmployeeCreate",
                                code=0,
                                content_type="application/json",
                                definition=openapi_definition.definition['components']['schemas']['EmployeeCreate'],
                            ),
                        ],
                        response_schemas=[
                            ContentSchema(
                                name="Employee",
                                code=201,
                                content_type="application/json",
                                definition=openapi_definition.definition['components']['schemas']['Employee'],
                            ),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=400,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=409,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=500,
                                          is_inline=True)
                        ]
                    ),
                    EndpointMethod(
                        name="get",
                        description='Returns all your employees.',
                        parameters=[
                            EndpointParameter(name="company_id",
                                              in_location="path",
                                              type="string",
                                              required=True),
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name="EmployeeList",
                                code=200,
                                content_type="application/json",
                                definition=openapi_definition.definition['components']['schemas']['EmployeeList'],
                            ),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=400,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=409,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=500,
                                          is_inline=True)
                        ]
                    ),
                ],
            ),
        ],
    ),
    "/companies/{company_id}/employees/{employee_num}": Endpoint(
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
                    EndpointParameter(name="employee_num", in_location="path", type="integer", required=True),
                ],
                next=[],
                methods=[
                    EndpointMethod(
                        name='get',
                        description='Returns one of your company employees',
                        parameters=[
                            EndpointParameter(name='company_id',
                                              in_location='path',
                                              type='string',
                                              required=True,
                                              format=''),
                            EndpointParameter(name='employee_num',
                                              in_location='path',
                                              type='integer',
                                              required=True,
                                              format='')],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name='Employee',
                                content_type='application/json',
                                definition={
                                    'allOf': [
                                        {'$ref': '#/components/schemas/EmployeeBase'}
                                    ],
                                    'title': 'Employee',
                                    'type': 'object'
                                },
                                code=200),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=404,
                                          is_inline=True),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=500,
                                          is_inline=True)
                        ]
                    )
                ],
            )
        ]
    ),
    "/companies/{company_id}/{number}": Endpoint(
        path='/companies/{company_id}/{number}',
        definition=openapi_definition,
        layers=[
            EndpointLayer(
                path='/companies/{company_id}/{number}',
                api_levels=['companies'],
                parameters=[
                    EndpointParameter(
                        name='company_id',
                        in_location='path',
                        type='string',
                        required=True,
                        format=''
                    ),
                    EndpointParameter(
                        name='number',
                        in_location='path',
                        type='integer',
                        required=True,
                        format=''
                    )
                ],
                next=[],
                methods=[
                    EndpointMethod(
                        name="get",
                        description='An endpoint used to test multiple path parameters in the same layer.',
                        parameters=[
                            EndpointParameter(name="company_id", in_location="path",
                                              type="string", required=True),
                            EndpointParameter(name="number", in_location="path",
                                              type="integer", required=True),
                        ],
                        request_schemas=[],
                        response_schemas=[
                            ContentSchema(
                                name="Company",
                                code=200,
                                content_type="application/json",
                                definition=openapi_definition.definition['components']['schemas']['Company'],
                            ),
                            ContentSchema(
                                name="Company",
                                code=200,
                                content_type="application/xml",
                                definition=openapi_definition.definition['components']['schemas']['Company'],
                            ),
                            ContentSchema(
                                name='ErrorResponse',
                                content_type='application/json',
                                definition={
                                    'properties': {
                                        'message': {
                                            'example': 'Oh, no!',
                                            'type': 'string'
                                        },
                                        'status': {
                                            'example': 400,
                                            'type': 'integer'
                                        }
                                    },
                                    'required': ['status', 'message'],
                                    'title': 'Error Response',
                                    'type': 'object'
                                },
                                code=404
                            ),
                            ContentSchema(name=NO_RESPONSE_ID,
                                          content_type='',
                                          definition={},
                                          code=500,
                                          is_inline=True)
                        ]
                    )
                ]
            )
        ]
    ),
}


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
                    EndpointParameter(name="employee_num", in_location="path", type="integer", required=True),
                ],
            ),
            ["employee_num"],
            ["integer"]
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


@pytest.mark.parametrize("path, expected", [
    (
            "/companies/{company_id}",
            expected_endpoints["/companies/{company_id}"]
    ),
    (
            "/companies/{company_id}/employees/{employee_num}",
            expected_endpoints["/companies/{company_id}/employees/{employee_num}"]
    ),
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
                                 EndpointParameter(name="company_id",
                                                   in_location="path",
                                                   type="string",
                                                   required=True),
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
                                 EndpointParameter(name="company_id",
                                                   in_location="path",
                                                   type="string",
                                                   required=True),
                             ],
                         ),
                         EndpointLayer(
                             path="/employees/{employee_num}",
                             api_levels=["employees"],
                             parameters=[
                                 EndpointParameter(name="employee_num",
                                                   in_location="path",
                                                   type="string",
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
                                 EndpointParameter(name="number", in_location="path", type="integer", required=True),
                             ],
                             methods=[
                                 EndpointMethod(
                                     name="get",
                                     description='An endpoint used to test multiple path parameters in the same layer.',
                                     parameters=[
                                         EndpointParameter(
                                             name="company_id",
                                             in_location="path",
                                             type="string",
                                             required=True),
                                         EndpointParameter(
                                             name="number",
                                             in_location="path",
                                             type="integer",
                                             required=True),
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
                                     description='Returns a company by its ID.',
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                     ]
                                 ),
                                 EndpointMethod(
                                     name="put",
                                     description='Updates an exising company.',
                                     parameters=[
                                         EndpointParameter(name="company_id", in_location="path",
                                                           type="string", required=True),
                                     ]
                                 ),
                                 EndpointMethod(
                                     name="delete",
                                     description='Deletes a company :(',
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
                                 EndpointParameter(name="company_id",
                                                   in_location="path",
                                                   type="string",
                                                   required=True),
                             ],
                         ),
                         EndpointLayer(
                             path="/employees/{employee_num}",
                             api_levels=["employees"],
                             parameters=[
                                 EndpointParameter(name="employee_num",
                                                   in_location="path",
                                                   type="integer",
                                                   required=True),
                             ],
                             methods=[
                                 EndpointMethod(
                                     name="get",
                                     description='Returns one of your company employees',
                                     parameters=[
                                         EndpointParameter(name="company_id",
                                                           in_location="path",
                                                           type="string",
                                                           required=True),
                                         EndpointParameter(name="employee_num",
                                                           in_location="path",
                                                           type="integer",
                                                           required=True),
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


@pytest.mark.parametrize("endpoint, expected_methods", [
    (
            Endpoint("/companies/{company_id}/{number}", definition=openapi_definition),
            expected_endpoints["/companies/{company_id}/{number}"].methods,
    ),
    (
            Endpoint("/companies/{company_id}/employees", definition=openapi_definition),
            expected_endpoints["/companies/{company_id}/employees"].methods,
    )
])
def test_process_endpoint_config(endpoint, expected_methods):
    """
    Tests processing an Endpoint to fill their content schemas for request and
    responses.
    """
    split_endpoint_layers(endpoint)
    parse_parameters(endpoint)

    parse_content_schemas(endpoint)
    assert endpoint.methods == expected_methods
