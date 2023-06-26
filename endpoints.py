from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List

from openapi import Definition
from utils import get_multi_key

if TYPE_CHECKING:
    from tree import APINode


@dataclass
class EndpointParameter:
    """
    Defines a parameter used by an endpoint.
    """
    name: str
    in_location: str  # "query", "header", "path" or "cookie".
    type: str
    required: bool = False
    format: str = ""

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
    parameters: List[EndpointParameter] = field(default_factory=list)
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
    parameters: List[EndpointParameter] = field(default_factory=list)  # Only path parameters
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
    definition: Definition = None

    @property
    def methods(self):
        return self.layers[-1].methods


def parse_endpoint(path: str, definition: Definition = None) -> Endpoint:
    endpoint = Endpoint(path=path, definition=definition)
    split_endpoint_layers(endpoint)
    # parse_parameters(endpoint)
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
            param = EndpointParameter(name=p[1:len(p) - 1],
                                      in_location="path",
                                      type="string",
                                      required=True)
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


def parse_parameters(endpoint: Endpoint):
    _ALLOWED_OPERATIONS = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]

    parameters = {}  # type: dict[tuple, EndpointParameter]

    path_config = endpoint.definition.paths[endpoint.path]

    if 'parameters' in path_config:
        for p in path_config['parameters']:
            parameter = parse_parameter(endpoint.definition, p)
            parameters[(parameter.in_location, parameter.name)] = parameter

    for operation_name in path_config:
        if operation_name.lower() not in _ALLOWED_OPERATIONS:
            continue

        operation = path_config[operation_name]
        op_parameters = parameters.copy()

        if 'parameters' in operation:
            for p in operation['parameters']:
                parameter = parse_parameter(endpoint.definition, p)
                op_parameters[(parameter.in_location, parameter.name)] = parameter

        endpoint.methods.append(EndpointMethod(
            name=operation_name.lower(),
            parameters=list(op_parameters.values())
        ))

    return None


def parse_parameter(definition: Definition, parameter_info: dict) -> EndpointParameter:
    info = parameter_info
    if '$ref' in info:
        info = definition.solve_ref(info['$ref'])

    return EndpointParameter(
        name=info['name'],
        in_location=info['in'],
        type=get_multi_key(info, 'schema.type', default='string'),
        required=info['required'] if info['in'] != 'path' else True,
        format=info.get('format', ''),
    )
