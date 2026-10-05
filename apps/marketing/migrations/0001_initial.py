import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentAsset",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                (
                    "kind",
                    models.CharField(
                        choices=[("image", "Image"), ("video", "Video"), ("copy", "Copy")],
                        default="copy",
                        max_length=16,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("approved", "Approved"), ("live", "Live")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                ("channel", models.CharField(default="instagram", max_length=32)),
                ("body", models.TextField(blank=True)),
                ("asset_url", models.URLField(blank=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="content_assets",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [models.Index(fields=["tenant", "status"], name="mkt_asset_tenant_status_idx")],
            },
        ),
        migrations.CreateModel(
            name="MarketingHook",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("headline", models.CharField(max_length=180)),
                ("angle", models.CharField(default="routine", max_length=64)),
                ("platform", models.CharField(default="instagram", max_length=32)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("ready", "Ready"), ("published", "Published")],
                        default="draft",
                        max_length=16,
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="marketing_hooks",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [models.Index(fields=["tenant", "platform"], name="mkt_hook_tenant_platform_idx")],
            },
        ),
        migrations.CreateModel(
            name="ChannelIntegration",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "provider",
                    models.CharField(
                        choices=[
                            ("instagram", "Instagram"),
                            ("tiktok", "TikTok"),
                            ("meta_ads", "Meta Ads"),
                            ("google_ads", "Google Ads"),
                            ("pinterest", "Pinterest"),
                            ("klaviyo", "Klaviyo"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("disconnected", "Disconnected"),
                            ("connected", "Connected"),
                            ("error", "Error"),
                        ],
                        default="disconnected",
                        max_length=16,
                    ),
                ),
                ("account_label", models.CharField(blank=True, max_length=160)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="channel_integrations",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("provider",),
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "provider"), name="mkt_unique_provider"),
                ],
            },
        ),
        migrations.CreateModel(
            name="AdSpend",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("channel", models.CharField(max_length=32)),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                        validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    ),
                ),
                ("spent_on", models.DateField()),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ad_spend",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("-spent_on",),
                "indexes": [models.Index(fields=["tenant", "spent_on"], name="mkt_spend_tenant_day_idx")],
            },
        ),
    ]
