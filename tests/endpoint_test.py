import pytest

from endpoints import Endpoint, EndpointLayer, EndpointParameter, parse_endpoint
from openapi import Definition

openapi_definition = Definition({
    "paths": {
        "/stores/{store_id}": 1,
        "/stores/{store_id}/products/{product_id}": 2,
        "/{first_id}/{second_id}/info": 3,
    }
})


@pytest.mark.parametrize("path, expected", [
    ("/stores/{store_id}", Endpoint(
        path="/stores/{store_id}",
        definition=openapi_definition.paths["/stores/{store_id}"],
        layers=[
            EndpointLayer(
                path="/stores/{store_id}",
                api_levels=["stores"],
                parameters=[
                    EndpointParameter(name="store_id", type="string", required=False),
                ],
                next=[],
                methods=[],
            )
        ],
    )),
    ("/stores/{store_id}/products/{product_id}", Endpoint(
        path="/stores/{store_id}/products/{product_id}",
        definition=openapi_definition.paths["/stores/{store_id}/products/{product_id}"],
        layers=[
            EndpointLayer(
                path="/stores/{store_id}",
                api_levels=["stores"],
                parameters=[
                    EndpointParameter(name="store_id", type="string", required=False),
                ],
                next=[],
                methods=[],
            ),
            EndpointLayer(
                path="/products/{product_id}",
                api_levels=["products"],
                parameters=[
                    EndpointParameter(name="product_id", type="string", required=False),
                ],
                next=[],
                methods=[],
            )
        ]
    )),
    ("/{first_id}/{second_id}/info", Endpoint(
        path="/{first_id}/{second_id}/info",
        definition=openapi_definition.paths["/{first_id}/{second_id}/info"],
        layers=[
            EndpointLayer(
                path="/{first_id}/{second_id}",
                api_levels=[],
                parameters=[
                    EndpointParameter(name="first_id", type="string", required=False),
                    EndpointParameter(name="second_id", type="string", required=False),
                ],
                next=[],
                methods=[],
            ),
            EndpointLayer(
                path="/info",
                api_levels=["info"],
                parameters=[],
                next=[],
                methods=[],
            )
        ]
    )),
])
def test_parse_endpoint(path, expected):
    """ Tests parsing an endpoint. """
    assert parse_endpoint(path, openapi_definition) == expected


@pytest.mark.parametrize("layer, expected_param_names, expected_param_types", [
    (
            EndpointLayer(
                path="/stores/{store_id}",
                parameters=[
                    EndpointParameter(name="store_id", type="string", required=False),
                ]),
            ["store_id"],
            ["string"]
    ),
    (
            EndpointLayer(
                path="/products/{product_id}",
                parameters=[
                    EndpointParameter(name="product_id", type="string", required=False),
                ],
            ),
            ["product_id"],
            ["string"]
    ),
    (
            EndpointLayer(
                path="/{first_id}/{second_id}",
                parameters=[
                    EndpointParameter(name="first_id", type="integer", required=False),
                    EndpointParameter(name="second_id", type="boolean", required=False),
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
