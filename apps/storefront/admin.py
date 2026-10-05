from django.contrib import admin

from .models import Bundle, BundleItem, StorefrontSettings


class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 0


@admin.register(StorefrontSettings)
class StorefrontSettingsAdmin(admin.ModelAdmin):
    list_display = ("tenant", "theme", "show_reviews", "show_bundles", "free_shipping_threshold")


@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "discount_percent", "is_active")
    inlines = (BundleItemInline,)
