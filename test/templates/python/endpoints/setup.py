from build import build
from utils.path import abs_path_from_current_script

built = False


def build_client():
    global built
    filename = abs_path_from_current_script('../../../definitions/companies_api.yaml')
    output_path = abs_path_from_current_script('./_build')
    build(filename, output_path)
    built = True
