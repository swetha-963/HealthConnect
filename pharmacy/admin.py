from django.contrib import admin

from .models import Cart, CartItem, Category, Medicine, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active", "prescription_required")
    search_fields = ("name", "brand")
    list_editable = ("price", "stock", "is_active")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_id", "full_name", "total", "status", "created_at")
    list_filter = ("status", "payment_method")
    search_fields = ("order_id", "full_name", "email")
    inlines = [OrderItemInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "items_count", "subtotal")
    inlines = [CartItemInline]
