"""Order API and the supplier status webhook."""

from __future__ import annotations

import hmac
from typing import Any

from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.permissions import IsTenantMember

from .models import Order
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    """Tenant-scoped orders. Create forwards fulfillment asynchronously."""

    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    http_method_names = ("get", "post", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Order.objects.filter(tenant=self.request.tenant).prefetch_related("items")


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
