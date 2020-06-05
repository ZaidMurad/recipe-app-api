from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # importing the django default user admin
from django.utils.translation import gettext as _ # This is a recommended convention for converting strings in our python to human readable text (it makes django project translatable). its useful if it gets pass through a translation engine to support multiple languages

from . import models

class UserAdmin(BaseUserAdmin):
    ordering = ['id'] # order the objects by id
    list_display = ['email', 'name'] # list users by email and name
    fieldsets = ( # to support our custom user model so that the edit page works. this defines the sections for the field sets in the create and edit pages. Each bracket in it is a section
        (None, {'fields': ('email', 'password')}), # the first arg is the title for the section (None here)
        (_('Personal Info'), {'fields': ('name',)}), # the comma at the end is mandatory, without it it will think of it as a string and won't work
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important Dates'), {'fields': ('last_login',)}), # we can add things like logout or last seen here too
    )
    add_fieldsets = ( # to support the add page (for adding new users). The user admin by default takes an add_fieldsets which defines the fields that you include in the create user page
        (None, {
            'classes': ('wide',), # the classes that are assigned to the form (we used the default which is only wide class)
            'fields': ('email', 'password1', 'password2'),
        }), # the comma is mandatory since we have only one item
    )

admin.site.register(models.User, UserAdmin)
