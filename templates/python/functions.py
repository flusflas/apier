from typing import List

from endpoints import ContentSchema, EndpointParameter


def get_params_by_location(parameters: List[EndpointParameter], param_type: str) -> List[EndpointParameter]:
    return list(filter(lambda p: p.in_location == param_type, parameters))


primitive_response_types_map = {
    'string': 'StringResponse',
    'number': 'FloatResponse',
    'integer': 'IntegerResponse',
    'object': 'ObjectResponse',
    'array': 'ArrayResponse',
    'boolean': 'BooleanResponse',
    'null': 'ObjectResponse',
    '': 'NoResponse',
}


def get_type(*args) -> str:
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

    types = list(args)
    for i, t in enumerate(types):
        if isinstance(t, str) and t in types_map:
            types[i] = types_map[t]
        elif isinstance(t, ContentSchema):
            if t.is_primitive:
                if t.code == 0:  # Request
                    types[i] = types_map[t.name]
                else:
                    types[i] = primitive_response_types_map[t.name]
            else:
                types[i] = t.name
        else:
            raise ValueError("Invalid type")

    types = list(set(types))
    if len(types) == 1:
        return types[0]
    else:
        return f"Union[{','.join(types)}]"
