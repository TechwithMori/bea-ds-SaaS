"""ASGI entrypoint for async servers."""

from __future__ import annotations

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")

application = get_asgi_application()
