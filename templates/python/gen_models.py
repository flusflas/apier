import copy
import os
import shutil
from pathlib import Path

import yaml

from endpoints import ContentSchema
from openapi import Definition


def generate_models(definition: Definition, schemas: dict[str, dict],
                    output_path: str):
    """
    Generate the Pydantic models for all the given schemas.

    :param definition:  The OpenAPI definition object.
    :param schemas:     The dictionary of schemas that will be generated as
                        models.
    :param output_path: The output directory.
    """
    openapi_output = copy.deepcopy(definition.definition)
    openapi_output['components'] = {'schemas': schemas}
    filename = f"{output_path}/_temp/schemas.yaml"

    file = Path(filename)
    file.parent.mkdir(parents=True, exist_ok=True)
    with file.open('w') as f:
        yaml.dump(openapi_output, f)

    os.system(f"datamodel-codegen --input {filename} --input-file-type openapi "
              f"--output {output_path}/models/models.py "
              f"--base-class .basemodel.APIBaseModel")

    shutil.rmtree(f'{output_path}/_temp')
