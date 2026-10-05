"""Cosmetic catalog.

``Supplier`` and ``Product`` are platform-global. A store does not own the
wholesale catalog; it publishes selected variants through ``StoreProduct``,
which is the tenant-scoped row.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel
from apps.tenants.models import Tenant


class Supplier(TimeStampedModel):
    """Upstream beauty wholesaler the platform forwards orders to."""

    name = models.CharField(max_length=160)
    code = models.SlugField(max_length=64, unique=True)
    api_base_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)

    class SyncStatus(models.TextChoices):
        IDLE = "idle", "Idle"
        OK = "ok", "Synced"
        FAILED = "failed", "Failed"

    sync_status = models.CharField(max_length=16, choices=SyncStatus.choices, default=SyncStatus.IDLE)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    credentials = models.JSONField(
        default=dict,
        blank=True,
        help_text="Non-secret supplier config. Secrets belong in the environment or a vault.",
    )

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    """A cosmetic SKU in the global catalog, before a store marks it up."""

    class Category(models.TextChoices):
        SKINCARE = "skincare", "Skincare"
        MAKEUP = "makeup", "Makeup"
        HAIRCARE = "haircare", "Haircare"
        FRAGRANCE = "fragrance", "Fragrance"
        TOOLS = "tools", "Tools"

    class Compliance(models.TextChoices):
        COMPLIANT = "compliant", "Compliant"
        PENDING_REVIEW = "pending_review", "Pending review"
        RESTRICTED = "restricted", "Restricted"

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="products")
    supplier_sku = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    sku = models.CharField(max_length=64, unique=True)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.SKINCARE)
    brand = models.CharField(max_length=120, blank=True)
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    suggested_retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    stock_level = models.PositiveIntegerField(default=0)
    weight_grams = models.PositiveIntegerField(default=0)
    ingredients = models.JSONField(default=list, blank=True)
    specifications = models.JSONField(default=dict, blank=True)
    compliance_status = models.CharField(
        max_length=32,
        choices=Compliance.choices,
        default=Compliance.COMPLIANT,
    )
    compliance_notes = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("title",)
        constraints = [
            models.UniqueConstraint(
                fields=("supplier", "supplier_sku"),
                name="products_unique_supplier_sku",
            ),
        ]
        indexes = [
            models.Index(fields=("category", "is_active")),
            models.Index(fields=("sku",)),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.sku})"


class ProductVariant(TimeStampedModel):
    """Shade, size, or scent variation of a catalog product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=120)
    sku = models.CharField(max_length=64, unique=True)
    attributes = models.JSONField(default=dict, blank=True)
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_level = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("product", "name")
        constraints = [
            models.UniqueConstraint(fields=("product", "name"), name="products_unique_variant_name"),
        ]

    def __str__(self) -> str:
        return f"{self.product.title} / {self.name}"


class StoreProduct(TimeStampedModel):
    """A tenant's published listing and retail price for a global variant."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="store_products")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="listings")
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    is_published = models.BooleanField(default=False)
    title_override = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "variant"),
                name="products_unique_store_variant",
            ),
        ]
        ordering = ("-created_at",)
        indexes = [models.Index(fields=("tenant", "is_published"))]

    def __str__(self) -> str:
        return self.title_override or str(self.variant)
