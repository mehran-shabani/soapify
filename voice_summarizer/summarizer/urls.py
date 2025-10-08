"""Legacy URL configuration with no active routes."""
from __future__ import annotations

from django.urls import URLPattern, URLResolver

app_name = "summarizer"

urlpatterns: list[URLPattern | URLResolver] = []
