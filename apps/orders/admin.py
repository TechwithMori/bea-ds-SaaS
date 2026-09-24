from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("sku", "title", "quantity", "unit_price", "unit_cost")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "tenant", "status", "customer_email", "total", "tracking_number")
    list_filter = ("status", "currency")
    search_fields = ("number", "customer_email", "supplier_reference", "tracking_number")
    inlines = (OrderItemInline,)
    readonly_fields = ("id", "created_at", "updated_at")
