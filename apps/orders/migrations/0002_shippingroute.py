import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
        ("tenants", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShippingRoute",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("carrier", models.CharField(max_length=64)),
                (
                    "service_level",
                    models.CharField(
                        choices=[("standard", "Standard"), ("express", "Express")],
                        default="standard",
                        max_length=16,
                    ),
                ),
                (
                    "regions",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text="Country codes this lane accepts. Use ROW as the catch-all.",
                    ),
                ),
                ("priority", models.PositiveIntegerField(default=100)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shipping_routes",
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={
                "ordering": ("priority", "name"),
            },
        ),
        migrations.AddConstraint(
            model_name="shippingroute",
            constraint=models.UniqueConstraint(fields=("tenant", "name"), name="orders_unique_route_name"),
        ),
        migrations.AddIndex(
            model_name="shippingroute",
            index=models.Index(fields=["tenant", "is_active", "priority"], name="orders_route_tenant_pri_idx"),
        ),
        migrations.AddField(
            model_name="order",
            name="shipping_route",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="orders",
                to="orders.shippingroute",
            ),
        ),
    ]
