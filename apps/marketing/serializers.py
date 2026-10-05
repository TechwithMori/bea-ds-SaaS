from __future__ import annotations

from rest_framework import serializers

from .models import AdSpend, ChannelIntegration, ContentAsset, MarketingHook


class ContentAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentAsset
        fields = (
            "id",
            "title",
            "kind",
            "status",
            "channel",
            "body",
            "asset_url",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: dict) -> ContentAsset:
        return ContentAsset.objects.create(tenant=self.context["request"].tenant, **validated_data)


class MarketingHookSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingHook
        fields = ("id", "headline", "angle", "platform", "status", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def create(self, validated_data: dict) -> MarketingHook:
        return MarketingHook.objects.create(tenant=self.context["request"].tenant, **validated_data)


class ChannelIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelIntegration
        fields = ("id", "provider", "status", "account_label", "updated_at")
        read_only_fields = ("id", "updated_at")

    def validate_provider(self, value: str) -> str:
        tenant = self.context["request"].tenant
        taken = ChannelIntegration.objects.filter(tenant=tenant, provider=value)
        if self.instance is not None:
            taken = taken.exclude(pk=self.instance.pk)
        if taken.exists():
            raise serializers.ValidationError("This channel is already on the desk.")
        return value

    def create(self, validated_data: dict) -> ChannelIntegration:
        return ChannelIntegration.objects.create(tenant=self.context["request"].tenant, **validated_data)


class AdSpendSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdSpend
        fields = ("id", "channel", "amount", "spent_on", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data: dict) -> AdSpend:
        return AdSpend.objects.create(tenant=self.context["request"].tenant, **validated_data)
