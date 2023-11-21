import os
import shutil

from jinja2 import Environment, FileSystemLoader
from openapi import Definition
from tree import APINode, APITree
from utils.dicts import get_multi_key

from templates.python.functions import get_params_by_location, get_type_hint
from templates.python.gen_models import generate_models


def render(definition: Definition, schemas: dict, api_tree: APITree):
    if os.path.exists('_build'):
        shutil.rmtree('_build')
    shutil.copytree('templates/python/base', '_build')

    generate_models(definition, schemas)
    render_api_file(definition, api_tree)
    render_api_components(api_tree)

    format_file("_build/")


def render_api_file(definition: Definition, api_tree: APITree):
    filename = "_build/api.py"
    environment = Environment(loader=FileSystemLoader("templates/python/"),
                              trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template("api_template.jinja")
    content = template.render(
        openapi=definition.definition,
        server_url=get_multi_key(definition.definition, 'servers.0.url', default=None),
        root_branches=api_tree.branches,
        raise_errors=bool(definition.get_value('info.x-api-gen.templates.python.raise-response-errors',
                                               default=True)),
    )
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)


def render_api_components(api_tree: APITree):
    for api in api_tree.branches:
        if api.next is not None:
            render_api_components(api.next)
        render_api_component(api)


def render_api_component(api_node: APINode):
    filename = f"_build/{api_node.api}.py"
    print(f"Rendering {filename}... ", end="")

    environment = Environment(loader=FileSystemLoader("templates/python/"),
                              trim_blocks=True, lstrip_blocks=True)

    template = environment.get_template("node_template.jinja")

    # Sort layers by number of parameters
    api_node.layers.sort(key=lambda p: len(p.parameters), reverse=True)

    has_layer_without_params = any(len(p.parameters) == 0 for p in api_node.layers)
    optional_param_names = [p.name for i, p in enumerate(api_node.params_set())
                            if len(api_node.layers) > 1 and i > 0 or has_layer_without_params]

    # TODO: Handle APIs with the same name
    content = template.render(
        api_node=api_node,
        class_id_name=api_node.api.capitalize(),
        optional_param_names=optional_param_names,
        has_layer_without_params=has_layer_without_params,
        get_type_hint=get_type_hint,
        get_params_by_location=get_params_by_location,
    )
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)

    print("OK")


def format_file(filename):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ruff.toml')

    os.system(f"ruff --config {config_file} check {filename} --fix -q")
    os.system(f"ruff --config {config_file} format {filename} -q")
    pass
