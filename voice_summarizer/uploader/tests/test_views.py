"""Integration-style tests for the uploader views."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from summarizer.services import OpenAIConfigurationError


@pytest.mark.django_db
def test_home_get_renders_page(client) -> None:
    """The home page should render successfully for a GET request."""

    response = client.get(reverse("uploader:home"))

    assert response.status_code == 200
    assert "خلاصه‌ساز هوشمند سخنرانی" in response.content.decode("utf-8")
    assert "بارگذاری فایل" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_home_post_success(client, settings, tmp_path, monkeypatch) -> None:
    """A successful upload should run through transcription and summarization."""

    settings.MEDIA_ROOT = tmp_path
    dummy_client = object()

    monkeypatch.setattr("uploader.views.create_client", lambda: dummy_client)

    saved_files: list[Path] = []

    def fake_transcribe(file_path, *, client):
        saved_files.append(Path(file_path))
        assert client is dummy_client
        return "  این یک متن است.  "

    def fake_summarize(transcript, *, client):
        assert transcript == "  این یک متن است.  "
        assert client is dummy_client
        return "  خلاصهٔ نهایی  "

    monkeypatch.setattr("uploader.views.transcribe_file", fake_transcribe)
    monkeypatch.setattr("uploader.views.summarize_text", fake_summarize)

    uploaded = SimpleUploadedFile("lecture.mp3", b"audio", content_type="audio/mpeg")
    response = client.post(
        reverse("uploader:home"),
        data={"file": uploaded},
        follow=True,
    )

    assert response.status_code == 200
    assert response.context["transcript"] == "  این یک متن است.  "
    assert response.context["summary"] == "  خلاصهٔ نهایی  "
    messages = {message.message for message in response.context["messages"]}
    assert "پردازش با موفقیت انجام شد." in messages
    # Uploaded file should be removed from storage even after success
    assert not any(tmp_path.iterdir())
    assert saved_files and saved_files[0].name == "lecture.mp3"


@pytest.mark.django_db
def test_home_post_handles_empty_transcript(client, settings, tmp_path, monkeypatch) -> None:
    """If transcription returns empty text, the user should see an error message."""

    settings.MEDIA_ROOT = tmp_path
    dummy_client = object()

    monkeypatch.setattr("uploader.views.create_client", lambda: dummy_client)
    monkeypatch.setattr(
        "uploader.views.transcribe_file", lambda *args, **kwargs: ""
    )
    summarize_called = SimpleNamespace(count=0)

    def fake_summarize(*args, **kwargs):
        summarize_called.count += 1
        return ""

    monkeypatch.setattr("uploader.views.summarize_text", fake_summarize)

    uploaded = SimpleUploadedFile("lecture.mp3", b"audio", content_type="audio/mpeg")
    response = client.post(
        reverse("uploader:home"),
        data={"file": uploaded},
        follow=True,
    )

    assert response.status_code == 200
    assert response.context["transcript"] == ""
    assert response.context["summary"] == ""
    messages = {message.message for message in response.context["messages"]}
    assert "رونویسی ناموفق بود." in messages
    assert summarize_called.count == 0
    assert not any(tmp_path.iterdir())


@pytest.mark.django_db
def test_home_post_handles_missing_api_key(client, settings, tmp_path, monkeypatch) -> None:
    """OpenAI configuration errors should be surfaced to the user."""

    settings.MEDIA_ROOT = tmp_path

    def fake_create_client():
        raise OpenAIConfigurationError("OPENAI_API_KEY تنظیم نشده است.")

    monkeypatch.setattr("uploader.views.create_client", fake_create_client)
    monkeypatch.setattr("uploader.views.transcribe_file", lambda *args, **kwargs: "")
    monkeypatch.setattr("uploader.views.summarize_text", lambda *args, **kwargs: "")

    uploaded = SimpleUploadedFile("lecture.mp3", b"audio", content_type="audio/mpeg")
    response = client.post(
        reverse("uploader:home"),
        data={"file": uploaded},
        follow=True,
    )

    assert response.status_code == 200
    assert response.context["transcript"] == ""
    assert response.context["summary"] == ""
    messages = {message.message for message in response.context["messages"]}
    assert "OPENAI_API_KEY تنظیم نشده است." in messages
    assert not any(tmp_path.iterdir())
