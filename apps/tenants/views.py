"""Store lifecycle endpoints for the authenticated merchant."""

from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Tenant
from .serializers import TenantSerializer


class TenantViewSet(viewsets.ModelViewSet):
    """CRUD for stores owned by the current user. Creation does not need a tenant header."""

    serializer_class = TenantSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "slug"
    http_method_names = ("get", "post", "patch", "head", "options")

    def get_queryset(self):  # type: ignore[no-untyped-def]
        return Tenant.objects.filter(owner=self.request.user)
