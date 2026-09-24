"""JWT authentication that also resolves the active store.

DRF authenticates inside the view, after Django middleware. Tenant ownership
checks therefore cannot live only in middleware: the session user is anonymous
on Bearer requests. This class runs SimpleJWT, then binds ``request.tenant``.
"""

from __future__ import annotations

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.authentication.models import User

from .models import Tenant


class TenantJWTAuthentication(JWTAuthentication):
    """Authenticate the merchant, then attach the store they are operating."""

    def authenticate(self, request: Request) -> tuple[User, object] | None:
        result = super().authenticate(request)
        if result is None:
            return None
        user, token = result
        request.tenant = resolve_tenant(request, user)
        return user, token


def resolve_tenant(request: Request, user: User) -> Tenant | None:
    """Return the store from ``X-Tenant-Slug``, else the owner's default store."""
    slug = request.headers.get("X-Tenant-Slug", "").strip().lower()
    if slug:
        tenant = Tenant.objects.filter(slug=slug).first()
        if tenant is None:
            return None
        if tenant.owner_id != user.id and not user.is_superuser:
            return None
        return tenant
    return Tenant.objects.filter(owner=user, is_default=True).first()
