from importlib import import_module

from openapi import Definition
from tree import APITree


def render_api(template: str, definition: Definition, schemas: dict,
               api_tree: APITree):
    try:
        render = import_module(f"templates.{template}.renderer").render
    except ModuleNotFoundError:
        raise ValueError(f"Template '{template}' not found")

    render(definition, schemas, api_tree)
