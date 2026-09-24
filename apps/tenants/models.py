"""Store (tenant) records.

Each Tenant is one automated storefront. Isolation is row-level: other apps
foreign-key to Tenant and filter every queryset by the request tenant.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.text import slugify

from apps.common.models import TimeStampedModel


class Tenant(TimeStampedModel):
    """A merchant store instance and its commercial state."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        PAST_DUE = "past_due", "Past due"
        SUSPENDED = "suspended", "Suspended"
        CANCELLED = "cancelled", "Cancelled"

    class Plan(models.TextChoices):
        TRIAL = "trial", "Trial"
        STARTER = "starter", "Starter"
        GROWTH = "growth", "Growth"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tenants",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    plan = models.CharField(max_length=20, choices=Plan.choices, default=Plan.TRIAL)
    custom_domain = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional storefront hostname, for example shop.example.com.",
    )
    currency = models.CharField(max_length=3, default="USD")
    niche = models.CharField(max_length=64, default="beauty")
    settings = models.JSONField(default=dict, blank=True)
    is_default = models.BooleanField(
        default=False,
        help_text="Used when an authenticated request omits X-Tenant-Slug.",
    )

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("owner",),
                condition=models.Q(is_default=True),
                name="tenants_one_default_store_per_owner",
            ),
        ]
        indexes = [
            models.Index(fields=("status", "plan")),
            models.Index(fields=("owner", "slug")),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args: object, **kwargs: object) -> None:
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)

    @property
    def can_sell(self) -> bool:
        """Only active, paid (or trial) stores may accept storefront orders."""
        return self.status == self.Status.ACTIVE
