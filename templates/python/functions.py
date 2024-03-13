import re
from typing import Union

from consts import NO_RESPONSE_ID
from endpoints import ContentSchema, EndpointMethod
from utils.strings import to_snake_case


def get_type_hint(*args: Union[str, ContentSchema],
                  include_primitive_type: bool = False) -> str:
    """
    Returns the type string associated to the given array of schemas so that
    it can be used for type hints.

    >>> get_type_hint(ContentSchema(name='MyType'))
    'models.MyType'
    >>> get_type_hint('string')
    'str'
    >>> get_type_hint('string', 'integer')
    'Union[str, int]'
    >>> get_type_hint(ContentSchema(name='MyType'), 'array')
    'Union[models.MyType, list]'
    >>> get_type_hint(ContentSchema(name='MyType', definition={'type': 'object'}), include_primitive_type=True)
    'Union[models.MyType, dict]'

    :param args:    List of type strings and/or ContentSchema instances.
    :param include_primitive_type: If True, the primitive type of the
                    ContentSchema instances will be added to the output.
                    The 'type' must be defined in the ContentSchema definition.
    :return:        Type hint.
    """
    if len(args) == 0:
        return ''

    types_map = {
        'string': 'str',
        'number': 'float',
        'integer': 'int',
        'object': 'dict',
        'array': 'list',
        'boolean': 'bool',
        'null': 'None',
    }

    types = []
    for i, t in enumerate(args):
        if isinstance(t, str):
            if t in types_map:
                types.append(types_map.get(t.lower(), t))
            else:
                types.append(t)
        elif isinstance(t, ContentSchema):
            if t.name in [NO_RESPONSE_ID, '']:
                types.append('primitives.NoResponse')
                break
            types.append("models." + t.name)
            if include_primitive_type and 'type' in t.schema:
                types.append(types_map[t.schema['type']])
        else:
            raise ValueError("Invalid type")

    types = list(dict.fromkeys(types))
    if len(types) == 1:
        return types[0]
    else:
        return f"Union[{', '.join(types)}]"


def payload_from_input_parameters(endpoint_method: EndpointMethod) -> str:
    """
    Returns the code to dynamically generate the payload of an endpoint that
    uses the input-parameters extension.
    """
    try:
        params = {}
        for method_param in endpoint_method.parameters:
            if method_param.in_location == 'path':
                params[method_param.name] = f"self._path_value('{to_snake_case(method_param.name)}')"
            elif method_param.in_location in ['query', 'header']:
                params[method_param.name] = f"params[{method_param.name}]"

        for input_param in endpoint_method.extensions.input_parameters.parameters:
            params[input_param.name] = to_snake_case(input_param.name)

        payload_str = endpoint_method.extensions.input_parameters.payload

        escaped_expression = payload_str.replace('"', '\\"')

        # Find and replace the variables in the expression
        variables = re.findall(r'{{([^{].*?[^}])}}', escaped_expression)
        for var in variables:
            param_name = params[var.strip()]
            escaped_expression = escaped_expression.replace('{{' + var + '}}', '" + str(' + param_name + ') + "')

        escaped_expression = f'"{escaped_expression}"'

        if escaped_expression.startswith('"" +'):
            escaped_expression = escaped_expression[len('"" +'):]
        if escaped_expression.endswith('+ ""'):
            escaped_expression = escaped_expression[:-len('+ ""'):]

        return escaped_expression

    except ValueError as e:
        raise ValueError(f"Error building payload from input-parameters extension: {e}")


def get_method_name(endpoint_method: EndpointMethod) -> str:
    """
    Returns the name of the function used in the client for the given endpoint
    method. By default, the name will be the HTTP method name, but this may
    change if the method-name extension is defined.
    """
    if endpoint_method.extensions and endpoint_method.extensions.method_name:
        extension_info = endpoint_method.extensions.method_name

        if 'python' in extension_info.templates:
            return to_snake_case(extension_info.templates['python'])

        if extension_info.default:
            return to_snake_case(extension_info.default)

    return to_snake_case(endpoint_method.name)
