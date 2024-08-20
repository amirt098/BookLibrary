from enum import unique

from django.db import models


class OfferBook(models.Model):
    uid = models.CharField(max_length=150, unique=True, null=True)
    offered_book_title = models.CharField(max_length=30)
    topic = models.CharField(max_length=50, blank=True, null=True, unique=True)
    author = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    proposer = models.CharField(max_length=30)
    purchase_link = models.CharField(max_length=30, blank=True, null=True)
    is_purchased = models.BooleanField(default=False)
    offered_at = models.BigIntegerField()

    def __str__(self):
        return f'{self.offered_book_title}, {self.author}, {self.publisher} proposer: {self.proposer}'
