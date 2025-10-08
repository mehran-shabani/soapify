"""Unit tests for the uploader forms using pytest style assertions."""
from __future__ import annotations

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from uploader.forms import MAX_FILE_SIZE_BYTES, UploadAudioForm


@pytest.mark.parametrize(
    "filename, content_type",
    [
        ("audio.mp3", "audio/mpeg"),
        ("lecture.wav", "audio/wav"),
    ],
)
def test_valid_file_upload(filename: str, content_type: str) -> None:
    """A file with an allowed extension and size should be accepted."""

    uploaded = SimpleUploadedFile(filename, b"data", content_type=content_type)
    form = UploadAudioForm(data={}, files={"file": uploaded})

    assert form.is_valid(), form.errors.as_text()


def test_invalid_extension_rejected() -> None:
    """Files with unsupported extensions should trigger a validation error."""

    uploaded = SimpleUploadedFile("notes.txt", b"data", content_type="text/plain")
    form = UploadAudioForm(data={}, files={"file": uploaded})

    assert not form.is_valid()
    assert "فرمت فایل پشتیبانی نمی‌شود" in form.errors["file"][0]


def test_file_too_large_rejected() -> None:
    """Files above the maximum size should not validate."""

    uploaded = SimpleUploadedFile(
        "bigfile.mp3",
        b"x" * (MAX_FILE_SIZE_BYTES + 1),
        content_type="audio/mpeg",
    )
    form = UploadAudioForm(data={}, files={"file": uploaded})

    assert not form.is_valid()
    assert "حجم فایل بیش از" in form.errors["file"][0]
