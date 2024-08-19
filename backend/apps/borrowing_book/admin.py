
from django.contrib import admin
from .models import Book, BorrowedBook


class BookAdmin(admin.ModelAdmin):
    list_display = "title", "writer", "quantity", "topic", "publisher"
    search_fields = ["title", "writer"]


class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = "username", "book_title", "borrowed_at", "return_at", "due_at"
    search_fields = ["username", "book_name"]


admin.site.register(Book, BookAdmin)
admin.site.register(BorrowedBook, BorrowedBookAdmin)
