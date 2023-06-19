from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from openapi import Definition

if TYPE_CHECKING:
    from tree import APINode


@dataclass
class EndpointParameter:
    """
    Defines a parameter used by an endpoint.
    """
    name: str
    type: str
    required: bool = False

    # kind: str   TODO: path, query, header...

    def __hash__(self):
        return hash(repr(self))


@dataclass
class ContentSchema:
    """
    Defines a content schema used by an endpoint.
    """
    name: str
    content_type: str
    definition: dict
    code: int = 0


@dataclass
class EndpointMethod:
    """
    Defines a method used by an endpoint (e.g. GET, POST...).
    """
    name: str
    request_schemas: List[ContentSchema] = field(default_factory=list)
    response_schemas: List[ContentSchema] = field(default_factory=list)
    # kind: str   TODO: path, query, header...

    def __hash__(self):
        return hash(repr(self))


@dataclass
class EndpointLayer:
    """
    Defines a layer/level that is part of an endpoint.

    For example, the endpoint "/stores/{store_id}/products/{product_id}"
    consists of two layers: "/stores/{store_id}" and "products/{product_id}".
    """
    path: str
    api_levels: List[str] = field(default_factory=list)
    parameters: List[EndpointParameter] = field(default_factory=list)
    next: List[APINode] = field(default_factory=list)
    methods: List[EndpointMethod] = field(default_factory=list)
    _id: uuid.UUID = field(default_factory=uuid.uuid4, compare=False)

    def param_names(self):
        return [p.name for p in self.parameters]

    def param_types(self):
        return [p.type for p in self.parameters]


@dataclass
class Endpoint:
    """
    Defines an API endpoint.
    """
    path: str
    layers: List[EndpointLayer] = field(default_factory=list)
    definition: dict = field(default_factory=dict)


def parse_endpoint(path: str, definition: Definition = None) -> Endpoint:
    if definition is not None:
        endpoint_definition = definition.paths[path]
    else:
        endpoint_definition = {}

    endpoint = Endpoint(path=path, definition=endpoint_definition)
    split_endpoint_layers(endpoint)
    return endpoint


def split_endpoint_layers(endpoint: Endpoint):
    path_levels = endpoint.path.split("/")

    # TODO: Review special cases (e.g. empty endpoints, trailing slash...)
    path_levels = path_levels[1:]

    endpoint_layer = EndpointLayer(path='')

    for i, p in enumerate(path_levels):
        if len(p) == 0:
            continue
        elif re.match(r'^{.+}$', p):
            endpoint_layer.path += f"/{p}"
            param = EndpointParameter(name=p[1:len(p) - 1], type="string")
            endpoint_layer.parameters.append(param)
        elif p.startswith("{") or p.endswith("}"):
            raise Exception("wrong parameter format in path")
        else:
            if i > 0:
                endpoint.layers.append(endpoint_layer)
            endpoint_layer = EndpointLayer(path='')
            endpoint_layer.path += f"/{p}"
            endpoint_layer.api_levels.append(p)

    endpoint.layers.append(endpoint_layer)
