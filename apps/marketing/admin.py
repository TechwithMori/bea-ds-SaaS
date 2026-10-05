from django.contrib import admin

from .models import AdSpend, ChannelIntegration, ContentAsset, MarketingHook


@admin.register(ContentAsset)
class ContentAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "tenant", "kind", "status", "channel")
    list_filter = ("kind", "status", "channel")


@admin.register(MarketingHook)
class MarketingHookAdmin(admin.ModelAdmin):
    list_display = ("headline", "tenant", "platform", "status")
    list_filter = ("platform", "status")


@admin.register(ChannelIntegration)
class ChannelIntegrationAdmin(admin.ModelAdmin):
    list_display = ("provider", "tenant", "status", "account_label")
    list_filter = ("provider", "status")


@admin.register(AdSpend)
class AdSpendAdmin(admin.ModelAdmin):
    list_display = ("tenant", "channel", "amount", "spent_on")
    list_filter = ("channel",)
