import os
import shutil

from jinja2 import Environment, FileSystemLoader
from openapi import Definition
from tree import APINode, APITree
from utils.dicts import get_multi_key
from utils.strings import to_pascal_case, to_snake_case

from templates.python.functions import get_type_hint
from templates.python.gen_models import generate_models


class Renderer:
    """
    Renderer class that builds a Python API client using a method chaining style,
    allowing seamless access to the endpoints by mirroring the structure of the
    target API endpoint.

    For instance, a "/companies/{company_id}/employees/{employee_id}" endpoint
    could be called using `api.companies(company_id).employees(employee_id)`.
    """

    def __init__(self, definition: Definition, schemas: dict, api_tree: APITree,
                 output_path: str):
        self.definition = definition
        self.schemas = schemas
        self.api_tree = api_tree
        self.output_path = output_path.rstrip('/')
        self.api_names = {}

    def render(self):
        self.api_names = {}

        if os.path.exists(self.output_path):
            # TODO: Ask before removing
            shutil.rmtree(self.output_path)
        shutil.copytree('templates/python/base', self.output_path)

        generate_models(self.definition, self.schemas, self.output_path)
        self.render_api_components()
        self.render_api_file()

        format_file(self.output_path)

    def render_api_file(self):
        filename = f"{self.output_path}/api.py"
        environment = Environment(loader=FileSystemLoader("templates/python/"),
                                  trim_blocks=True, lstrip_blocks=True)

        environment.filters['snake_case'] = to_snake_case
        environment.filters['pascal_case'] = to_pascal_case
        environment.filters['api_name'] = self.get_api_name

        template = environment.get_template("api_template.jinja")
        content = template.render(
            openapi=self.definition.definition,
            server_url=get_multi_key(self.definition.definition, 'servers.0.url', default=None),
            root_branches=self.api_tree.branches,
            raise_errors=bool(self.definition.get_value('info.x-api-gen.templates.python.raise-response-errors',
                                                        default=True)),
        )
        with open(filename, mode="w", encoding="utf-8") as message:
            message.write(content)

    def render_api_components(self):
        nodes_processed = set()
        stack = [self.api_tree]

        while stack:
            current_tree = stack.pop()
            for api in current_tree.branches:
                if api.next is not None:
                    stack.append(api.next)
                if id(api) not in nodes_processed:
                    self.render_api_component(api)
                    nodes_processed.add(id(api))

    def get_api_name(self, api_node: APINode) -> str:
        """
        Returns a unique name for the given API node.
        """
        reserved_names = ['models', 'internal']

        api_name = self.api_names.get(id(api_node))
        if api_name:
            return api_name

        api_name = api_node.api
        i = 0
        while api_name in list(self.api_names.values()) + reserved_names:
            i += 1
            api_name = api_node.api + str(i)

        self.api_names[id(api_node)] = api_name
        return api_name

    def render_api_component(self, api_node: APINode):
        api_filename = to_snake_case(self.get_api_name(api_node))
        filename = f"{self.output_path}/{api_filename}.py"
        print(f"Rendering {filename}... ", end="")

        environment = Environment(loader=FileSystemLoader("templates/python/"),
                                  trim_blocks=True, lstrip_blocks=True)

        environment.filters['snake_case'] = to_snake_case
        environment.filters['pascal_case'] = to_pascal_case
        environment.filters['api_name'] = self.get_api_name

        template = environment.get_template("node_template.jinja")

        # Sort layers by number of parameters
        api_node.layers.sort(key=lambda p: len(p.parameters), reverse=True)

        has_layer_without_params = any(len(p.parameters) == 0 for p in api_node.layers)
        optional_param_names = [p.name for i, p in enumerate(api_node.params_set())
                                if len(api_node.layers) > 1 and i > 0 or has_layer_without_params]

        content = template.render(
            api_node=api_node,
            optional_param_names=optional_param_names,
            has_layer_without_params=has_layer_without_params,
            get_type_hint=get_type_hint,
        )
        with open(filename, mode="w", encoding="utf-8") as message:
            message.write(content)

        print("OK")


def format_file(filename):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ruff.toml')

    os.system(f"ruff --config {config_file} check {filename} --fix -q")
    os.system(f"ruff --config {config_file} format {filename} -q")
