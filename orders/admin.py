from django.contrib import admin
from .models import Payment, Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'account', 'product', 'quantity', 'product_price', 'is_ordered')

class OrderAdmin(admin.ModelAdmin):
    list_display    = ['user', 'full_name', 'payment', 'order_number', 'status', 'is_ordered']
    list_filter     = ['status', 'is_ordered']
    search_fields   = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page   = 20
    inlines         = [OrderProductInline]

# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ['payment_id', 'user', 'payment_method', 'amount_paid', 'created_at', 'status']


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
admin.site.register(Payment) 