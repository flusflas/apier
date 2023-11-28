from typing import Union

from consts import NO_RESPONSE_ID
from endpoints import ContentSchema


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
            types.append(types_map.get(t.lower(), t))
        elif isinstance(t, ContentSchema):
            if t.name in [NO_RESPONSE_ID, '']:
                types.append('primitives.NoResponse')
                break
            types.append("models." + t.name)
            if include_primitive_type and 'type' in t.definition:
                types.append(types_map[t.definition['type']])
        else:
            raise ValueError("Invalid type")

    types = list(dict.fromkeys(types))
    if len(types) == 1:
        return types[0]
    else:
        return f"Union[{', '.join(types)}]"
