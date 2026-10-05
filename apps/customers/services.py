"""Roll order history up onto the store's customer record."""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, Sum

from apps.orders.models import Order

from .models import Customer


def record_order_customer(order: Order) -> Customer:
    """Create or refresh the buyer behind this order."""
    email = order.customer_email.strip().lower()
    settled = Order.objects.filter(tenant=order.tenant, customer_email__iexact=email).exclude(
        status__in=[Order.Status.CANCELLED, Order.Status.FAILED]
    )
    stats = settled.aggregate(lifetime=Sum("total"), count=Count("id"))
    lifetime = stats["lifetime"] or Decimal("0")
    orders_count = stats["count"] or 0
    if lifetime >= Decimal("300"):
        tier = Customer.Tier.MUSE
    elif lifetime >= Decimal("120"):
        tier = Customer.Tier.INSIDER
    else:
        tier = Customer.Tier.MEMBER
    customer, _created = Customer.objects.update_or_create(
        tenant=order.tenant,
        email=email,
        defaults={
            "name": order.customer_name,
            "lifetime_value": lifetime,
            "orders_count": orders_count,
            "points": int(lifetime),
            "loyalty_tier": tier,
            "last_order_at": settled.order_by("-created_at").values_list("created_at", flat=True).first(),
        },
    )
    return customer
