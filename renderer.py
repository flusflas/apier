from importlib import import_module

from openapi import Definition
from tree import APITree


def render_api(template: str, definition: Definition, schemas: dict,
               api_tree: APITree):
    try:
        renderer = import_module(f"templates.{template}.renderer").Renderer()
    except ModuleNotFoundError:
        raise ValueError(f"Template '{template}' not found")

    renderer.render(definition, schemas, api_tree)
