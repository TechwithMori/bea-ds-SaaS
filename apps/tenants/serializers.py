from __future__ import annotations

from rest_framework import serializers

from .models import Tenant
from .provision import ensure_store_defaults


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = (
            "id",
            "name",
            "slug",
            "status",
            "plan",
            "custom_domain",
            "currency",
            "niche",
            "settings",
            "is_default",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "plan", "created_at", "updated_at")
        extra_kwargs = {
            "settings": {"required": False},
            "slug": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data: dict) -> Tenant:
        owner = self.context["request"].user
        is_first = not Tenant.objects.filter(owner=owner).exists()
        validated_data.setdefault("is_default", is_first)
        tenant = Tenant.objects.create(owner=owner, **validated_data)
        ensure_store_defaults(tenant)
        return tenant
