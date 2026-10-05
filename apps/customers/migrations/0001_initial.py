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
            name="Customer",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=160)),
                ("email", models.EmailField(max_length=254)),
                (
                    "loyalty_tier",
                    models.CharField(
                        choices=[("member", "Member"), ("insider", "Insider"), ("muse", "Muse")],
                        default="member",
                        max_length=16,
                    ),
                ),
                ("lifetime_value", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=12)),
                ("orders_count", models.PositiveIntegerField(default=0)),
                ("points", models.PositiveIntegerField(default=0)),
                ("last_order_at", models.DateTimeField(blank=True, null=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="customers",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("-lifetime_value", "email"),
                "indexes": [models.Index(fields=["tenant", "loyalty_tier"], name="cust_tenant_tier_idx")],
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "email"), name="customers_unique_email"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Inquiry",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("customer_name", models.CharField(max_length=160)),
                ("customer_email", models.EmailField(max_length=254)),
                ("subject", models.CharField(max_length=180)),
                ("body", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("waiting", "Waiting"), ("resolved", "Resolved")],
                        default="open",
                        max_length=16,
                    ),
                ),
                (
                    "channel",
                    models.CharField(
                        choices=[("email", "Email"), ("chat", "Chat"), ("sms", "SMS")],
                        default="email",
                        max_length=16,
                    ),
                ),
                (
                    "customer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="inquiries",
                        to="customers.customer",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inquiries",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "inquiries",
                "ordering": ("-created_at",),
                "indexes": [models.Index(fields=["tenant", "status"], name="cust_inquiry_status_idx")],
            },
        ),
        migrations.CreateModel(
            name="RetentionTrigger",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                (
                    "channel",
                    models.CharField(
                        choices=[("email", "Email"), ("sms", "SMS")],
                        default="email",
                        max_length=16,
                    ),
                ),
                (
                    "event",
                    models.CharField(
                        choices=[
                            ("welcome", "Welcome"),
                            ("abandoned_checkout", "Abandoned checkout"),
                            ("post_purchase", "Post purchase"),
                            ("winback", "Win-back"),
                            ("review_request", "Review request"),
                        ],
                        max_length=32,
                    ),
                ),
                ("is_enabled", models.BooleanField(default=True)),
                ("delay_hours", models.PositiveIntegerField(default=0)),
                ("template_preview", models.TextField(blank=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="retention_triggers",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("delay_hours", "name"),
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "name"), name="customers_unique_trigger_name"),
                ],
            },
        ),
    ]
