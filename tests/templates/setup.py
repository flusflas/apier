import inspect
import os

from apier.core.build import build
from apier.utils.path import abs_path_from_current_script

built = False


def build_client(template: str, definition_file: str):
    global built
    ctx = {}
    filename = abs_path_from_current_script(f"../definitions/{definition_file}")

    # Get the parent directory of the script that calls this function
    caller_path = os.path.dirname(inspect.stack()[1].filename)
    output_path = os.path.join(caller_path, "_build")
    build(ctx, template, filename, output_path)
    built = True
