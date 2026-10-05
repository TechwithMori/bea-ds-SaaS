"""Growth desk: creative assets, hooks, channel connections, and ad spend."""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel
from apps.tenants.models import Tenant


class ContentAsset(TimeStampedModel):
    """A piece of store creative: still, motion, or written copy."""

    class Kind(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"
        COPY = "copy", "Copy"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        APPROVED = "approved", "Approved"
        LIVE = "live", "Live"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="content_assets")
    title = models.CharField(max_length=180)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.COPY)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    channel = models.CharField(max_length=32, default="instagram")
    body = models.TextField(blank=True)
    asset_url = models.URLField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("tenant", "status"), name="mkt_asset_tenant_status_idx")]

    def __str__(self) -> str:
        return self.title


class MarketingHook(TimeStampedModel):
    """A short angle the growth desk can hand to ads or organic posts."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        READY = "ready", "Ready"
        PUBLISHED = "published", "Published"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="marketing_hooks")
    headline = models.CharField(max_length=180)
    angle = models.CharField(max_length=64, default="routine")
    platform = models.CharField(max_length=32, default="instagram")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("tenant", "platform"), name="mkt_hook_tenant_platform_idx")]

    def __str__(self) -> str:
        return self.headline


class ChannelIntegration(TimeStampedModel):
    """A social or ads account the store can connect."""

    class Provider(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        TIKTOK = "tiktok", "TikTok"
        META_ADS = "meta_ads", "Meta Ads"
        GOOGLE_ADS = "google_ads", "Google Ads"
        PINTEREST = "pinterest", "Pinterest"
        KLAVIYO = "klaviyo", "Klaviyo"

    class Status(models.TextChoices):
        DISCONNECTED = "disconnected", "Disconnected"
        CONNECTED = "connected", "Connected"
        ERROR = "error", "Error"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="channel_integrations")
    provider = models.CharField(max_length=32, choices=Provider.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DISCONNECTED)
    account_label = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ("provider",)
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "provider"),
                name="mkt_unique_provider",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.provider} ({self.status})"


class AdSpend(TimeStampedModel):
    """Daily media cost used to compute acquisition cost."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="ad_spend")
    channel = models.CharField(max_length=32)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    spent_on = models.DateField()

    class Meta:
        ordering = ("-spent_on",)
        indexes = [models.Index(fields=("tenant", "spent_on"), name="mkt_spend_tenant_day_idx")]

    def __str__(self) -> str:
        return f"{self.channel} {self.spent_on}"
