from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.transaction import on_commit
from rest_framework import serializers

from apps.customers.services import record_order_customer
from apps.products.models import StoreProduct

from .models import Order, OrderItem, ShippingRoute
from .routing import assign_route
from .tasks import forward_order_to_supplier


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "sku", "title", "quantity", "unit_price", "unit_cost", "line_total")
        read_only_fields = fields


class OrderItemWriteSerializer(serializers.Serializer):
    store_product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    lines = OrderItemWriteSerializer(many=True, write_only=True)
    route_name = serializers.SerializerMethodField()
    route_carrier = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "status",
            "customer_name",
            "customer_email",
            "shipping_address",
            "currency",
            "subtotal",
            "shipping_total",
            "total",
            "supplier_reference",
            "tracking_carrier",
            "tracking_number",
            "tracking_url",
            "forwarded_at",
            "fulfilled_at",
            "items",
            "lines",
            "route_name",
            "route_carrier",
            "created_at",
        )
        read_only_fields = (
            "id",
            "number",
            "status",
            "subtotal",
            "total",
            "supplier_reference",
            "tracking_carrier",
            "tracking_number",
            "tracking_url",
            "forwarded_at",
            "fulfilled_at",
            "route_name",
            "route_carrier",
            "created_at",
        )

    def validate(self, attrs: dict) -> dict:
        tenant = getattr(self.context["request"], "tenant", None)
        if tenant is None or not tenant.can_sell:
            raise serializers.ValidationError("This store cannot accept orders.")
        listings = {
            str(row.id): row
            for row in StoreProduct.objects.filter(
                tenant=tenant,
                is_published=True,
                id__in=[line["store_product_id"] for line in attrs["lines"]],
            ).select_related("variant", "variant__product")
        }
        resolved: list[tuple[StoreProduct, int]] = []
        for line in attrs["lines"]:
            listing = listings.get(str(line["store_product_id"]))
            if listing is None:
                raise serializers.ValidationError(
                    {"lines": f"Unknown or unpublished listing {line['store_product_id']}."}
                )
            if listing.variant.stock_level < line["quantity"]:
                raise serializers.ValidationError(
                    {"lines": f"{listing.variant.sku} does not have enough stock."}
                )
            resolved.append((listing, line["quantity"]))
        attrs["resolved_lines"] = resolved
        return attrs

    def create(self, validated_data: dict) -> Order:
        lines: list[tuple[StoreProduct, int]] = validated_data.pop("resolved_lines")
        validated_data.pop("lines")
        tenant = self.context["request"].tenant
        validated_data["currency"] = tenant.currency
        with transaction.atomic():
            order = Order.objects.create(
                tenant=tenant,
                number=self._next_number(tenant.id),
                status=Order.Status.PAID,
                shipping_route=assign_route(tenant, validated_data.get("shipping_address")),
                **validated_data,
            )
            OrderItem.objects.bulk_create(
                [
                    OrderItem(
                        order=order,
                        variant=listing.variant,
                        sku=listing.variant.sku,
                        title=listing.title_override or listing.variant.product.title,
                        quantity=quantity,
                        unit_price=listing.retail_price,
                        unit_cost=listing.variant.wholesale_price,
                    )
                    for listing, quantity in lines
                ]
            )
            order.recalculate_totals()
            order.save(update_fields=["subtotal", "total", "updated_at"])
            record_order_customer(order)
        on_commit(lambda: forward_order_to_supplier.delay(str(order.id)))
        return order

    def get_route_name(self, order: Order) -> str:
        return order.shipping_route.name if order.shipping_route_id else ""

    def get_route_carrier(self, order: Order) -> str:
        return order.shipping_route.carrier if order.shipping_route_id else ""

    @staticmethod
    def _next_number(tenant_id: object) -> str:
        count = Order.objects.filter(tenant_id=tenant_id).count() + 1
        return f"BD-{str(tenant_id)[:8].upper()}-{count:06d}"

    def to_representation(self, instance: Order) -> dict:
        data = super().to_representation(instance)
        data["total"] = str(Decimal(data["total"]))
        return data


class ShippingRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingRoute
        fields = (
            "id",
            "name",
            "carrier",
            "service_level",
            "regions",
            "priority",
            "is_active",
            "updated_at",
        )
        read_only_fields = ("id", "updated_at")

    def create(self, validated_data: dict) -> ShippingRoute:
        return ShippingRoute.objects.create(tenant=self.context["request"].tenant, **validated_data)
