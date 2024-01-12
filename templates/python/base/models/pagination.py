from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator


@dataclass
class _PaginationHelper:
    supported: bool = False
    results_attribute: str = ''
    results: list = None
    iter_idx: int = 0
    iter_func: callable = None


@dataclass
class Paginator:
    """
    This class allows to paginate the results of an API response instance.
    """
    _pagination: _PaginationHelper = field(default_factory=_PaginationHelper,
                                           compare=False)

    def __iter__(self):
        self._pagination.iter_idx = 0
        return self

    def __next__(self) -> bool:
        results = self._pagination.results
        if self._pagination.iter_idx >= len(results):
            if self._pagination.iter_func:
                current_data = getattr(self, self._pagination.results_attribute)
                next_results = self._pagination.iter_func()
                self._pagination.iter_func = next_results._pagination.iter_func
                current_data.extend(getattr(next_results, self._pagination.results_attribute))

        if self._pagination.iter_idx >= len(results):
            raise StopIteration

        i = self._pagination.iter_idx
        self._pagination.iter_idx = self._pagination.iter_idx + 1
        return results[i]


class PaginationDescription(BaseModel):
    class Config:
        allow_population_by_field_name = True

    reuse_previous_request: bool = Field(default=False, alias='reuse-previous-request')
    method: str = ''
    url: str = ''
    modifiers: List[PaginationModifier] = Field(default_factory=list)
    result: str
    has_more: str

    @root_validator
    def validate_fields(cls, values: dict):
        if isinstance(values, PaginationDescription):
            values = values.dict()
        reuse = values.get("reuse-previous-request") or values.get("reuse_previous_request")
        for attr in ['method', 'url']:
            if not reuse and not values[attr]:
                raise ValueError(f"The field '{attr}' is required if 'reuse-previous-request' is False")
        return values


class PaginationModifier(BaseModel):
    op: Optional[str] = 'set'
    param: str
    value: str


PaginationDescription.update_forward_refs()
