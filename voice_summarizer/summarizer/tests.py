"""Test suite for the summarizer app."""
from __future__ import annotations

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from uploader.forms import MAX_FILE_SIZE_BYTES, UploadAudioForm


class UploadAudioFormTests(TestCase):
    """Validate UploadAudioForm behavior."""

    def test_valid_extension_and_size(self) -> None:
        content = b"dummy-audio"
        uploaded = SimpleUploadedFile("lecture.mp3", content, content_type="audio/mpeg")
        form = UploadAudioForm(files={"file": uploaded})

        self.assertTrue(form.is_valid(), form.errors.as_text())

    def test_invalid_extension(self) -> None:
        content = b"data"
        uploaded = SimpleUploadedFile("notes.txt", content, content_type="text/plain")
        form = UploadAudioForm(files={"file": uploaded})

        self.assertFalse(form.is_valid())
        self.assertIn("فرمت فایل پشتیبانی نمی‌شود", form.errors["file"][0])

    def test_oversized_file(self) -> None:
        content = b"a" * (MAX_FILE_SIZE_BYTES + 1)
        uploaded = SimpleUploadedFile("lecture.wav", content, content_type="audio/wav")
        form = UploadAudioForm(files={"file": uploaded})

        self.assertFalse(form.is_valid())
        self.assertIn("حجم فایل بیش از", form.errors["file"][0])


class HomeViewTests(TestCase):
    """Ensure the home page renders correctly."""

    def test_get_request_renders_form(self) -> None:
        client = Client()
        response = client.get(reverse("uploader:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "خلاصه‌ساز هوشمند سخنرانی")
        self.assertContains(response, "بارگذاری فایل")
