from __future__ import annotations

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.mixins import WorkspaceMixin
from apps.tenants.permissions import IsTenantMember

from .models import Product, StoreProduct
from .serializers import ProductSerializer, StoreProductSerializer
from .sourcing import sourcing_overview


class CatalogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Read-only global cosmetic catalog. Not tenant-owned."""

    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.filter(is_active=True).select_related("supplier").prefetch_related("variants")


class SourcingOverviewView(WorkspaceMixin, APIView):
    """Margins, ingredient compliance, and supplier sync for the sourcing desk."""

    permission_classes = (IsAuthenticated, IsTenantMember)

    def get(self, request: Request) -> Response:
        return Response(sourcing_overview(request.tenant))


class StoreProductViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    """Listings published by the active store."""

    serializer_class = StoreProductSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            StoreProduct.objects.filter(tenant=self.request.tenant)
            .select_related("variant", "variant__product")
        )
