import sys

import yaml

from endpoints import parse_endpoint, get_schemas
from openapi import Definition
from renderer import render_api
from tree import build_endpoints_tree


def build(filename):
    definition = Definition.load(filename)
    endpoints = []
    for path in definition.paths:
        endpoints.append(parse_endpoint(path, definition))

    schemas = get_schemas()
    api_tree = build_endpoints_tree(endpoints)
    render_api('python', definition, schemas, api_tree, '_build/')


if __name__ == '__main__':
    build(sys.argv[1])
