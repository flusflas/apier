import re


def to_pascal_case(text: str) -> str:
    """
    Returns the PascalCase string of the given input.
    """
    words = re.findall('[a-zA-Z0-9]+', text)
    pascal_case_text = ''.join(word[0].upper() + word[1:] for word in words)
    return pascal_case_text
