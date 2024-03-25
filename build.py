import sys

from endpoints import EndpointsParser
from openapi import Definition
from renderer import render_api
from tree import build_endpoints_tree


def build(filename, output_path='_build/'):
    definition = Definition.load(filename)

    parser = EndpointsParser(definition)

    endpoints = []
    for path in definition.paths:
        endpoints.append(parser.parse_endpoint(path))

    render_api('python', definition, parser.schemas, endpoints, output_path)


if __name__ == '__main__':
    build(sys.argv[1])
