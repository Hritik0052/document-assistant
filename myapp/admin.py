from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from myapp.models import Token, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone')}),
    )


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'is_verified', 'expired_at', 'created_at')
    search_fields = ('user__username', 'token')
