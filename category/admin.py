from django.contrib import admin
from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields     = {'slug': ('category_name',)} # NOTE: in python if we declare a tuple with only 1 value, it must have a comma at the end
    list_display            = ('category_name', 'slug')

# Register models
admin.site.register(Category, CategoryAdmin)
