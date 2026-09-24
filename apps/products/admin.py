from django.contrib import admin

from .models import Product, ProductVariant, StoreProduct, Supplier


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active")
    search_fields = ("name", "code")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "sku", "category", "wholesale_price", "stock_level", "supplier")
    list_filter = ("category", "is_active", "supplier")
    search_fields = ("title", "sku", "brand", "supplier_sku")
    inlines = (ProductVariantInline,)


@admin.register(StoreProduct)
class StoreProductAdmin(admin.ModelAdmin):
    list_display = ("tenant", "variant", "retail_price", "is_published")
    list_filter = ("is_published",)
