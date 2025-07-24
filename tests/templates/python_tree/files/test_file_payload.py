from io import IOBase

import pytest
from pydantic import ValidationError

from apier.templates.python_tree.base.models.primitives import FilePayload
from apier.utils.path import abs_path_from_current_script

test_file_path = abs_path_from_current_script("data/pdf.pdf")


def test_file_payload():
    """
    Tests the FilePayload built-in model for handling file uploads.
    """
    file_upload = FilePayload(
        filename="my_file.pdf",
        content=open(test_file_path, "rb"),
        content_type="application/pdf",
    )

    assert file_upload.filename == "my_file.pdf"
    assert file_upload.content.read() == open(test_file_path, "rb").read()
    assert file_upload.content_type == "application/pdf"


@pytest.mark.parametrize(
    ("path", "content_type", "expected_content_type"),
    [
        (
            abs_path_from_current_script("data/pdf.pdf"),
            "application/pdf",
            "application/pdf",
        ),
        (
            "tests/templates/python_tree/files/data/pdf.pdf",
            "application/pdf",
            "application/pdf",
        ),
        ("tests/templates/python_tree/files/data/image.jpg", None, "image/jpeg"),
        (
            "tests/templates/python_tree/files/data/empty",
            None,
            "application/octet-stream",
        ),
    ],
)
def test_file_payload_from_path(path, content_type, expected_content_type):
    """
    Tests the FilePayload built-in model loading a file from a path.
    """

    if content_type:
        file_upload = FilePayload.from_path(path=path, content_type=content_type)
    else:
        file_upload = FilePayload.from_path(path=path)

    assert file_upload.filename == path.split("/")[-1]
    assert isinstance(file_upload.content, IOBase)
    assert file_upload.content.read() == open(path, "rb").read()
    assert file_upload.content_type == expected_content_type


def test_file_payload_validation_error():
    """
    Tests that a validation error is raised when an invalid content type is provided to FilePayload.
    """

    with pytest.raises(
        ValidationError, match="Content must be bytes or a file-like object"
    ):
        FilePayload(
            filename="invalid_file",
            content="not_a_file_like_object",
            content_type="text/plain",
        )


def test_file_payload_from_path_error():
    """
    Tests that a validation error is raised when an invalid path is provided to FilePayload.from_path.
    """
    with pytest.raises(FileNotFoundError):
        FilePayload.from_path(path="non_existent_file.txt")
