from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from .input_parameters import InputParametersDescription
from templates.python.base.models.extensions.pagination import PaginationDescription
from .method_name import MethodNameDescription

if TYPE_CHECKING:
    from endpoints import Endpoint


class Extensions(BaseModel):
    class Config:
        allow_population_by_field_name = True

    pagination: Pagination = Field(default=None, alias='x-pagination')
    input_parameters: InputParametersDescription = Field(default=None, alias='x-input-parameters')
    method_name: MethodNameDescription = Field(default=None, alias='x-method-name')


class Pagination(BaseModel):
    next: PaginationDescription


Extensions.update_forward_refs()


def parse_extensions(endpoint: Endpoint):
    for method in endpoint.methods:
        endpoint_def = endpoint.definition.paths[endpoint.path][method.name]
        extensions_def = {k: v for k, v in endpoint_def.items() if k.lower().startswith('x-')}
        if not extensions_def:
            continue

        for extension_name, extension_def in extensions_def.items():
            if '$ref' in extension_def:
                extensions_def[extension_name] = endpoint.definition.solve_ref(extension_def['$ref'])

        method.extensions = Extensions.parse_obj(extensions_def)
