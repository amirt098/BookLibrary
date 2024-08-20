from django.contrib import admin
from .models import Contact, Process, Field


class ContactAdmin(admin.ModelAdmin):
    list_display = "mobile", "chat_id", "status",
    search_fields = ["mobile", "chat_id", "status"]

class ProcessAdmin(admin.ModelAdmin):
    list_display = "uid", "type", "status", "step_counter",
    search_fields = ["mobile", "chat_id", "status"]

class FieldAdmin(admin.ModelAdmin):
    list_display = "name", "value", "process",
    search_fields = ["name", "value", "process"]


admin.site.register(Contact, ContactAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Field, FieldAdmin)