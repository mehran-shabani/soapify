"""View stubs for the summarizer app."""
from __future__ import annotations

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import UploadAudioForm


def upload_and_summarize(request: HttpRequest) -> HttpResponse:
    """Handle audio uploads and prepare placeholders for future processing."""

    transcript = ""
    summary = ""

    if request.method == "POST":
        form = UploadAudioForm(request.POST, request.FILES)
        if form.is_valid():
            storage = FileSystemStorage()
            uploaded_file = form.cleaned_data["file"]
            saved_path = storage.save(uploaded_file.name, uploaded_file)
            messages.success(request, "فایل با موفقیت دریافت شد. پردازش هوشمند به‌زودی افزوده می‌شود.")
            storage.delete(saved_path)
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
