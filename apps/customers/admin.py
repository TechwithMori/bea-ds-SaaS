from django.contrib import admin

from .models import Customer, Inquiry, RetentionTrigger


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("email", "tenant", "loyalty_tier", "lifetime_value", "orders_count")
    search_fields = ("email", "name")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("subject", "tenant", "status", "channel", "customer_email")
    list_filter = ("status", "channel")


@admin.register(RetentionTrigger)
class RetentionTriggerAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "channel", "event", "is_enabled")
    list_filter = ("channel", "event", "is_enabled")
