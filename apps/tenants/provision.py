"""Give every new store a working desk instead of an empty database."""

from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from apps.customers.models import RetentionTrigger
from apps.marketing.models import ChannelIntegration, ContentAsset, MarketingHook
from apps.orders.models import ShippingRoute
from apps.storefront.models import StorefrontSettings
from apps.tenants.models import Tenant

STARTER_HOOKS = (
    {
        "headline": "Your barrier cream, without the twelve-step lecture.",
        "angle": "routine",
        "platform": "instagram",
        "status": MarketingHook.Status.READY,
    },
    {
        "headline": "Three textures. One evening sink. Zero guesswork.",
        "angle": "bundle",
        "platform": "tiktok",
        "status": MarketingHook.Status.DRAFT,
    },
    {
        "headline": "The serum people finish — then write us about.",
        "angle": "social proof",
        "platform": "email",
        "status": MarketingHook.Status.DRAFT,
    },
)

STARTER_ASSETS = (
    {
        "title": "PDP hero — morning serum",
        "kind": ContentAsset.Kind.IMAGE,
        "status": ContentAsset.Status.DRAFT,
        "channel": "storefront",
        "body": "Close crop on glass, warm stone, one drop on the back of the hand.",
    },
    {
        "title": "UGC caption set",
        "kind": ContentAsset.Kind.COPY,
        "status": ContentAsset.Status.APPROVED,
        "channel": "tiktok",
        "body": "I replaced four bottles with this. Skin feels calm by Thursday.",
    },
)

STARTER_TRIGGERS = (
    {
        "name": "Welcome to the ritual",
        "channel": RetentionTrigger.Channel.EMAIL,
        "event": RetentionTrigger.Event.WELCOME,
        "is_enabled": True,
        "delay_hours": 0,
        "template_preview": "Thanks for joining. Here is how to start the first seven days.",
    },
    {
        "name": "Abandoned ritual",
        "channel": RetentionTrigger.Channel.EMAIL,
        "event": RetentionTrigger.Event.ABANDONED_CHECKOUT,
        "is_enabled": True,
        "delay_hours": 2,
        "template_preview": "Your routine is still waiting at the sink.",
    },
    {
        "name": "Post-purchase care",
        "channel": RetentionTrigger.Channel.SMS,
        "event": RetentionTrigger.Event.POST_PURCHASE,
        "is_enabled": True,
        "delay_hours": 24,
        "template_preview": "Your order is moving. Patch-test the serum the first night.",
    },
    {
        "name": "Win-back",
        "channel": RetentionTrigger.Channel.EMAIL,
        "event": RetentionTrigger.Event.WINBACK,
        "is_enabled": False,
        "delay_hours": 720,
        "template_preview": "It has been a while. Your insider points are still here.",
    },
)

STARTER_ROUTES = (
    {
        "name": "United States",
        "carrier": "USPS",
        "service_level": ShippingRoute.ServiceLevel.STANDARD,
        "regions": ["US"],
        "priority": 10,
    },
    {
        "name": "European Union",
        "carrier": "DHL",
        "service_level": ShippingRoute.ServiceLevel.EXPRESS,
        "regions": ["EU"],
        "priority": 20,
    },
    {
        "name": "Rest of world",
        "carrier": "DHL",
        "service_level": ShippingRoute.ServiceLevel.STANDARD,
        "regions": ["ROW"],
        "priority": 30,
    },
)


def ensure_store_defaults(tenant: Tenant) -> None:
    """Create starter marketing, shop, retention, and shipping records once."""
    settings = dict(tenant.settings or {})
    if settings.get("workspace_ready"):
        return
    with transaction.atomic():
        locked = Tenant.objects.select_for_update().get(pk=tenant.pk)
        settings = dict(locked.settings or {})
        if settings.get("workspace_ready"):
            tenant.settings = settings
            return
        _create_defaults(locked)
        settings["workspace_ready"] = True
        locked.settings = settings
        locked.save(update_fields=["settings", "updated_at"])
        tenant.settings = settings


def _create_defaults(tenant: Tenant) -> None:
    StorefrontSettings.objects.get_or_create(
        tenant=tenant,
        defaults={
            "theme": StorefrontSettings.Theme.ATELIER,
            "announcement": "Complimentary samples on orders over $75.",
            "free_shipping_threshold": Decimal("75.00"),
            "show_reviews": True,
            "show_urgency": False,
            "show_bundles": True,
        },
    )
    for provider in ChannelIntegration.Provider.values:
        ChannelIntegration.objects.get_or_create(tenant=tenant, provider=provider)
    for hook in STARTER_HOOKS:
        MarketingHook.objects.get_or_create(tenant=tenant, headline=hook["headline"], defaults=hook)
    for asset in STARTER_ASSETS:
        ContentAsset.objects.get_or_create(tenant=tenant, title=asset["title"], defaults=asset)
    for trigger in STARTER_TRIGGERS:
        RetentionTrigger.objects.get_or_create(tenant=tenant, name=trigger["name"], defaults=trigger)
    for route in STARTER_ROUTES:
        ShippingRoute.objects.get_or_create(tenant=tenant, name=route["name"], defaults=route)
