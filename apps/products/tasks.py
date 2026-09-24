"""Inventory sync jobs. The worker polls suppliers and writes stock back to the catalog."""

from __future__ import annotations

import logging

import httpx
from celery import shared_task
from django.db import transaction

from .models import Product, Supplier

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(httpx.HTTPError,), retry_backoff=True, max_retries=5)
def sync_supplier_inventory(self, supplier_code: str | None = None) -> dict[str, int]:
    """Pull stock levels from active suppliers and update catalog rows.

    Expected supplier payload::

        {"items": [{"sku": "BEA-001", "stock_level": 42}]}

    Suppliers without an API base URL are skipped so local development does not
    fail closed.
    """
    suppliers = Supplier.objects.filter(is_active=True).exclude(api_base_url="")
    if supplier_code:
        suppliers = suppliers.filter(code=supplier_code)

    updated = 0
    for supplier in suppliers:
        updated += _sync_one(supplier)
    logger.info("inventory_sync_complete", extra={"updated": updated})
    return {"updated": updated}


def _sync_one(supplier: Supplier) -> int:
    url = f"{supplier.api_base_url.rstrip('/')}/inventory"
    response = httpx.get(url, timeout=20.0)
    response.raise_for_status()
    payload = response.json()
    items = payload.get("items", [])
    count = 0
    with transaction.atomic():
        for item in items:
            sku = item.get("sku")
            stock = item.get("stock_level")
            if not sku or stock is None:
                continue
            count += Product.objects.filter(supplier=supplier, sku=sku).update(stock_level=int(stock))
    return count
