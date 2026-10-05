from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.tenants.mixins import WorkspaceMixin
from apps.tenants.permissions import IsTenantMember

from .models import Customer, Inquiry, RetentionTrigger
from .serializers import CustomerSerializer, InquirySerializer, RetentionTriggerSerializer


class CustomerViewSet(WorkspaceMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Customer.objects.filter(tenant=self.request.tenant)


class InquiryViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = InquirySerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Inquiry.objects.filter(tenant=self.request.tenant)


class RetentionTriggerViewSet(WorkspaceMixin, viewsets.ModelViewSet):
    serializer_class = RetentionTriggerSerializer
    permission_classes = (IsAuthenticated, IsTenantMember)
    pagination_class = None
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return RetentionTrigger.objects.filter(tenant=self.request.tenant)
