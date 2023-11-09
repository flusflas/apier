import os
import shutil

from jinja2 import Environment, FileSystemLoader

from openapi import Definition
from templates.python.functions import get_type, get_params_by_location
from tree import APINode, APITree


def render(definition: Definition, api_tree: APITree):
    if os.path.exists('_build'):
        shutil.rmtree('_build')
    shutil.copytree('templates/python/base', '_build')

    render_api_file(definition, api_tree)
    render_api_components(api_tree)


def render_api_file(definition: Definition, api_tree: APITree):
    filename = "_build/api.py"
    environment = Environment(loader=FileSystemLoader("templates/python/"),
                              trim_blocks=True, lstrip_blocks=True)
    template = environment.get_template("api_template.jinja")
    content = template.render(
        openapi=definition.definition,
        root_branches=api_tree.branches,
    )
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)

    format_file(filename)


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
        eq_type_func=get_type,
        get_params_by_location=get_params_by_location,
    )
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(content)

    format_file(filename)
    print("OK")


def format_file(filename):
    os.system(f"autopep8 --max-line-length 119 --in-place --aggressive --aggressive {filename}")
    # os.system(f"autoflake --in-place {filename}")
    os.system(f"isort -q {filename}")
