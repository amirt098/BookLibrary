from django.db import models


class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('disabled', 'Disabled'),
    ]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    published_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    quantity = models.IntegerField()

    def __str__(self):
        return self.title
