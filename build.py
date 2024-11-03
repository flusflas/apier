from typing import Union, List

from endpoints import EndpointsParser
from merge import merge_spec_files
from openapi import Definition
from renderer import render_api


def build(ctx, filename: Union[str, List], output_path='_build/'):
    """
    Build the API client from the given OpenAPI file(s).

    :param filename: The OpenAPI file(s) to use.
    :param output_path: The output directory.
    """
    if isinstance(filename, str):
        definition = Definition.load(filename)
    elif len(filename) == 1:
        definition = Definition.load(filename[0])
    else:
        merged_spec = merge_spec_files(*filename)
        definition = Definition(merged_spec)

    parser = EndpointsParser(definition)

    endpoints = []
    for path in definition.paths:
        endpoints.append(parser.parse_endpoint(path))

    render_api(ctx, 'python', definition, parser.schemas, endpoints, output_path)
