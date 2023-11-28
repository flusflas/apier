import copy
import os
import shutil
from pathlib import Path

import yaml

from endpoints import ContentSchema
from openapi import Definition


def generate_models(definition: Definition, schemas: dict[str, ContentSchema],
                    output_path: str):
    """
    Generate the Pydantic models for all the given schemas.

    :param definition:  The OpenAPI definition object.
    :param schemas:     The dictionary of schemas that will be generated to
                        models.
    :param output_path: The output directory.
    """
    openapi_output = copy.deepcopy(definition.definition)
    definition_schemas = definition.get_value('components.schemas')

    for key, schema in schemas.items():
        definition_schemas[key] = schema.definition

    openapi_output['components'] = {'schemas': definition_schemas}

    filename = "_temp/schemas.yaml"

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open('w') as f:
        yaml.dump(openapi_output, f)

    os.system(f"datamodel-codegen --input {filename} --input-file-type openapi "
              f"--output {output_path}/models/models.py "
              f"--base-class .basemodel.APIBaseModel")

    shutil.rmtree('_temp')
