
from django.contrib import admin
from .models import Book, BorrowedBook


class BookAdmin(admin.ModelAdmin):
    list_display = "title", "auther", "quantity", "topic", "publisher"
    search_fields = ["title", "auther"]


class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = "username", "book_name", "borrowed_date", "return_date", "due_date"
    search_fields = ["username", "book_name"]


admin.site.register(Book, BookAdmin)
admin.site.register(BorrowedBook, BorrowedBookAdmin)
