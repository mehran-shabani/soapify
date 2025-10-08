"""Tests for the OpenAI service layer using pytest."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from summarizer import services
from summarizer.services import OpenAIConfigurationError


class DummyOpenAI:
    """Lightweight stand-in for the OpenAI client constructor."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_create_client_requires_api_key(settings, monkeypatch) -> None:
    """create_client should raise if no API key is configured."""

    settings.OPENAI_API_KEY = None
    monkeypatch.setattr(services, "OpenAI", DummyOpenAI)

    with pytest.raises(OpenAIConfigurationError):
        services.create_client()


def test_create_client_uses_base_url_when_configured(settings, monkeypatch) -> None:
    """A configured base URL should be forwarded to the OpenAI client."""

    settings.OPENAI_API_KEY = "key"
    settings.OPENAI_BASE_URL = "https://example.test/api"
    monkeypatch.setattr(services, "OpenAI", DummyOpenAI)

    client = services.create_client()

    assert isinstance(client, DummyOpenAI)
    assert client.kwargs == {"api_key": "key", "base_url": "https://example.test/api"}


def test_create_client_omits_base_url_when_empty(settings, monkeypatch) -> None:
    """Empty base URLs should fall back to the SDK default."""

    settings.OPENAI_API_KEY = "another-key"
    settings.OPENAI_BASE_URL = None
    monkeypatch.setattr(services, "OpenAI", DummyOpenAI)

    client = services.create_client()

    assert isinstance(client, DummyOpenAI)
    assert client.kwargs == {"api_key": "another-key"}


def test_transcribe_file_returns_stripped_text(settings, tmp_path, monkeypatch) -> None:
    """transcribe_file should relay the configured model and strip whitespace."""

    settings.OPENAI_API_KEY = "key"
    settings.OPENAI_TRANSCRIBE_MODEL = "whisper-test"

    response = SimpleNamespace(text="  transcript result  ")
    calls: dict[str, object] = {}

    def fake_create_client():
        def fake_transcribe(model, file):
            calls["model"] = model
            calls["filename"] = Path(file.name).name  # type: ignore[attr-defined]
            return response

        return SimpleNamespace(
            audio=SimpleNamespace(
                transcriptions=SimpleNamespace(create=fake_transcribe)
            )
        )

    monkeypatch.setattr(services, "create_client", fake_create_client)

    audio_path = tmp_path / "audio.mp3"
    audio_path.write_bytes(b"binary")

    result = services.transcribe_file(audio_path)

    assert result == "transcript result"
    assert calls["model"] == "whisper-test"
    assert calls["filename"].endswith("audio.mp3")


def test_transcribe_file_invalid_response(settings, tmp_path, monkeypatch) -> None:
    """Missing text fields from OpenAI responses should raise an error."""

    settings.OPENAI_API_KEY = "key"

    fake_client = SimpleNamespace(
        audio=SimpleNamespace(
            transcriptions=SimpleNamespace(create=lambda *args, **kwargs: SimpleNamespace())
        )
    )
    monkeypatch.setattr(services, "create_client", lambda: fake_client)

    audio_path = tmp_path / "audio.wav"
    audio_path.write_bytes(b"binary")

    with pytest.raises(ValueError):
        services.transcribe_file(audio_path)


def test_summarize_text_builds_prompt_and_trims(settings, monkeypatch) -> None:
    """summarize_text should build the expected prompt and trim responses."""

    settings.OPENAI_API_KEY = "key"
    settings.OPENAI_SUMMARY_MODEL = "gpt-test"

    recorded: dict[str, object] = {}

    def fake_create(messages_return: str):
        def _inner(*, model, messages, temperature):
            recorded.update({
                "model": model,
                "messages": messages,
                "temperature": temperature,
            })
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(message=SimpleNamespace(content=messages_return))
                ]
            )

        return _inner

    dummy_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=fake_create("  final summary  "))
        )
    )

    monkeypatch.setattr(services, "create_client", lambda: dummy_client)

    result = services.summarize_text("  متن آزمایشی  ")

    assert result == "final summary"
    assert recorded["model"] == "gpt-test"
    assert recorded["temperature"] == 0.2
    assert recorded["messages"][0]["role"] == "system"
    assert "متن: متن آزمایشی" in recorded["messages"][1]["content"]


def test_summarize_text_missing_choices_raises(monkeypatch) -> None:
    """Empty choices should raise a ValueError."""

    dummy_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **_: SimpleNamespace(choices=[]))
        )
    )

    result_client = lambda: dummy_client
    monkeypatch.setattr(services, "create_client", result_client)

    with pytest.raises(ValueError):
        services.summarize_text("hello")


def test_summarize_text_missing_content_raises(monkeypatch) -> None:
    """A choice without string content should raise a ValueError."""

    dummy_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: SimpleNamespace(
                    choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
                )
            )
        )
    )

    monkeypatch.setattr(services, "create_client", lambda: dummy_client)

    with pytest.raises(ValueError):
        services.summarize_text("hello")
