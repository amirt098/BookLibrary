from django.contrib import admin
from .models import OfferBook


class OfferBookAdmin(admin.ModelAdmin):
    list_display = ("offered_book_title",
                    "topic", "author", "publisher",
                    "proposer", "purchase_link", "is_purchased", "offered_at")

    search_fields = ["offered_book_title", "author" , "proposer", "is_purchased"]


admin.site.register(OfferBook, OfferBookAdmin)
