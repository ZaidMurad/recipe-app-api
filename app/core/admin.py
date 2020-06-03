from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # importing the django default user admin
from django.utils.translation import gettext as _ # This is a recommended convention for converting strings in our python to human readable text. its useful if it gets pass through a translation engine to support multiple languages

from . import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id'] # order the users by id
    list_display = ['email', 'name'] # list them by email and name
    fieldsets = ( # to support our custom user model so that the edit page works. this defines the sections for the field sets in the create and edit pages. Each bracket in it is a section
        (None, {'fields': ('email', 'password')}), # the first arg is the title for the section
        (_('Personal Info'), {'fields': ('name',)}), # the comma at the end is mandatory
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important Dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

admin.site.register(models.User, UserAdmin)
