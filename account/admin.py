from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.models import Group as DefaultGroup
from .models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = [
        'username',
        'email',
        'account',
        'first_name',
        'last_name',
        'middle_name',
        'age',
        'gender',
        'is_active',
        'date_joined',
    ]
    list_filter = [
        'is_active',
        'is_staff',
        'gender',
    ]
  


admin.site.unregister(DefaultGroup)
admin.site.register(Group)

