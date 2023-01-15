from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


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


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius: 50%;">'.format(object.profile_picture.url))

    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail', 'user', 'city', 'state', 'country')

# register models
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
