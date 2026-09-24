"""Forward paid orders to the wholesale supplier and record the supplier reference."""

from __future__ import annotations

import logging
from typing import Any

import httpx
from celery import shared_task
from django.db import transaction
from django.utils import timezone

from .models import Order

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(httpx.HTTPError,), retry_backoff=True, max_retries=5)
def forward_order_to_supplier(self, order_id: str) -> dict[str, Any]:
    """POST a paid order to the variant's supplier fulfillment endpoint."""
    order = (
        Order.objects.select_related("tenant")
        .prefetch_related("items__variant__product__supplier")
        .get(pk=order_id)
    )
    if order.status not in {Order.Status.PAID, Order.Status.FAILED}:
        return {"skipped": True, "status": order.status}

    item = order.items.select_related("variant__product__supplier").first()
    if item is None:
        order.status = Order.Status.FAILED
        order.save(update_fields=["status", "updated_at"])
        return {"skipped": True, "reason": "empty_order"}

    supplier = item.variant.product.supplier
    if not supplier.api_base_url:
        logger.info("supplier_forward_skipped_no_api", extra={"order": order.number})
        return {"skipped": True, "reason": "supplier_has_no_api"}

    payload = {
        "external_id": order.number,
        "ship_to": {
            "name": order.customer_name,
            "email": order.customer_email,
            "address": order.shipping_address,
        },
        "lines": [
            {"sku": line.sku, "quantity": line.quantity}
            for line in order.items.all()
        ],
    }
    response = httpx.post(
        f"{supplier.api_base_url.rstrip('/')}/orders",
        json=payload,
        timeout=30.0,
    )
    response.raise_for_status()
    body = response.json()
    with transaction.atomic():
        order.supplier_reference = str(body.get("id", ""))
        order.status = Order.Status.FORWARDED
        order.forwarded_at = timezone.now()
        order.save(update_fields=["supplier_reference", "status", "forwarded_at", "updated_at"])
    return {"order": order.number, "supplier_reference": order.supplier_reference}
