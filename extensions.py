from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from templates.python.base.models.pagination import PaginationDescription

if TYPE_CHECKING:
    from endpoints import Endpoint


class Extensions(BaseModel):
    class Config:
        allow_population_by_field_name = True

    pagination: Pagination = Field(default=None, alias='x-pagination')


class Pagination(BaseModel):
    next: PaginationDescription


Extensions.update_forward_refs()


def parse_extensions(endpoint: Endpoint):
    for method in endpoint.methods:
        endpoint_def = endpoint.definition.paths[endpoint.path][method.name]
        extensions_def = {k: v for k, v in endpoint_def.items() if k.lower().startswith('x-')}
        if not extensions_def:
            continue
        method.extensions = Extensions.parse_obj(extensions_def)
