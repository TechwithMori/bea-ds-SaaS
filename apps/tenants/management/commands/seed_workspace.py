"""Load one active beauty store so every desk has live rows to read."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.customers.models import Inquiry
from apps.customers.services import record_order_customer
from apps.marketing.models import AdSpend, ChannelIntegration
from apps.orders.models import Order, OrderItem
from apps.orders.routing import assign_route
from apps.products.models import Product, ProductVariant, StoreProduct, Supplier
from apps.storefront.models import Bundle, BundleItem
from apps.tenants.models import Tenant
from apps.tenants.provision import ensure_store_defaults

User = get_user_model()

DEMO_EMAIL = "iris@lumenatelier.test"
DEMO_PASSWORD = "bea-drops-demo"


class Command(BaseCommand):
    help = "Create the Lumen Atelier demo store, catalog, orders, and desk records."

    def handle(self, *args: object, **options: object) -> None:
        user, created = User.objects.get_or_create(
            email=DEMO_EMAIL,
            defaults={"first_name": "Iris", "last_name": "Vale", "company_name": "Lumen Atelier"},
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save(update_fields=["password"])

        tenant, _tenant_created = Tenant.objects.get_or_create(
            slug="lumen-atelier",
            defaults={
                "owner": user,
                "name": "Lumen Atelier",
                "status": Tenant.Status.ACTIVE,
                "plan": Tenant.Plan.GROWTH,
                "currency": "USD",
                "niche": "beauty",
                "is_default": True,
            },
        )
        tenant.status = Tenant.Status.ACTIVE
        tenant.plan = Tenant.Plan.GROWTH
        tenant.save(update_fields=["status", "plan", "updated_at"])
        ensure_store_defaults(tenant)

        supplier, _created = Supplier.objects.get_or_create(
            code="north-glow",
            defaults={
                "name": "North Glow Labs",
                "contact_email": "hello@northglow.example",
                "is_active": True,
                "sync_status": Supplier.SyncStatus.OK,
                "last_synced_at": timezone.now(),
            },
        )
        supplier.sync_status = Supplier.SyncStatus.OK
        supplier.last_synced_at = timezone.now()
        supplier.save(update_fields=["sync_status", "last_synced_at", "updated_at"])

        catalog = [
            ("BEA-SERUM-01", "Calm Repair Serum", "skincare", "42.00", "78.00", 240, "compliant", "", ["niacinamide", "panthenol"]),
            ("BEA-CREAM-02", "Barrier Cream", "skincare", "28.00", "54.00", 180, "compliant", "", ["ceramides", "squalane"]),
            ("BEA-OIL-03", "Night Oil", "skincare", "31.00", "64.00", 40, "pending_review", "Fragrance allergen check open.", ["squalane", "rosehip"]),
            ("BEA-LIP-04", "Soft Lip Tint", "makeup", "9.50", "24.00", 320, "compliant", "", ["castor oil", "vitamin e"]),
            ("BEA-WASH-05", "Gel Cleanser", "skincare", "11.00", "28.00", 0, "restricted", "Hold: preservative system under review.", ["glycerin"]),
        ]
        variants = []
        for sku, title, category, wholesale, retail, stock, compliance, notes, ingredients in catalog:
            product, _created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    "supplier": supplier,
                    "supplier_sku": sku,
                    "title": title,
                    "category": category,
                    "brand": "North Glow",
                    "wholesale_price": Decimal(wholesale),
                    "suggested_retail_price": Decimal(retail),
                    "stock_level": stock,
                    "ingredients": ingredients,
                    "compliance_status": compliance,
                    "compliance_notes": notes,
                    "description": f"{title} from the vetted cosmetics bench.",
                },
            )
            variant, _created = ProductVariant.objects.get_or_create(
                sku=f"{sku}-30",
                defaults={
                    "product": product,
                    "name": "30 ml",
                    "wholesale_price": Decimal(wholesale),
                    "stock_level": stock,
                    "attributes": {"size": "30ml"},
                },
            )
            variants.append((variant, Decimal(retail)))

        listings = []
        for variant, retail in variants:
            listing, _created = StoreProduct.objects.get_or_create(
                tenant=tenant,
                variant=variant,
                defaults={"retail_price": retail, "is_published": variant.stock_level > 0},
            )
            listings.append(listing)

        if not Order.objects.filter(tenant=tenant).exists():
            self._orders(tenant, listings)

        if not AdSpend.objects.filter(tenant=tenant).exists():
            today = timezone.now().date()
            AdSpend.objects.bulk_create(
                [
                    AdSpend(tenant=tenant, channel="meta_ads", amount=Decimal("840.00"), spent_on=today - timedelta(days=6)),
                    AdSpend(tenant=tenant, channel="tiktok", amount=Decimal("420.00"), spent_on=today - timedelta(days=4)),
                    AdSpend(tenant=tenant, channel="google_ads", amount=Decimal("260.00"), spent_on=today - timedelta(days=2)),
                ]
            )

        ChannelIntegration.objects.filter(tenant=tenant, provider__in=["instagram", "klaviyo"]).update(
            status=ChannelIntegration.Status.CONNECTED,
            account_label="Lumen Atelier",
        )

        if not Inquiry.objects.filter(tenant=tenant).exists():
            Inquiry.objects.create(
                tenant=tenant,
                customer_name="Mara Ellison",
                customer_email="mara@example.com",
                subject="Is the serum fragrance-free?",
                body="I want the Calm Repair Serum but I react to added scent.",
                status=Inquiry.Status.OPEN,
                channel=Inquiry.Channel.EMAIL,
            )
            Inquiry.objects.create(
                tenant=tenant,
                customer_name="Jonah Park",
                customer_email="jonah@example.com",
                subject="Where is order BD tracking?",
                body="The shipping mail arrived, but the carrier page is empty.",
                status=Inquiry.Status.WAITING,
                channel=Inquiry.Channel.CHAT,
            )

        serum = next((row for row in listings if "SERUM" in row.variant.sku), None)
        cream = next((row for row in listings if "CREAM" in row.variant.sku), None)
        if serum and cream and not Bundle.objects.filter(tenant=tenant, name="Evening Sink Set").exists():
            bundle = Bundle.objects.create(
                tenant=tenant,
                name="Evening Sink Set",
                description="Serum and barrier cream, sequenced for the last ten minutes of the day.",
                discount_percent=Decimal("12.00"),
                is_active=True,
            )
            BundleItem.objects.bulk_create(
                [
                    BundleItem(bundle=bundle, store_product=serum, quantity=1),
                    BundleItem(bundle=bundle, store_product=cream, quantity=1),
                ]
            )

        self.stdout.write(self.style.SUCCESS(f"Workspace ready for {DEMO_EMAIL} / {DEMO_PASSWORD}"))

    def _orders(self, tenant: Tenant, listings: list[StoreProduct]) -> None:
        now = timezone.now()
        drafts = [
            ("Mara Ellison", "mara@example.com", "US", Order.Status.FULFILLED, 0, listings[0], 1),
            ("Jonah Park", "jonah@example.com", "US", Order.Status.FORWARDED, 1, listings[1], 1),
            ("Adele Costa", "adele@example.com", "FR", Order.Status.PAID, 3, listings[3], 2),
            ("Mara Ellison", "mara@example.com", "US", Order.Status.FULFILLED, 9, listings[0], 1),
            ("Noah Idris", "noah@example.com", "DE", Order.Status.PENDING, 2, listings[1], 1),
        ]
        sequence = Order.objects.filter(tenant=tenant).count()
        for name, email, country, status, days_ago, listing, quantity in drafts:
            sequence += 1
            order = Order.objects.create(
                tenant=tenant,
                number=f"BD-{str(tenant.id)[:8].upper()}-{sequence:06d}",
                status=status,
                customer_name=name,
                customer_email=email,
                shipping_address={"line1": "18 Mercer", "city": "New York", "country": country},
                currency="USD",
                shipping_route=assign_route(tenant, {"country": country}),
                shipping_total=Decimal("6.00"),
            )
            if status == Order.Status.FULFILLED:
                order.tracking_carrier = order.shipping_route.carrier if order.shipping_route_id else "USPS"
                order.tracking_number = f"TRK{sequence:06d}"
                order.fulfilled_at = now - timedelta(days=days_ago)
            OrderItem.objects.create(
                order=order,
                variant=listing.variant,
                sku=listing.variant.sku,
                title=listing.variant.product.title,
                quantity=quantity,
                unit_price=listing.retail_price,
                unit_cost=listing.variant.wholesale_price,
            )
            order.recalculate_totals()
            order.created_at = now - timedelta(days=days_ago)
            order.save()
            record_order_customer(order)
