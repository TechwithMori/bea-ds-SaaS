"""Finance desk. Figures are computed from settled orders and recorded ad spend."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.money import money
from apps.marketing.models import AdSpend
from apps.orders.models import Order, OrderItem
from apps.tenants.mixins import WorkspaceMixin
from apps.tenants.permissions import IsTenantMember

MONEY = DecimalField(max_digits=14, decimal_places=2)
SETTLED = (
    Order.Status.PENDING,
    Order.Status.PAID,
    Order.Status.FORWARDED,
    Order.Status.FULFILLED,
)


class AnalyticsOverviewView(WorkspaceMixin, APIView):
    """Revenue, AOV, acquisition cost, and net margin for the active store."""

    permission_classes = (IsAuthenticated, IsTenantMember)

    def get(self, request: Request) -> Response:
        raw_days = request.query_params.get("days", "30")
        days = int(raw_days) if raw_days in {"7", "30", "90"} else 30
        since = timezone.now() - timedelta(days=days)
        tenant = request.tenant
        orders = Order.objects.filter(
            tenant=tenant,
            created_at__gte=since,
            status__in=SETTLED,
        )
        revenue = orders.aggregate(total=Sum("total"))["total"] or Decimal("0")
        order_count = orders.count()
        aov = (revenue / order_count) if order_count else Decimal("0")

        line_total = ExpressionWrapper(F("unit_cost") * F("quantity"), output_field=MONEY)
        cogs = (
            OrderItem.objects.filter(order__in=orders).aggregate(cost=Sum(line_total))["cost"]
            or Decimal("0")
        )
        spend_qs = AdSpend.objects.filter(tenant=tenant, spent_on__gte=since.date())
        ad_spend = spend_qs.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        gross_profit = revenue - cogs
        net_profit = gross_profit - ad_spend
        net_margin = (net_profit / revenue * Decimal(100)) if revenue else Decimal("0")
        new_customers = orders.values("customer_email").distinct().count()
        cac = (ad_spend / new_customers) if new_customers and ad_spend else None

        series_rows = (
            orders.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(revenue=Sum("total"), orders=Count("id"))
            .order_by("day")
        )
        product_revenue = ExpressionWrapper(F("unit_price") * F("quantity"), output_field=MONEY)
        top_rows = (
            OrderItem.objects.filter(order__in=orders)
            .values("title")
            .annotate(revenue=Sum(product_revenue), units=Sum("quantity"))
            .order_by("-revenue")[:5]
        )
        spend_rows = spend_qs.values("channel").annotate(amount=Sum("amount")).order_by("-amount")

        return Response(
            {
                "currency": tenant.currency,
                "days": days,
                "revenue": money(revenue),
                "order_count": order_count,
                "aov": money(aov),
                "cogs": money(cogs),
                "ad_spend": money(ad_spend),
                "gross_profit": money(gross_profit),
                "net_profit": money(net_profit),
                "net_margin_percent": f"{net_margin.quantize(Decimal('0.1'))}",
                "cac": money(cac) if cac is not None else None,
                "new_customers": new_customers,
                "series": [
                    {
                        "day": row["day"].isoformat(),
                        "revenue": money(row["revenue"]),
                        "orders": row["orders"],
                    }
                    for row in series_rows
                ],
                "spend_by_channel": [
                    {"channel": row["channel"], "amount": money(row["amount"])} for row in spend_rows
                ],
                "top_products": [
                    {
                        "title": row["title"],
                        "revenue": money(row["revenue"]),
                        "units": row["units"],
                    }
                    for row in top_rows
                ],
            }
        )
