"""Retention desk: buyers, inquiries, and lifecycle messages."""

from __future__ import annotations

from decimal import Decimal

from django.db import models

from apps.common.models import TimeStampedModel
from apps.tenants.models import Tenant


class Customer(TimeStampedModel):
    """A store's end customer, rolled up from orders."""

    class Tier(models.TextChoices):
        MEMBER = "member", "Member"
        INSIDER = "insider", "Insider"
        MUSE = "muse", "Muse"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="customers")
    name = models.CharField(max_length=160)
    email = models.EmailField()
    loyalty_tier = models.CharField(max_length=16, choices=Tier.choices, default=Tier.MEMBER)
    lifetime_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    orders_count = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=0)
    last_order_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-lifetime_value", "email")
        constraints = [
            models.UniqueConstraint(fields=("tenant", "email"), name="customers_unique_email"),
        ]
        indexes = [models.Index(fields=("tenant", "loyalty_tier"), name="cust_tenant_tier_idx")]

    def __str__(self) -> str:
        return self.email


class Inquiry(TimeStampedModel):
    """A customer question waiting on the retention desk."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        WAITING = "waiting", "Waiting"
        RESOLVED = "resolved", "Resolved"

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        CHAT = "chat", "Chat"
        SMS = "sms", "SMS"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="inquiries")
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="inquiries",
    )
    customer_name = models.CharField(max_length=160)
    customer_email = models.EmailField()
    subject = models.CharField(max_length=180)
    body = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.EMAIL)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "inquiries"
        indexes = [models.Index(fields=("tenant", "status"), name="cust_inquiry_status_idx")]

    def __str__(self) -> str:
        return self.subject


class RetentionTrigger(TimeStampedModel):
    """An automated email or SMS the desk sends after a lifecycle event."""

    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"

    class Event(models.TextChoices):
        WELCOME = "welcome", "Welcome"
        ABANDONED_CHECKOUT = "abandoned_checkout", "Abandoned checkout"
        POST_PURCHASE = "post_purchase", "Post purchase"
        WINBACK = "winback", "Win-back"
        REVIEW_REQUEST = "review_request", "Review request"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="retention_triggers")
    name = models.CharField(max_length=120)
    channel = models.CharField(max_length=16, choices=Channel.choices, default=Channel.EMAIL)
    event = models.CharField(max_length=32, choices=Event.choices)
    is_enabled = models.BooleanField(default=True)
    delay_hours = models.PositiveIntegerField(default=0)
    template_preview = models.TextField(blank=True)

    class Meta:
        ordering = ("delay_hours", "name")
        constraints = [
            models.UniqueConstraint(fields=("tenant", "name"), name="customers_unique_trigger_name"),
        ]

    def __str__(self) -> str:
        return self.name
