from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = "username", "email", "password", "telegram_id", "first_name", "last_name", "mobile"
    search_fields = ["username", "telegram_id"]


admin.site.register(User, UserAdmin)