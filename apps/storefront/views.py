from __future__ import annotations

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tenants.mixins import WorkspaceMixin
from apps.tenants.permissions import IsTenantMember

from .models import Bundle, StorefrontSettings
from .serializers import BundleSerializer, StorefrontSettingsSerializer


class StorefrontSettingsView(WorkspaceMixin, generics.RetrieveUpdateAPIView):
    """The single shop configuration for the active store."""

    serializer_class = StorefrontSettingsSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    http_method_names = ("get", "patch", "head", "options")

    def get_object(self) -> StorefrontSettings:  # type: ignore[override]
        settings, _created = StorefrontSettings.objects.get_or_create(tenant=self.request.tenant)
        return settings


class BundleViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = BundleSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return (
            Bundle.objects.filter(tenant=self.request.tenant)
            .prefetch_related("items__store_product__variant__product")
        )
