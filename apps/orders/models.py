"""End-customer orders captured by a tenant store and forwarded to a supplier."""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel
from apps.products.models import ProductVariant
from apps.tenants.models import Tenant


class Order(TimeStampedModel):
    """A storefront checkout belonging to exactly one tenant."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FORWARDED = "forwarded", "Forwarded to supplier"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"
        FAILED = "failed", "Failed"

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name="orders")
    number = models.CharField(max_length=32, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    customer_name = models.CharField(max_length=160)
    customer_email = models.EmailField()
    shipping_address = models.JSONField(default=dict)
    currency = models.CharField(max_length=3, default="USD")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    shipping_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    supplier_reference = models.CharField(max_length=128, blank=True)
    tracking_carrier = models.CharField(max_length=64, blank=True)
    tracking_number = models.CharField(max_length=128, blank=True)
    tracking_url = models.URLField(blank=True)
    forwarded_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    shipping_route = models.ForeignKey(
        "orders.ShippingRoute",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("tenant", "status")),
            models.Index(fields=("tenant", "created_at")),
            models.Index(fields=("supplier_reference",)),
        ]

    def __str__(self) -> str:
        return self.number

    def recalculate_totals(self) -> None:
        """Recompute money fields from line items. Caller saves the order."""
        subtotal = sum((item.line_total for item in self.items.all()), Decimal("0"))
        self.subtotal = subtotal
        self.total = subtotal + self.shipping_total


class OrderItem(TimeStampedModel):
    """Immutable commercial snapshot of a variant at purchase time."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    sku = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("order", "variant"), name="orders_unique_line_variant"),
        ]

    def __str__(self) -> str:
        return f"{self.sku} x{self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


class ShippingRoute(TimeStampedModel):
    """A lane the store uses to choose a carrier for an end-customer address."""

    class ServiceLevel(models.TextChoices):
        STANDARD = "standard", "Standard"
        EXPRESS = "express", "Express"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="shipping_routes")
    name = models.CharField(max_length=120)
    carrier = models.CharField(max_length=64)
    service_level = models.CharField(
        max_length=16,
        choices=ServiceLevel.choices,
        default=ServiceLevel.STANDARD,
    )
    regions = models.JSONField(
        default=list,
        blank=True,
        help_text="Country codes this lane accepts. Use ROW as the catch-all.",
    )
    priority = models.PositiveIntegerField(default=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("priority", "name")
        constraints = [
            models.UniqueConstraint(fields=("tenant", "name"), name="orders_unique_route_name"),
        ]
        indexes = [
            models.Index(fields=("tenant", "is_active", "priority"), name="orders_route_tenant_pri_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.carrier})"
