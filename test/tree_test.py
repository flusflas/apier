import random
from uuid import UUID
from typing import List
from unittest.mock import patch

import pytest

from .expected_data import expected_tree_repr


def _predictive_uuid():
    rd = random.Random()
    rd.seed(0)
    return lambda: UUID(int=rd.getrandbits(128))


with patch('uuid.uuid4', new=_predictive_uuid()):
    from endpoints import Endpoint, parse_endpoint
    from openapi import Definition
    from tree import build_endpoints_tree

openapi_definition = Definition.load('definitions/companies_api.yaml')


@pytest.fixture
def endpoints() -> List[Endpoint]:
    ee = []
    for path in openapi_definition.paths:
        ee.append(parse_endpoint(path, openapi_definition))
    return ee


def test_build_endpoints_tree(endpoints):
    """
    Tests building an API tree from a list of endpoints.
    """
    tree = build_endpoints_tree(endpoints)

    assert repr(tree) == expected_tree_repr

    assert len(tree.branches) == 1
    assert tree.branches[0].api == 'companies'

    companies_node = tree.branches[0]

    # Layer /companies
    assert len(companies_node.layers) == 3
    assert companies_node.layers[0].path == '/companies'
    assert len(companies_node.layers[0].next) == 0

    # Layer /companies/{company_id}
    assert companies_node.layers[1].path == '/companies/{company_id}'
    assert len(companies_node.layers[1].next) == 2
    assert len(companies_node.layers[1].next[0].layers) == 2
    assert companies_node.layers[1].next[0].api == 'employees'
    assert companies_node.layers[1].next[0] == companies_node.next.branches[0]
    assert companies_node.layers[1].next[1].api == 'departments'
    assert companies_node.layers[1].next[1] == companies_node.next.branches[1]

    # Layer /companies/{company_id}/{number}'
    assert companies_node.layers[2].path == '/companies/{company_id}/{number}'
    assert len(companies_node.layers[2].next) == 0
