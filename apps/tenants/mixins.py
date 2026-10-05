"""View mixin that prepares a store the first time a desk is opened."""

from __future__ import annotations

from rest_framework.request import Request

from .provision import ensure_store_defaults


class WorkspaceMixin:
    """Call ``ensure_store_defaults`` after authentication has resolved the store."""

    def initial(self, request: Request, *args: object, **kwargs: object) -> None:
        super().initial(request, *args, **kwargs)  # type: ignore[misc]
        tenant = getattr(request, "tenant", None)
        if tenant is not None and request.user.is_authenticated:
            ensure_store_defaults(tenant)
