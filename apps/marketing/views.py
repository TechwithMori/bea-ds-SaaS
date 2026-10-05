from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tenants.mixins import WorkspaceMixin
from apps.tenants.permissions import IsTenantMember

from .models import AdSpend, ChannelIntegration, ContentAsset, MarketingHook
from .serializers import (
    AdSpendSerializer,
    ChannelIntegrationSerializer,
    ContentAssetSerializer,
    MarketingHookSerializer,
)


class ContentAssetViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = ContentAssetSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return ContentAsset.objects.filter(tenant=self.request.tenant)


class MarketingHookViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = MarketingHookSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return MarketingHook.objects.filter(tenant=self.request.tenant)


class ChannelIntegrationViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = ChannelIntegrationSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return ChannelIntegration.objects.filter(tenant=self.request.tenant)


class AdSpendViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = AdSpendSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "delete", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return AdSpend.objects.filter(tenant=self.request.tenant)
