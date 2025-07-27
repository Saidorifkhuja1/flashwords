from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from .forms import UserCreationForm, UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = (
        'phone_number', 'email', 'name','bio', 'notification_token' ,'last_name', 'username',
        'role', 'status', 'is_verified', 'is_admin', 'is_superuser'
    )
    list_filter = ('is_admin', 'is_superuser', 'role', 'status', 'is_verified')

    fieldsets = (
        ('Personal info', {
            'fields': (
                'phone_number', 'email', 'name','bio','notification_token', 'last_name', 'username',
                'avatar', 'mini_avatar', 'role', 'status', 'is_verified', 'password'
            )
        }),
        ('Permissions', {'fields': ( 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'email', 'name', 'bio','notification_token','last_name', 'username',
                'avatar', 'mini_avatar', 'role', 'status', 'is_verified',
                'password1', 'password2', 'is_admin', 'is_superuser'
            ),
        }),
    )

    search_fields = ('phone_number', 'email', 'name', 'last_name', 'username')
    ordering = ('phone_number',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)
