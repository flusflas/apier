import random
from typing import List

import pytest

from apier.core.api.endpoints import Endpoint, EndpointsParser, EndpointLayer
from apier.core.api.openapi import Definition
from apier.core.api.tree import build_endpoints_tree

openapi_definition = Definition.load('definitions/companies_api.yaml')


@pytest.fixture
def endpoints() -> List[Endpoint]:
    parser = EndpointsParser(openapi_definition)
    ee = []
    for path in openapi_definition.paths:
        ee.append(parser.parse_endpoint(path))
    return ee


@pytest.mark.parametrize("_", range(5))
def test_build_endpoints_tree(endpoints, _):
    """
    Tests building an API tree from a list of endpoints.
    """
    random.shuffle(endpoints)
    tree = build_endpoints_tree(endpoints)

    assert len(tree.branches) == 2
    assert tree.branches[0].api == 'companies'

    companies_node = tree.branches[0]

    # Layer /companies
    assert len(companies_node.layers) == 3
    assert companies_node.layers[1].path == '/companies'
    assert len(companies_node.layers[1].next) == 0

    # Layer /companies/{company_id}
    assert companies_node.layers[0].path == '/companies/{company_id}'
    assert len(companies_node.layers[0].next) == 2
    assert len(companies_node.layers[0].next[0].layers) == 2
    assert companies_node.layers[0].next[0].api == 'employees'
    assert companies_node.layers[0].next[0] == companies_node.next.branches[0]
    assert companies_node.layers[0].next[1].api == 'departments'
    assert companies_node.layers[0].next[1] == companies_node.next.branches[1]

    # Layer /companies/{company_id}/{number}'
    assert companies_node.layers[2].path == '/companies/{company_id}/{number}'
    assert len(companies_node.layers[2].next) == 0


def test_build_endpoints_tree_order():
    """
    Tests building an API tree from a list of endpoints with different order.
    """
    definition = Definition({
        'info': {
            'x-apier': {
                'equivalent_paths': [
                    {
                        'source': '/foo',
                        'target': '/bar/foo'
                    }
                ]
            }
        }
    })
    endpoint1 = Endpoint(
        path='/foo',
        layers=[
            EndpointLayer(
                path='/foo',
                api_levels=['foo']
            ),
        ],
        definition=definition,
    )

    endpoint2 = Endpoint(
        path='/bar/foo',
        layers=[
            EndpointLayer(
                path='/bar',
                api_levels=['bar']
            ),
            EndpointLayer(
                path='/foo',
                api_levels=['foo']
            ),
        ],
        definition=definition,
    )

    # Test for both endpoint orders
    for endpoints in [[endpoint1, endpoint2], [endpoint2, endpoint1]]:
        tree = build_endpoints_tree(endpoints)

        assert len(tree.branches) == 2

        assert tree.branches[0].api == 'bar'
        assert tree.branches[1].api == 'foo'
        assert tree.branches[0].next.branches[0] == tree.branches[1]
