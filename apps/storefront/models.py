"""Shop desk: theme, conversion settings, and bundles."""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel
from apps.products.models import StoreProduct
from apps.tenants.models import Tenant


class StorefrontSettings(TimeStampedModel):
    """One configuration record per store."""

    class Theme(models.TextChoices):
        ATELIER = "atelier", "Atelier"
        CLINIQUE = "clinique", "Clinique"
        NOIR = "noir", "Noir"
        SOL = "sol", "Sol"

    class FontPairing(models.TextChoices):
        EDITORIAL = "editorial", "Editorial"
        CLEAN = "clean", "Clean"
        SOFT = "soft", "Soft"

    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="storefront")
    theme = models.CharField(max_length=16, choices=Theme.choices, default=Theme.ATELIER)
    font_pairing = models.CharField(
        max_length=16,
        choices=FontPairing.choices,
        default=FontPairing.EDITORIAL,
    )
    primary_color = models.CharField(max_length=7, default="#241910")
    accent_color = models.CharField(max_length=7, default="#C9847A")
    announcement = models.CharField(max_length=180, blank=True)
    show_reviews = models.BooleanField(default=True)
    show_urgency = models.BooleanField(default=False)
    show_bundles = models.BooleanField(default=True)
    free_shipping_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("75.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        verbose_name = "storefront settings"
        verbose_name_plural = "storefront settings"

    def __str__(self) -> str:
        return f"{self.tenant.name} storefront"


class Bundle(TimeStampedModel):
    """A merchandised set of listings sold at a discount."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="bundles")
    name = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("80"))],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(fields=("tenant", "name"), name="storefront_unique_bundle_name"),
        ]

    def __str__(self) -> str:
        return self.name


class BundleItem(TimeStampedModel):
    bundle = models.ForeignKey(Bundle, on_delete=models.CASCADE, related_name="items")
    store_product = models.ForeignKey(StoreProduct, on_delete=models.PROTECT, related_name="bundle_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("bundle", "store_product"),
                name="sf_unique_bundle_item",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.bundle.name} / {self.store_product_id}"
