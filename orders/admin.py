from django.contrib import admin
from .models import Payment, Order, OrderProduct


class OrderAdmin(admin.ModelAdmin):
    list_display    = ['user', 'full_name', 'payment', 'order_number', 'status', 'is_ordered']
    list_filter     = ['status', 'is_ordered']
    search_fields   = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page   = 20

class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'account', 'order', 'payment']

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'payment_method', 'amount_paid', 'created_at', 'status']


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(Payment, PaymentAdmin) 