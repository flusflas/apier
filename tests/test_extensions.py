import pytest
from pydantic import ValidationError

from apier.extensions.pagination import PaginationDescription


@pytest.mark.parametrize(
    "data,expected_mode",
    [
        (
            {
                "operation_id": "getItems",
                "parameters": [{"name": "page", "value": "$response.body#/nextPage"}],
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "operation",
        ),
        (
            {
                "reuse_previous_request": True,
                "modifiers": [{"op": "set", "param": "page", "value": "2"}],
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "modifiers",
        ),
        (  # Operation mode with no parameters
            {
                "operation_id": "getItems",
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "operation",
        ),
        (  # Modifiers mode with no modifiers
            {
                "reuse_previous_request": True,
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "modifiers",
        ),
    ],
)
def test_pagination_description_valid_modes(data, expected_mode):
    """Tests that PaginationDescription can be created with valid modes."""
    desc = PaginationDescription(**data)
    if expected_mode == "operation":
        assert desc.operation_id is not None
        assert bool(desc.modifiers) == bool(data.get("modifiers"))
        assert desc.reuse_previous_request is None
        assert desc.modifiers is None
    else:
        assert desc.reuse_previous_request == data.get("reuse_previous_request")
        assert bool(desc.modifiers) == bool(data.get("modifiers"))
        assert desc.operation_id is None
        assert desc.parameters is None


@pytest.mark.parametrize(
    "invalid_data, error_message",
    [
        (  # Both operation and modifiers mode fields set
            {
                "operation_id": "getItems",
                "modifiers": [{"op": "set", "param": "page", "value": "2"}],
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "Cannot use 'operation_id' or 'parameters' with 'reuse_previous_request' or 'modifiers'",
        ),
        (  # Both parameters and reuse_previous_request set
            {
                "parameters": [{"name": "page", "value": "2"}],
                "reuse_previous_request": True,
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "Cannot use 'operation_id' or 'parameters' with 'reuse_previous_request' or 'modifiers'",
        ),
        (  # Parameters without operation_id in operation mode
            {
                "parameters": [{"name": "page", "value": "2"}],
                "result": "$response.body#/items",
                "has_more": "$response.body#/hasMore",
            },
            "'operation_id' is required in operation mode.",
        ),
    ],
)
def test_pagination_description_mutually_exclusive_modes(invalid_data, error_message):
    """Tests that mutually exclusive fields raise ValidationError."""
    with pytest.raises(ValidationError) as e:
        PaginationDescription(**invalid_data)

    assert error_message in str(e.value)
