from __future__ import annotations

import itertools
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import List

from endpoints import EndpointLayer, parse_endpoint, Endpoint


class PathNotFoundException(Exception):
    pass


@dataclass
class APITree:
    """
    A tree of APINode instances that connects the layers of all the endpoints
    of an API.
    """
    branches: List[APINode] = field(default_factory=list)

    def node(self, api_level: str) -> APINode | None:
        """
        Returns the node of the tree with the given API level, or None if it is
        not found.

        :param api_level: Name of the API level.
        :return: Node of the tree with the given API level, or None if the level
                 is not found.
        """
        for node in self.branches:
            if node.api == api_level:
                return node
        return None

    def search_path(self, search_path: str) -> (APITree, APINode, EndpointLayer):
        """
        Searches in the tree for the branch that matches the given path, and
        returns the tree, node and endpoint layer of the match.

        :param search_path: The endpoint path to search for in the tree.
        :raises PathNotFoundException: The path was not found in the tree.
        :return: The tree, node and endpoint layer found in the tree.
        """
        search_endpoint = parse_endpoint(search_path)

        accumulated_path = ""
        tree = self
        for search_layer in search_endpoint.layers:
            accumulated_path += search_layer.path
            node_matched = False
            for node in tree.branches:
                if node_matched:
                    break
                for layer in node.layers:
                    if layer.path == search_layer.path:
                        if accumulated_path.startswith(search_path):
                            return tree, node, layer
                        tree = node.next
                        node_matched = True
                        break

        raise PathNotFoundException("path not found in api tree")


@dataclass
class APINode:
    """
    Defines a node of an APITree.
    """
    api: str
    layers: List[EndpointLayer] = field(default_factory=list)
    next: APITree = field(default_factory=APITree)
    _id: str = field(default_factory=uuid.uuid4)

    def params_set(self):
        """
        Returns all the layer params in a flat list without duplicates.
        """
        params = itertools.chain(*(p.parameters for p in self.layers))
        return list(OrderedDict.fromkeys(params))


def build_endpoints_tree(endpoints: List[Endpoint]) -> APITree:
    """
    Builds an APITree from the given list of endpoints.

    :param endpoints: List of Endpoint instances to build the tree.
    :return: An API tree built from the given list of endpoints.
    """
    api_tree = APITree()

    if len(endpoints) == 0:
        return api_tree

    config = endpoints[0].definition.get_value('info.x-api-gen', '.', {})

    for e in endpoints:
        _build_recursive(api_tree, api_tree, e.layers, config)

    return api_tree


def _build_recursive(api_tree: APITree,
                     current_tree: APITree,
                     layers: List[EndpointLayer],
                     config: dict,
                     current_path: str = "") -> APINode | None:
    if len(layers) == 0:
        return None

    layer = layers[0]
    current_path += layer.path
    if len(layer.api_levels) == 0:
        # TODO
        # raise Exception("this layer does not have an api level!")
        return None

    equivalent_paths = config.get('equivalent_paths', [])
    for eq_path in equivalent_paths:
        if current_path.startswith(eq_path["source"]):
            eq_path = current_path.replace(eq_path["source"], eq_path["target"])
            try:
                tree, node, _ = api_tree.search_path(eq_path)
                current_tree.branches.append(node)
                current_tree = tree
                break
            except PathNotFoundException:
                raise PathNotFoundException("equivalent endpoint not found in tree")

    api_level = layer.api_levels[0]
    node = current_tree.node(api_level)

    if node is not None:
        p = next((p for p in node.layers if p.path == layer.path), None)
        if p is None:
            node.layers.append(layer)
        else:
            layer = p
    else:
        node = APINode(api=api_level, layers=[layer])
        current_tree.branches.append(node)

    if len(layers[1:]) > 0:
        next_node = _build_recursive(api_tree, node.next, layers[1:], config, current_path)
        if next_node is not None:
            if next_node not in layer.next:
                layer.next.append(next_node)
            # if next_node not in current_tree.branches:
            #     current_tree.branches.append(next_node)

    return node
