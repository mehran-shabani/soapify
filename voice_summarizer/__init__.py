"""Project package initialisation helper."""
from __future__ import annotations

from importlib import import_module
import sys

_project_module = import_module(".voice_summarizer", package=__name__)
sys.modules[f"{__name__}.voice_summarizer"] = _project_module
voice_summarizer = _project_module

__all__ = ["voice_summarizer"]
