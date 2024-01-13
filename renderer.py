import os
from importlib import import_module

from openapi import Definition
from tree import APITree


def render_api(template: str, definition: Definition, schemas: dict,
               api_tree: APITree, output_path: str):

    if not os.path.isabs(output_path):
        output_path = os.path.normpath(os.path.join(os.getcwd(), output_path))

    try:
        renderer = (import_module(f"templates.{template}.renderer").
                    Renderer(definition, schemas, api_tree, output_path))
    except ModuleNotFoundError:
        raise ValueError(f"Template '{template}' not found")

    renderer.render()
