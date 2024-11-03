import os
from importlib import import_module

from endpoints import Endpoint
from openapi import Definition


def render_api(ctx, template: str, definition: Definition, schemas: dict,
               endpoints: list[Endpoint], output_path: str):
    """ Render the API client using the specified template. """

    if ctx is None:
        ctx = {
            'verbose': False,
            'output_logger': print
        }

    if not os.path.isabs(output_path):
        output_path = os.path.normpath(os.path.join(os.getcwd(), output_path))

    try:
        renderer = (import_module(f"templates.{template}.renderer").
                    Renderer(ctx, definition, schemas, endpoints, output_path))
    except ModuleNotFoundError:
        raise ValueError(f"Template '{template}' not found")

    renderer.render()
