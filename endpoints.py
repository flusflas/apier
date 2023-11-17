from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Tuple

from consts import NO_RESPONSE_ID
from openapi import Definition
from utils.dicts import get_multi_key
from utils.strings import to_pascal_case

if TYPE_CHECKING:
    from tree import APINode

_ALLOWED_OPERATIONS = ["get", "put", "post", "delete", "options", "head", "patch", "trace"]


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
    description: str = ""

    def __hash__(self):
        return hash(repr(self))


@dataclass
class ContentSchema:
    """
    Defines a content schema used by an endpoint.
    """
    name: str
    content_type: str = ''
    definition: dict = None
    code: int = 0
    is_inline: bool = False


@dataclass
class EndpointMethod:
    """
    Defines a method used by an endpoint (e.g. GET, POST...).
    """
    name: str
    description: str
    parameters: List[EndpointParameter] = field(default_factory=list)
    request_schemas: List[ContentSchema] = field(default_factory=list)
    response_schemas: List[ContentSchema] = field(default_factory=list)

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

    def get_method(self, method_name: str) -> EndpointMethod | None:
        for method in self.methods:
            if method.name == method_name:
                return method
        return None


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


_schemas = {}


def init_schemas(definition: Definition):
    """
    Initializes the dictionary of schemas with the ones defined in the given
    OpenAPI definition under the 'components.schemas' section.
    """
    clear_schemas()
    schemas = definition.get_value('components.schemas', default={})
    for schema_name, schema_def in schemas.items():
        _schemas[schema_name] = ContentSchema(
            name=schema_name,
            definition=schema_def,
        )


def get_schemas():
    """
    Returns the dictionary of schemas.
    """
    return _schemas


def clear_schemas():
    """
    Clears the dictionary of schemas.
    """
    global _schemas
    _schemas = {}


def parse_endpoint(path: str, definition: Definition = None) -> Endpoint:
    endpoint = Endpoint(path=path, definition=definition)
    split_endpoint_layers(endpoint)
    if definition is not None:
        parse_parameters(endpoint)
        parse_content_schemas(endpoint)
    return endpoint


def split_endpoint_layers(endpoint: Endpoint):
    """
    Splits the path of the given Endpoint into all their layers and adds them
    to the instance.
    """
    path_levels = endpoint.path.split("/")

    # TODO: Review special cases (e.g. empty endpoints, trailing slash...)
    path_levels = path_levels[1:]

    endpoint_layer = EndpointLayer(path='')

    for i, p in enumerate(path_levels):
        if len(p) == 0:
            continue
        elif re.match(r'^{.+}$', p):
            param_name = p[1:len(p) - 1]
            endpoint_layer.path += f"/{p}"
            param, _ = get_first_endpoint_param(endpoint, param_name, 'path')
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


def get_first_endpoint_param(endpoint: Endpoint, param_name: str,
                             in_location: str) -> Tuple[EndpointParameter, bool]:
    """
    Return an EndpointParameter with the information of the first parameter
    found in an endpoint that matches the given name and location.
    If the Endpoint doesn't have an OpenAPI definition or the parameter is not
    found, a basic EndpointParameter instance will be returned with the given
    information.

    :param endpoint:    The Endpoint to search for the parameter.
    :param param_name:  The parameter name.
    :param in_location: The location of the parameter (path, query...).
    :return: The parameter information and a boolean value indicating whether
             the parameter description has been found in the endpoint definition.
    """
    schema_found = False
    param_schema = {}
    if endpoint.definition is not None:
        for key, value in endpoint.definition.paths[endpoint.path].items():
            if schema_found:
                break

            if key != "parameters" and key not in _ALLOWED_OPERATIONS:
                continue

            if key in _ALLOWED_OPERATIONS:
                if 'parameters' in value:
                    value = value['parameters']
                else:
                    continue

            for schema_def in value:
                if '$ref' in schema_def:
                    schema_def = endpoint.definition.solve_ref(schema_def['$ref'])
                if schema_def.get('in') == in_location and schema_def.get('name') == param_name:
                    param_schema = schema_def
                    schema_found = True
                    break

    return EndpointParameter(
        name=param_name,
        description=param_schema.get('description', ''),
        in_location=in_location,
        type=get_multi_key(param_schema, 'schema.type', default='string'),
        required=param_schema.get('required', False) if in_location != 'path' else True,
        format=param_schema.get('format', ''),
    ), schema_found


def parse_parameters(endpoint: Endpoint):
    """
    Parses all the request parameters of the given Endpoint and adds them
    to the instance.
    """
    parameters = {}  # type: dict[tuple, EndpointParameter]
    path_config = endpoint.definition.paths[endpoint.path]

    if 'parameters' in path_config:
        for p in path_config['parameters']:
            parameter = parse_parameter(endpoint.definition, p)
            parameters[(parameter.in_location, parameter.name)] = parameter

    for operation_name, operation in path_config.items():
        if operation_name.lower() not in _ALLOWED_OPERATIONS:
            continue

        op_parameters = parameters.copy()

        if 'parameters' in operation:
            for p in operation['parameters']:
                parameter = parse_parameter(endpoint.definition, p)
                op_parameters[(parameter.in_location, parameter.name)] = parameter

        endpoint.methods.append(EndpointMethod(
            name=operation_name.lower(),
            description=operation.get("description"),
            parameters=list(op_parameters.values())
        ))

    return None


def parse_parameter(definition: Definition, parameter_info: dict) -> EndpointParameter:
    """
    Parses a parameter definition.

    :param definition: The OpenAPI definition.
    :param parameter_info: The parameter definition.
    :return: An EndpointParameter with the parameter information.
    """
    info = parameter_info
    if '$ref' in info:
        info = definition.solve_ref(info['$ref'])

    return EndpointParameter(
        name=info['name'],
        description=info.get('description', ""),
        in_location=info['in'],
        type=get_multi_key(info, 'schema.type', default='string'),
        required=info.get('required', False) if info['in'] != 'path' else True,
        format=info.get('format', ''),
    )


def parse_content_schemas(endpoint: Endpoint):
    """
    Parses the content schemas of the given Endpoint and adds them
    to the instance.
    """
    path_config = endpoint.definition.paths[endpoint.path]

    for operation_name, operation in path_config.items():
        if operation_name.lower() not in _ALLOWED_OPERATIONS:
            continue

        req_schemas = []
        req_definition = get_multi_key(operation, 'requestBody.content', '.', {})
        for content_type, content_type_definition in req_definition.items():
            schema = content_type_definition.get('schema', {})
            req_schemas.append(parse_schema(endpoint, operation_name,
                                            schema, content_type))

        resp_schemas = []
        resp_definition = operation.get('responses', {})
        for resp_code, resp_definition in resp_definition.items():
            resp_code = int(resp_code)
            resp_definition = resp_definition.get('content', {})
            for content_type, content_type_definition in resp_definition.items():
                schema = content_type_definition.get('schema', {})
                resp_schemas.append(parse_schema(endpoint, operation_name, schema,
                                                 content_type, resp_code))

            if len(resp_definition) == 0:
                resp_schemas.append(ContentSchema(
                    name=NO_RESPONSE_ID,
                    code=resp_code,
                    content_type='',
                    definition=resp_definition,
                    is_inline=True,
                ))

        method = endpoint.layers[-1].get_method(operation_name)
        method.request_schemas = req_schemas
        method.response_schemas = resp_schemas


def parse_schema(endpoint: Endpoint, operation_name: str,
                 schema_def: dict, content_type: str,
                 resp_code: int = 0) -> ContentSchema:
    """
    Parses a content schema and inserts it to the global dictionary of schemas
    if it's missing.

    If the given schema is defined inline, the name will be taken from the
    'title' attribute. Otherwise, the name will be generated based on the
    'type' attribute.

    :param endpoint: The Endpoint where the schema is used.
    :param operation_name: Name of the endpoint operation.
    :param schema_def: Schema definition.
    :param content_type: Content type of the request/response.
    :param resp_code: Response code returned (omitted for requests).
    :return: A ContentSchema with the content schema information.
    """
    if not _schemas:
        init_schemas(endpoint.definition)

    is_inline = False
    if '$ref' in schema_def:
        schema_name = schema_def['$ref'].split('/')[-1]
        schema_def = endpoint.definition.solve_ref(schema_def['$ref'])
    else:
        is_inline = True
        schema_name = schema_def.get('title')
        if schema_name:
            if schema_name in _schemas:
                raise Exception(f"Schema name '{schema_name}' is already taken")
        else:
            schema_name = schema_def.get('type', 'string')

    schema_name = to_pascal_case(schema_name)

    # Generate a new schema name if the current is already taken
    i = 1
    original_schema_name = schema_name
    while is_inline and schema_name in _schemas:
        # An identical schema already exists
        if _schemas[schema_name].definition == schema_def:
            if content_type == _schemas[schema_name].content_type:
                return _schemas[schema_name]
            else:
                return ContentSchema(
                    name=schema_name,
                    code=resp_code,
                    content_type=content_type,
                    definition=schema_def,
                    is_inline=is_inline,
                )

        # Rename schema
        i += 1
        schema_name = to_pascal_case(original_schema_name + str(i))

    _schemas[schema_name] = ContentSchema(
        name=schema_name,
        code=resp_code,
        content_type=content_type,
        definition=schema_def,
        is_inline=is_inline,
    )
    return _schemas[schema_name]
