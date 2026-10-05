import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("products", "0002_storeproduct_ordering"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StorefrontSettings",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "theme",
                    models.CharField(
                        choices=[
                            ("atelier", "Atelier"),
                            ("clinique", "Clinique"),
                            ("noir", "Noir"),
                            ("sol", "Sol"),
                        ],
                        default="atelier",
                        max_length=16,
                    ),
                ),
                (
                    "font_pairing",
                    models.CharField(
                        choices=[("editorial", "Editorial"), ("clean", "Clean"), ("soft", "Soft")],
                        default="editorial",
                        max_length=16,
                    ),
                ),
                ("primary_color", models.CharField(default="#241910", max_length=7)),
                ("accent_color", models.CharField(default="#C9847A", max_length=7)),
                ("announcement", models.CharField(blank=True, max_length=180)),
                ("show_reviews", models.BooleanField(default=True)),
                ("show_urgency", models.BooleanField(default=False)),
                ("show_bundles", models.BooleanField(default=True)),
                (
                    "free_shipping_threshold",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("75.00"),
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                (
                    "tenant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="storefront",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "storefront settings",
                "verbose_name_plural": "storefront settings",
            },
        ),
        migrations.CreateModel(
            name="Bundle",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("description", models.TextField(blank=True)),
                (
                    "discount_percent",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("10.00"),
                        max_digits=5,
                        validators=[
                            django.core.validators.MinValueValidator(Decimal("0")),
                            django.core.validators.MaxValueValidator(Decimal("80")),
                        ],
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bundles",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "name"), name="storefront_unique_bundle_name"),
                ],
            },
        ),
        migrations.CreateModel(
            name="BundleItem",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "quantity",
                    models.PositiveIntegerField(
                        default=1,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "bundle",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="storefront.bundle",
                    ),
                ),
                (
                    "store_product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bundle_items",
                        to="products.storeproduct",
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("bundle", "store_product"),
                        name="sf_unique_bundle_item",
                    ),
                ],
            },
        ),
    ]
