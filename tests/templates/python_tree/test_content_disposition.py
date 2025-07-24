import pytest

from apier.templates.python_tree.base.internal.content_disposition import (
    parse_content_disposition,
)


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        (
            'attachment; filename="example.txt"',
            "example.txt",
        ),
        (
            "attachment; filename=example.txt",
            "example.txt",
        ),
        (
            'attachment;filename="AS038100-KT.pdf"',
            "AS038100-KT.pdf",
        ),
        (
            "attachment; filename*=UTF-8''%e2%82%ac%20rates.csv",
            "€ rates.csv",
        ),
        (
            "attachment; filename=\"fallback.txt\"; filename*=UTF-8''better%20name.txt",
            "better name.txt",
        ),
        (
            "attachment; filename*=utf-8''file%20name.txt",
            "file name.txt",
        ),
        (
            "attachment; filename*=UTF-8\\'\\'file%20name.txt",
            "file name.txt",
        ),
        (
            'attachment; filename="file with spaces.txt"',
            "file with spaces.txt",
        ),
        (
            'attachment; filename="file_with_underscores.txt"',
            "file_with_underscores.txt",
        ),
    ],
)
def test_parse_content_disposition(header, expected):
    """Tests the parse_content_disposition function."""
    filename = parse_content_disposition(header)
    assert filename == expected
