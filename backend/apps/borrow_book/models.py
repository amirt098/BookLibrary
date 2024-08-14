from django.db import models


class BorrowBook(models.Model):
    book_title = models.CharField(max_length=255)
    borrower_name = models.CharField(max_length=255)
    borrow_at = models.BigIntegerField()
    return_at = models.BigIntegerField(null=True)
    return_promise_at = models.BigIntegerField()

    def __str__(self):
        return f"{self.borrower_name} borrowed {self.book_title}"
