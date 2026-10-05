from __future__ import annotations

from rest_framework import serializers

from .models import Product, ProductVariant, StoreProduct, Supplier


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "name", "code", "is_active", "sync_status", "last_synced_at")


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "name",
            "sku",
            "attributes",
            "wholesale_price",
            "stock_level",
            "is_active",
        )


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, read_only=True)
    supplier = SupplierSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "sku",
            "category",
            "brand",
            "wholesale_price",
            "suggested_retail_price",
            "stock_level",
            "ingredients",
            "specifications",
            "compliance_status",
            "compliance_notes",
            "supplier",
            "variants",
            "is_active",
        )


class StoreProductSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.PrimaryKeyRelatedField(
        source="variant",
        queryset=ProductVariant.objects.filter(is_active=True),
        write_only=True,
    )

    class Meta:
        model = StoreProduct
        fields = (
            "id",
            "variant",
            "variant_id",
            "retail_price",
            "is_published",
            "title_override",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: dict) -> StoreProduct:
        return StoreProduct.objects.create(tenant=self.context["request"].tenant, **validated_data)
