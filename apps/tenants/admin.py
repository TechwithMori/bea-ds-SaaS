from django.contrib import admin

from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "owner", "status", "plan", "is_default")
    list_filter = ("status", "plan", "niche")
    search_fields = ("name", "slug", "custom_domain", "owner__email")
    readonly_fields = ("id", "created_at", "updated_at")
