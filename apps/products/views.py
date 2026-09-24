from __future__ import annotations

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tenants.permissions import IsTenantMember

from .models import Product, StoreProduct
from .serializers import ProductSerializer, StoreProductSerializer


class CatalogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Read-only global cosmetic catalog. Not tenant-owned."""

    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Product.objects.filter(is_active=True).select_related("supplier").prefetch_related("variants")


class StoreProductViewSet(viewsets.ModelViewSet):
    """Listings published by the active store."""

    serializer_class = StoreProductSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            StoreProduct.objects.filter(tenant=self.request.tenant)
            .select_related("variant", "variant__product")
        )
