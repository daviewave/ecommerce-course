from django.contrib import admin

from .models import Account
from django.contrib.auth.admin import UserAdmin


class AccountAdmin(UserAdmin):
    # NOTE: 'list_display' controls the columns that are displayed inside the app on the django admin UI
    list_display = ('email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')

    # NOTE: 'list_display_links' controls the fields from list display that are clickable, and lead to more information
    list_display_links = ('email', 'first_name', 'last_name')

    # NOTE: 'readonly_fields' controls the admin fields that will not be allowed to be edited
    readonly_fields = ('last_login', 'date_joined')

    # NOTE: 'ordered' controls the order in which each instance of the model is listed on the django admin page
    ordered = ('-date_joined')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# register models
admin.site.register(Account, AccountAdmin)
