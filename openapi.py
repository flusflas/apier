import operator
from functools import reduce
from typing import Mapping, Any


class Definition:
    """
    An OpenAPI definition.
    """
    def __init__(self, definition: dict):
        self.definition = definition

    @property
    def paths(self) -> dict:
        """
        Returns all the endpoint paths of this definition.

        :return: The paths content of this definition.
        """
        return self.definition['paths']

    def get_value(self, key: str, separator: str = '.'):
        """
        Returns the value of the definition given by a key, which can define
        multiple levels (e.g. "info.version").

        :param key: The key of the value that will be returned. It can define
                    multiple levels by using a separator (which is '.' by default).
        :param separator: The separator of a multi-level key.
        :return: The definition value of the given key. It raises a KeyError
                 if the value is not found.
        """
        try:
            return reduce(operator.getitem, key.split(separator), self.definition)
        except KeyError:
            raise KeyError(f"Key '{key}' not found")

    def solve_ref(self, ref: str) -> Mapping[str, Any]:
        """
        Returns the definition of the given reference ($ref).
        :param ref: A definition reference (e.g. "#/components/schemas/Store").
        :return: The reference defintion. It raises a KeyError if the value
                 is not found.
        """
        ref_clean = ref.replace('#/', '')
        try:
            return self.get_value(ref_clean, '/')
        except KeyError:
            raise KeyError(f"Reference '{ref}' not found")
