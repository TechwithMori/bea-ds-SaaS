"""Pick the shipping lane for an end-customer address."""

from __future__ import annotations

from apps.tenants.models import Tenant

from .models import ShippingRoute

EU_COUNTRIES = {
    "AT",
    "BE",
    "DE",
    "ES",
    "FR",
    "IE",
    "IT",
    "NL",
    "PT",
    "SE",
    "EU",
}


def assign_route(tenant: Tenant, address: dict | None) -> ShippingRoute | None:
    """Return the first active lane whose regions include the destination.

    A region value of ``ROW`` is the catch-all and is used only when nothing
    more specific matches.
    """
    country = str((address or {}).get("country") or "").strip().upper()
    routes = ShippingRoute.objects.filter(tenant=tenant, is_active=True).order_by("priority", "name")
    fallback: ShippingRoute | None = None
    for route in routes:
        regions = {str(region).upper() for region in (route.regions or [])}
        if "ROW" in regions:
            fallback = fallback or route
        if not country:
            continue
        if country in regions or (country in EU_COUNTRIES and "EU" in regions):
            return route
    return fallback
