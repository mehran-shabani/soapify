"""URL patterns for the uploader app."""
from __future__ import annotations

from django.urls import path

from .views import home

app_name = "uploader"

urlpatterns = [
    path("", home, name="home"),
]
