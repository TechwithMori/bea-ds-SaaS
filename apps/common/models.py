"""Timestamped base models."""

from __future__ import annotations

import uuid

from django.db import models


class UUIDModel(models.Model):
    """Primary key that is safe to expose in public APIs."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedModel(UUIDModel):
    """Adds created/updated timestamps to a UUID primary key."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
