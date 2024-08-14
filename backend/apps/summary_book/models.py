from django.db import models


class SummaryBook(models.Model):
    introducer = models.CharField(max_length=30)
    book = models.CharField(max_length=100)
    summary = models.TextField()
    wrote_at = models.BigIntegerField(null=True)