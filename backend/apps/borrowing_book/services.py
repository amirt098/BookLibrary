import logging
from datetime import datetime
from typing import List

from django.db import transaction
from django.utils import timezone

from models import Book, BorrowedBook
import interfaces

logger = logging.getLogger(__name__)

class LibraryFacade:
    def __init__(self):
        pass

    def add_book(self, input_data: interfaces.AddBookInput) -> interfaces.AddBookOutput:
        try:
            logger.info(f"Adding book with data: {input_data}")
            book, created = Book.objects.get_or_create(
                title=input_data.title,
                author=input_data.author,
                isbn=input_data.isbn,
                defaults={
                    'quantity': input_data.quantity,
                    'topic': input_data.topic,
                    'publisher': input_data.publisher,
                    'date_published': input_data.date_published
                }
            )
            if not created:
                book.quantity += input_data.quantity
                book.save()
            logger.info(f"Book added: {book}")
            return interfaces.AddBookOutput(
                id=book.id,
                title=book.title,
                quantity=book.quantity,
                topic=book.topic,
                publisher=book.publisher,
                date_published=str(book.date_published) if book.date_published else None
            )
        except Exception as e:
            logger.error(f"Failed to add book: {str(e)}")
            raise e

    def borrow_book(self, input_data: interfaces.BorrowBookInput, penalty_rate_per_day=0.5) -> interfaces.BorrowBookOutput:
        try:
            with transaction.atomic():
                logger.info(f"Borrowing book with data: {input_data}")
                book = Book.objects.get(id=input_data.book_id)
                if book.quantity > 0:
                    book.quantity -= 1
                    book.save()
                    borrowed_book = BorrowedBook.objects.create(
                        username=input_data.username,
                        book_id=input_data.book_id,
                        due_date=input_data.due_date
                    )
                    penalty = borrowed_book.calculate_penalty(penalty_rate_per_day)
                    logger.info(f"Book borrowed: {borrowed_book} with penalty: {penalty}")
                    return interfaces.BorrowBookOutput(
                        id=borrowed_book.id,
                        username=input_data.username,
                        book_id=input_data.book_id,
                        borrowed_date=str(borrowed_book.borrowed_date),
                        due_date=str(borrowed_book.due_date),
                        penalty=penalty
                    )
                else:
                    raise ValueError("Book is not available")
        except Exception as e:
            logger.error(f"Failed to borrow book: {str(e)}")
            raise e

    def get_books(self, filters: interfaces.BookFilter) -> List[interfaces.AddBookOutput]:
        try:
            logger.info(f"Fetching books with filters: {filters}")
            books = Book.objects.all()

            if filters.title:
                books = books.filter(title__contains=filters.title)
            if filters.author:
                books = books.filter(author__contains=filters.author)
            if filters.isbn:
                books = books.filter(isbn=filters.isbn)
            if filters.topic:
                books = books.filter(topic__contains=filters.topic)
            if filters.publisher:
                books = books.filter(publisher__contains=filters.publisher)
            if filters.date_published:
                books = books.filter(date_published=filters.date_published)

            result = [
                interfaces.AddBookOutput(
                    id=book.id,
                    title=book.title,
                    quantity=book.quantity,
                    topic=book.topic,
                    publisher=book.publisher,
                    date_published=str(book.date_published) if book.date_published else None
                ) for book in books
            ]
            logger.info(f"Books fetched: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch books: {str(e)}")
            raise e

    def get_borrowed_books(self, filters: interfaces.BorrowedBookFilter) -> List[interfaces.BorrowBookOutput]:
        try:
            logger.info(f"Fetching borrowed books with filters: {filters}")
            borrowed_books = BorrowedBook.objects.all()

            if filters.username:
                borrowed_books = borrowed_books.filter(username=filters.username)
            if filters.book_id:
                borrowed_books = borrowed_books.filter(book_id=filters.book_id)
            if filters.borrowed_date:
                borrowed_books = borrowed_books.filter(
                    borrowed_date__date=datetime.strptime(filters.borrowed_date, '%Y-%m-%d').date()
                )

            result = [
                interfaces.BorrowBookOutput(
                    id=borrowed_book.id,
                    username=borrowed_book.username,
                    book_id=borrowed_book.book_name,
                    borrowed_date=str(borrowed_book.borrowed_date),
                    due_date=str(borrowed_book.due_date),
                    penalty=borrowed_book.calculate_penalty(penalty_rate_per_day=0.5)
                ) for borrowed_book in borrowed_books
            ]
            logger.info(f"Borrowed books fetched: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch borrowed books: {str(e)}")
            raise e

    def return_book(self, input_data: interfaces.ReturnBookInput,
                    penalty_rate_per_day=0.5) -> interfaces.ReturnBookOutput:
        try:
            with transaction.atomic():
                logger.info(f"Returning book with data: {input_data}")
                borrowed_book = BorrowedBook.objects.get(id=input_data.borrowed_book_id)
                book = Book.objects.get(id=borrowed_book.book_name)

                if book.quantity is not None:
                    book.quantity += 1
                    book.save()

                penalty = borrowed_book.calculate_penalty(penalty_rate_per_day)
                borrowed_book.borrowed_date = datetime.now().date()
                borrowed_book.save()

                logger.info(f"Book returned: {borrowed_book} with penalty: {penalty}")
                return interfaces.ReturnBookOutput(
                    id=borrowed_book.id,
                    username=input_data.username,
                    book_id=borrowed_book.book_name,
                    return_date=str(datetime.now().date()),
                    penalty=penalty
                )
        except BorrowedBook.DoesNotExist:
            logger.error("Borrowed book record not found.")
            raise ValueError("Borrowed book record not found.")
        except Book.DoesNotExist:
            logger.error("Book record not found.")
            raise ValueError("Book record not found.")
        except Exception as e:
            logger.error(f"Failed to return book: {str(e)}")
            raise e
