"""Bea Drops platform package.

Celery is imported lazily so management commands and tests can boot even when
the broker client is not yet installed in a throwaway environment.
"""

from __future__ import annotations

try:
    from .celery import app as celery_app
except ImportError:  # pragma: no cover - import-time guard only
    celery_app = None

__all__ = ("celery_app",)
