"""Order API and the supplier status webhook."""

from __future__ import annotations

import hmac
from typing import Any

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.mixins import WorkspaceMixin
from apps.tenants.permissions import IsTenantMember

from .models import Order, ShippingRoute
from .serializers import OrderSerializer, ShippingRouteSerializer


class OrderViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    """Tenant-scoped orders. Create forwards fulfillment asynchronously."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Order.objects.filter(tenant=self.request.tenant)
            .select_related("shipping_route")
            .prefetch_related("items")
        )

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """Counts for the fulfillment board lanes."""
        qs = self.get_queryset()

        def count_for(*statuses: str) -> int:
            return qs.filter(status__in=statuses).count()

        return Response(
            {
                "pending": count_for(Order.Status.PENDING),
                "processing": count_for(Order.Status.PAID, Order.Status.FORWARDED),
                "shipped": count_for(Order.Status.FULFILLED),
                "exceptions": count_for(Order.Status.CANCELLED, Order.Status.FAILED),
            }
        )


class ShippingRouteViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    """Carrier lanes used to route a destination to a shipper."""

    serializer_class = ShippingRouteSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return ShippingRoute.objects.filter(tenant=self.request.tenant)


class SupplierFulfillmentWebhookView(APIView):
    """Receive tracking updates from a supplier.

    Authentication is a shared secret in ``X-Supplier-Signature``, compared in
    constant time. The payload identifies the order by ``external_id``.
    """

    authentication_classes: list[Any] = []
    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        expected = settings.SUPPLIER_WEBHOOK_SECRET
        provided = request.headers.get("X-Supplier-Signature", "")
        if not expected or not hmac.compare_digest(provided, expected):
            return Response({"detail": "Invalid signature."}, status=status.HTTP_401_UNAUTHORIZED)

        external_id = request.data.get("external_id")
        order = Order.objects.filter(number=external_id).first()
        if order is None:
            return Response({"detail": "Unknown order."}, status=status.HTTP_404_NOT_FOUND)

        order.tracking_carrier = request.data.get("carrier", order.tracking_carrier)
        order.tracking_number = request.data.get("tracking_number", order.tracking_number)
        order.tracking_url = request.data.get("tracking_url", order.tracking_url)
        incoming = request.data.get("status")
        if incoming in {Order.Status.FULFILLED, Order.Status.CANCELLED, Order.Status.FAILED}:
            order.status = incoming
            if incoming == Order.Status.FULFILLED:
                order.fulfilled_at = timezone.now()
        order.save()
        return Response({"number": order.number, "status": order.status})
