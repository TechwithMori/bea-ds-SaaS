"""DRF permission that refuses cross-tenant access."""

from __future__ import annotations

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView


class IsTenantMember(BasePermission):
    """Allow the request only when middleware resolved a store the user owns."""

    message = "A valid store context is required."

    def has_permission(self, request: Request, view: APIView) -> bool:
        tenant = getattr(request, "tenant", None)
        user = request.user
        if tenant is None or not user.is_authenticated:
            return False
        if tenant.status == tenant.Status.SUSPENDED and request.method not in {"GET", "HEAD", "OPTIONS"}:
            return False
        return bool(user.is_superuser or tenant.owner_id == user.id)
