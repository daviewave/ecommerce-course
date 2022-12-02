from django.contrib import admin
#-- my imports --#
from .models import Product

#NOTE: to populate the value for slug based on the input used for 'product_name' need to add the following class
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_name',)}
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    

# Register models
admin.site.register(Product, ProductAdmin)
