import json
from functools import reduce
from typing import Union
from urllib.parse import urlparse, parse_qs

from requests import Response


class RuntimeExpressionError(Exception):
    """ Invalid runtime expression. """

    def __init__(self, *attrs, caused_by: Exception = None):
        super().__init__(*attrs)
        self.caused_by = caused_by


def decode_expression(expression: str, obj: Union[dict, Response]):
    """
    Decodes an OpenAPI runtime expression (https://swagger.io/docs/specification/links/).
    It also accepts a dot-separated expression to address an attribute of the
    response body.

    It raises a RuntimeExpressionError if the expression cannot be evaluated
    successfully.

    :param expression: An OpenAPI runtime expression or a dot-separated expression.
    :param obj:        The response on which the expression will be applied.
    :return:           The result of the evaluated expression.
    """
    try:
        expression = expression.strip()
        if expression.startswith('$'):
            return _decode_runtime_expression(expression, obj)

        if isinstance(obj, Response):
            obj = obj.json()

        if not isinstance(obj, dict):
            raise ValueError("Invalid dict response")

        return _get_from_dict(obj, expression)
    except RuntimeExpressionError as e:
        raise e
    except Exception as e:
        raise RuntimeExpressionError(caused_by=e)


def _decode_runtime_expression(expression: str, resp: Response):
    """
    Decodes the given runtime expression, according to
    https://swagger.io/docs/specification/links/.
    """
    def to_string(obj):
        return str(obj) if obj is not None else ''

    def get_query_string(param):
        parsed_url = urlparse(resp.request.url)
        query_params = parse_qs(parsed_url.query)
        value = query_params.get(param, [])
        if len(value) == 0:
            raise RuntimeExpressionError(f"Query parameter '{param}' not found")
        elif len(value) == 1:
            return value[0]
        else:
            return value

    expression_funcs = {
        '$url': lambda: resp.request.url,
        '$method': lambda: resp.request.method,
        '$request.query.*': lambda x: get_query_string(x),
        # TODO: '$request.path.*': lambda x: resp,
        '$request.header.*': lambda x: resp.request.headers.get(x),
        '$request.body': lambda: to_string(resp.request.body),
        '$request.body#*': lambda x: _get_from_dict(json.loads(resp.request.body), x, '/'),
        '$statusCode': lambda: resp.status_code,
        '$response.header.*': lambda x: resp.headers.get(x),
        '$response.body': lambda: resp.text,
        '$response.body#*': lambda x: _get_from_dict(resp.json(), x, '/'),
    }

    for expr, fn in expression_funcs.items():
        if expr.endswith('*'):
            expr_prefix = expr.rstrip('*')
            if expression.startswith(expr_prefix):
                return fn(expression[len(expr_prefix):])
        if expr == expression:
            return fn()

    raise RuntimeExpressionError("invalid runtime expression")


def _get_from_dict(d: dict, key: str, separator='.'):
    try:
        def get_item(a, b):
            if isinstance(a, list):
                b = int(b)
            return a[b]

        return reduce(get_item, key.split(separator), d)
    except KeyError:
        raise KeyError(f"Key '{key}' not found")
    except IndexError:
        raise IndexError(f"Index '{key}' out of range")
