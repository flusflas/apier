from apier.core.build import build
from apier.utils.path import abs_path_from_current_script

built = False


def build_client(template: str):
    global built
    ctx = {}
    filename = abs_path_from_current_script("../../../definitions/companies_api.yaml")
    output_path = abs_path_from_current_script("./_build")
    build(ctx, template, filename, output_path)
    built = True
