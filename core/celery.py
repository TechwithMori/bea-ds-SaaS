"""Celery application bound to the Django settings module."""

from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings.local")

app = Celery("bea_drops")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> str:
    """Return the request id so operators can confirm the worker is alive."""
    return f"pong:{self.request.id}"
