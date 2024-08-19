from django.contrib import admin
from .models import Contact


class ContactAdmin(admin.ModelAdmin):
    list_display = "mobile", "chat_id", "status",
    search_fields = ["mobile", "chat_id", "status"]


admin.site.register(Contact, ContactAdmin)