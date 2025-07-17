# Templates

## Overview
Templates in apier define how client libraries are generated from OpenAPI specifications. They control the structure, interface, and programming language of the output code, allowing you to adapt the generated client to your project's requirements or coding standards.

## How Templates Work

Templates in apier are Python packages that define how the client code is generated.

- **Selecting a Template:**
  - Use the `--template` option to select a built-in template.
  - Use the `--custom-template` option to specify the path to a custom template directory.

- **Renderer Class:**
  - The `Renderer` class receives arguments such as parsed OpenAPI endpoints, schemas, the output directory, and other relevant data.
  - The `render()` method is responsible for generating the output files for the client library.

- **Rendering Logic:**
  - It's up to the `Renderer` class how to implement the logic for generating files based on the provided OpenAPI specification.
  - Files can be rendered using Jinja2 templates, other tools, or custom code.

This flexible approach allows you to fully control the structure and style of the generated client code.

## Built-in Templates

Currently, there is one built-in template available:

- **python-tree**: Generates Python client libraries with a hierarchical, chainable method structure that reflects the organization of REST API endpoints. [See details and usage examples.](python_tree.md)

Other built-in templates will be added in the future.

## Creating a New Template
To create a new template, create a Python package with a `renderer.py` file that defines a `Renderer` class. This class must implement the `render()` method, which will handle the logic for generating the client library files based on the provided inputs.

How the `Renderer` class is implemented is up to you, but it should typically include methods for processing the OpenAPI endpoints and schemas, and generating the necessary files in the specified output directory using tools like Jinja2 for templating or custom logic.

**Minimal example of renderer.py:**
```python
class Renderer:
    def __init__(self, ctx: dict, definition: 'Definition', schemas: dict,
                 endpoints: list['Endpoint'], output_path: str):
        self.ctx = ctx
        self.definition = definition
        self.schemas = schemas
        self.endpoints = endpoints
        self.output_path = output_path
        # Other initialization logic ...

    def render(self):
        # Implement your rendering logic here
        pass
```

For more details on template arguments and advanced usage, refer to the main documentation or explore existing templates.

## Authentication

Templates are responsible for generating the necessary authentication code based on the OpenAPI specification. This includes handling security schemes like API keys, OAuth2, and basic authentication.
