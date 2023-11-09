import sys

import yaml

from endpoints import parse_endpoint
from openapi import Definition
from renderer import render_api
from tree import build_endpoints_tree


def build(filename):
    with open(filename) as f:
        spec = yaml.safe_load(f.read())

    definition = Definition(spec)
    endpoints = []
    for path in definition.paths:
        endpoints.append(parse_endpoint(path, definition))

    api_tree = build_endpoints_tree(endpoints)
    render_api('python', definition, api_tree)


if __name__ == '__main__':
    build(sys.argv[1])
