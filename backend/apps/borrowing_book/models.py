from django.db import models
from django.utils import timezone


# Book Model
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    topic = models.CharField(max_length=100, null=True, blank=True)
    publisher = models.CharField(max_length=255, null=True, blank=True)
    date_published = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


# BorrowedBook Model
class BorrowedBook(models.Model):
    username = models.CharField(max_length=150)
    book_name = models.CharField(max_length=255)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()

    def __str__(self):
        return f'{self.book_name} borrowed by {self.username}'

    def is_overdue(self):
        return timezone.now() > self.due_date

    def calculate_penalty(self, penalty_rate_per_day):
        if self.is_overdue():
            days_overdue = (timezone.now() - self.due_date).days
            return days_overdue * penalty_rate_per_day
        return 0.0
