"""Views for handling uploads and OpenAI processing."""
from __future__ import annotations

from pathlib import Path

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UploadAudioForm
from .openai_client import (
    OpenAIConfigurationError,
    create_client,
    summarize_transcript,
    transcribe_audio,
)


def upload_and_summarize(request: HttpRequest) -> HttpResponse:
    """Handle audio uploads, transcription, and summarization."""

    transcript = ""
    summary = ""

    if request.method == "POST":
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            storage = FileSystemStorage()
            uploaded_file = form.cleaned_data["file"]
            saved_name = storage.save(uploaded_file.name, uploaded_file)
            saved_path = Path(storage.path(saved_name))
            try:
                client = create_client()
                transcript = transcribe_audio(saved_path, client=client)
                if not transcript:
                    messages.error(request, "رونویسی ناموفق بود.")
                else:
                    summary = summarize_transcript(transcript, client=client)
                    if summary:
                        messages.success(request, "پردازش با موفقیت انجام شد.")
                    else:
                        messages.error(
                            request,
                            "خلاصه‌سازی ناموفق بود. لطفاً دوباره تلاش کنید.",
                        )
            except OpenAIConfigurationError as exc:
                messages.error(request, str(exc))
                transcript = ""
                summary = ""
            except Exception:
                messages.error(
                    request,
                    "خطای ارتباط با سرویس هوش مصنوعی رخ داد. لطفاً بعداً دوباره تلاش کنید.",
                )
                summary = ""
            finally:
                try:
                    storage.delete(saved_name)
                except Exception:
                    pass
            form = UploadAudioForm()
        else:
            messages.error(request, "لطفاً خطاهای فرم را بررسی کنید و دوباره تلاش نمایید.")
    else:
        form = UploadAudioForm()

    context = {
        "form": form,
        "transcript": transcript,
        "summary": summary,
    }
    return render(request, "summarizer/index.html", context)
