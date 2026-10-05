from __future__ import annotations

from rest_framework import serializers

from .models import Customer, Inquiry, RetentionTrigger


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "id",
            "name",
            "email",
            "loyalty_tier",
            "lifetime_value",
            "orders_count",
            "points",
            "last_order_at",
        )
        read_only_fields = fields


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = (
            "id",
            "customer_name",
            "customer_email",
            "subject",
            "body",
            "status",
            "channel",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: dict) -> Inquiry:
        tenant = self.context["request"].tenant
        email = validated_data["customer_email"].strip().lower()
        validated_data["customer_email"] = email
        customer = Customer.objects.filter(tenant=tenant, email=email).first()
        return Inquiry.objects.create(tenant=tenant, customer=customer, **validated_data)


class RetentionTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetentionTrigger
        fields = (
            "id",
            "name",
            "channel",
            "event",
            "is_enabled",
            "delay_hours",
            "template_preview",
            "updated_at",
        )
        read_only_fields = ("id", "updated_at")

    def create(self, validated_data: dict) -> RetentionTrigger:
        return RetentionTrigger.objects.create(tenant=self.context["request"].tenant, **validated_data)
