"""WSGI config for voice_summarizer project."""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "voice_summarizer.settings")

application = get_wsgi_application()
