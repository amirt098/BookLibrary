from django.db import models


class OfferBook(models.Model):
    offered_book_title = models.CharField(max_length=30)
    topic = models.CharField(max_length=50, blank=True, null=True, unique=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    proposer = models.CharField(max_length=30)
    purchase_link = models.CharField(max_length=30, blank=True, null=True)
    is_purchased = models.BooleanField(default=False)

    def __str__(self):
        return self.offered_book_title
