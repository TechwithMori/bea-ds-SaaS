"""Read model for the sourcing desk: margins, compliance, and supplier sync."""

from __future__ import annotations

from apps.common.money import margin_percent, money
from apps.tenants.models import Tenant

from .models import Product, StoreProduct, Supplier


def sourcing_overview(tenant: Tenant | None) -> dict:
    products = (
        Product.objects.filter(is_active=True)
        .select_related("supplier")
        .order_by("title")[:100]
    )
    catalog = [_catalog_row(product) for product in products]
    compliance = {
        "compliant": 0,
        "pending_review": 0,
        "restricted": 0,
    }
    for row in catalog:
        compliance[row["compliance_status"]] = compliance.get(row["compliance_status"], 0) + 1

    suppliers = [
        {
            "id": str(supplier.id),
            "name": supplier.name,
            "code": supplier.code,
            "is_active": supplier.is_active,
            "sync_status": supplier.sync_status,
            "last_synced_at": supplier.last_synced_at.isoformat() if supplier.last_synced_at else None,
        }
        for supplier in Supplier.objects.order_by("name")
    ]
    listings = []
    if tenant is not None:
        stored = (
            StoreProduct.objects.filter(tenant=tenant)
            .select_related("variant", "variant__product", "variant__product__supplier")
            .order_by("-created_at")
        )
        listings = [_listing_row(listing) for listing in stored]
    return {
        "suppliers": suppliers,
        "compliance": compliance,
        "catalog": catalog,
        "listings": listings,
    }


def _catalog_row(product: Product) -> dict:
    return {
        "id": str(product.id),
        "title": product.title,
        "sku": product.sku,
        "category": product.category,
        "brand": product.brand,
        "wholesale_price": money(product.wholesale_price),
        "suggested_retail_price": money(product.suggested_retail_price),
        "margin_percent": margin_percent(product.suggested_retail_price, product.wholesale_price),
        "stock_level": product.stock_level,
        "compliance_status": product.compliance_status,
        "compliance_notes": product.compliance_notes,
        "ingredients": product.ingredients,
        "supplier_name": product.supplier.name,
        "sync_status": product.supplier.sync_status,
    }


def _listing_row(listing: StoreProduct) -> dict:
    variant = listing.variant
    product = variant.product
    return {
        "id": str(listing.id),
        "title": listing.title_override or product.title,
        "variant_name": variant.name,
        "sku": variant.sku,
        "category": product.category,
        "wholesale_price": money(variant.wholesale_price),
        "retail_price": money(listing.retail_price),
        "margin_percent": margin_percent(listing.retail_price, variant.wholesale_price),
        "stock_level": variant.stock_level,
        "is_published": listing.is_published,
        "compliance_status": product.compliance_status,
        "supplier_name": product.supplier.name,
        "sync_status": product.supplier.sync_status,
    }
