"""URL patterns for the summarizer app."""
from __future__ import annotations

from django.urls import path

from .views import upload_and_summarize

app_name = "summarizer"

urlpatterns = [
    path("", upload_and_summarize, name="home"),
]
