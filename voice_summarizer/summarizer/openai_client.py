"""Utilities for interacting with the OpenAI SDK."""
from __future__ import annotations

from pathlib import Path

from django.conf import settings

from openai import OpenAI


class OpenAIConfigurationError(RuntimeError):
    """Raised when required OpenAI configuration is missing."""


def create_client() -> OpenAI:
    """Create an OpenAI client using project settings."""

    api_key = getattr(settings, "OPENAI_API_KEY", None)
    if not api_key:
        raise OpenAIConfigurationError("OPENAI_API_KEY تنظیم نشده است.")

    base_url = getattr(settings, "OPENAI_BASE_URL", None)
    if base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    return OpenAI(api_key=api_key)


def transcribe_audio(file_path: Path, *, client: OpenAI | None = None) -> str:
    """Transcribe the provided audio file using the configured model."""

    client = client or create_client()
    model = getattr(settings, "OPENAI_TRANSCRIBE_MODEL", "whisper-1")

    with file_path.open("rb") as audio_file:
        response = client.audio.transcriptions.create(model=model, file=audio_file)

    transcript_text = getattr(response, "text", "") or ""
    return transcript_text.strip()


def summarize_transcript(transcript: str, *, client: OpenAI | None = None) -> str:
    """Summarize a transcript using the configured chat completion model."""

    client = client or create_client()
    model = getattr(settings, "OPENAI_SUMMARY_MODEL", "gpt-4o-mini")

    messages = [
        {
            "role": "system",
            "content": "تو یک دستیار مطالعات پزشکی هستی که پاسخ‌ها را به فارسی و با ساختار خواسته‌شده ارائه می‌دهد.",
        },
        {
            "role": "user",
            "content": (
                "برای متن زیر یک خلاصهٔ تحلیلی پزشکی تهیه کن."
                " خروجی دقیقاً شامل دو بخش باشد:\n"
                "1) خلاصهٔ کلی در ۳ تا ۴ جمله\n"
                "2) نکات کلیدی به صورت موارد گلوله‌ای\n\n"
                f"متن: {transcript.strip()}"
            ),
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.2,
    )

    choice = response.choices[0] if response.choices else None
    content = getattr(choice, "message", None)
    summary_text = getattr(content, "content", "") if content else ""
    return summary_text.strip()

