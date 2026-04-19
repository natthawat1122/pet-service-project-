from django.contrib import admin
from django.utils.html import format_html
from .models import Category, ServiceItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(ServiceItem)
class ServiceItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price', 'is_available', 'service_image_preview']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'is_available']

    def service_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit:cover; border-radius:8px;" />',
                obj.image.url
            )
        return "ไม่มีรูป"

    service_image_preview.short_description = 'รูปภาพ'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['service_item', 'quantity', 'price']
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'customer',
        'full_name',
        'phone',
        'pet_name',
        'pet_type',
        'booking_date',
        'payment_method',
        'payment_status',
        'status',
        'slip_preview',
        'created_at',
    ]
    list_filter = ['status', 'payment_method', 'payment_status', 'booking_date', 'created_at']
    search_fields = ['customer__username', 'full_name', 'phone', 'pet_name', 'pet_type', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'slip_preview']
    list_editable = ['payment_status', 'status']

    fieldsets = (
        ('ข้อมูลลูกค้า', {
            'fields': ('customer', 'full_name', 'phone', 'address')
        }),
        ('ข้อมูลสัตว์เลี้ยง', {
            'fields': ('pet_name', 'pet_type', 'booking_date')
        }),
        ('การชำระเงิน', {
            'fields': ('payment_method', 'payment_status', 'slip_image', 'slip_preview')
        }),
        ('สถานะคำสั่งซื้อ', {
            'fields': ('status', 'created_at')
        }),
    )

    def slip_preview(self, obj):
        if obj.slip_image:
            return format_html(
                '<a href="{0}" target="_blank"><img src="{0}" width="120" style="border-radius:10px; object-fit:cover;" /></a>',
                obj.slip_image.url
            )
        return "ไม่มีสลิป"

    slip_preview.short_description = 'สลิป'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'service_item', 'quantity', 'price']
    list_filter = ['service_item']
    search_fields = ['order__customer__username', 'service_item__name']