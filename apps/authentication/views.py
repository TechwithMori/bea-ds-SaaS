"""Registration and current-user endpoints. Token issue/refresh come from SimpleJWT."""

from __future__ import annotations

from rest_framework import generics, permissions
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""

    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class MeView(generics.RetrieveAPIView):
    """GET /api/v1/auth/me/"""

    serializer_class = UserSerializer

    def get_object(self):  # type: ignore[no-untyped-def]
        return self.request.user

    def retrieve(self, request: Request, *args: object, **kwargs: object) -> Response:
        return Response(self.get_serializer(request.user).data)
