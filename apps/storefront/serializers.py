from __future__ import annotations

from django.db import transaction
from rest_framework import serializers

from apps.products.models import StoreProduct

from .models import Bundle, BundleItem, StorefrontSettings


class StorefrontSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorefrontSettings
        fields = (
            "id",
            "theme",
            "font_pairing",
            "primary_color",
            "accent_color",
            "announcement",
            "show_reviews",
            "show_urgency",
            "show_bundles",
            "free_shipping_threshold",
            "updated_at",
        )
        read_only_fields = ("id", "updated_at")


class BundleItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    class Meta:
        model = BundleItem
        fields = ("id", "store_product", "quantity", "title")
        read_only_fields = fields

    def get_title(self, item: BundleItem) -> str:
        listing = item.store_product
        return listing.title_override or listing.variant.product.title


class BundleItemWriteSerializer(serializers.Serializer):
    store_product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class BundleSerializer(serializers.ModelSerializer):
    items = BundleItemSerializer(many=True, read_only=True)
    lines = BundleItemWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Bundle
        fields = (
            "id",
            "name",
            "description",
            "discount_percent",
            "is_active",
            "items",
            "lines",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs: dict) -> dict:
        lines = attrs.get("lines")
        if lines is None:
            return attrs
        tenant = self.context["request"].tenant
        listings = {
            row.id: row
            for row in StoreProduct.objects.filter(
                tenant=tenant,
                id__in=[line["store_product_id"] for line in lines],
            )
        }
        resolved = []
        for line in lines:
            listing = listings.get(line["store_product_id"])
            if listing is None:
                raise serializers.ValidationError(
                    {"lines": f"Unknown listing {line['store_product_id']}."}
                )
            resolved.append((listing, line["quantity"]))
        attrs["resolved_lines"] = resolved
        return attrs

    def create(self, validated_data: dict) -> Bundle:
        lines = validated_data.pop("resolved_lines", [])
        validated_data.pop("lines", None)
        tenant = self.context["request"].tenant
        with transaction.atomic():
            bundle = Bundle.objects.create(tenant=tenant, **validated_data)
            _write_items(bundle, lines)
        return bundle

    def update(self, instance: Bundle, validated_data: dict) -> Bundle:
        lines = validated_data.pop("resolved_lines", None)
        validated_data.pop("lines", None)
        with transaction.atomic():
            bundle = super().update(instance, validated_data)
            if lines is not None:
                bundle.items.all().delete()
                _write_items(bundle, lines)
        return bundle


def _write_items(bundle: Bundle, lines: list[tuple[StoreProduct, int]]) -> None:
    BundleItem.objects.bulk_create(
        [
            BundleItem(bundle=bundle, store_product=listing, quantity=quantity)
            for listing, quantity in lines
        ]
    )
