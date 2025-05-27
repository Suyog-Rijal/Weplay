from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class UserAdmin(BaseUserAdmin):
	model = CustomUser
	list_display = ('email', 'full_name', 'is_verified', 'is_staff', 'is_google_account', 'is_active')
	list_filter = ('is_verified', 'is_staff', 'is_google_account', 'is_active')
	search_fields = ('email', 'full_name')
	ordering = ('-created_at',)

	fieldsets = (
		(None, {'fields': ('email', 'full_name', 'password')}),
	)

	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_active')}),
	)

	readonly_fields = ('created_at', 'updated_at')

