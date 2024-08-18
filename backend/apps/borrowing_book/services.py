import logging
from datetime import datetime
from typing import List

from django.db import transaction
from django.utils import timezone

from models import Book, BorrowedBook
import interfaces

logger = logging.getLogger(__name__)


class LibraryFacade(interfaces.AbstractLibraryFacade):
    def __init__(self):
        pass

    def add_book(self, input_data: interfaces.AddBookInput) -> interfaces.AddBookOutput:
        try:
            logger.info(f"Adding book with data: {input_data}")
            book, created = Book.objects.get_or_create(
                title=input_data.title,
                author=input_data.author,
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
        except Book.DoesNotExist:
            logger.info(f'Book: {input_data.book_title} Not found')
            interfaces.BookNotFound(f'Book: {input_data.book_title} Not found')
        except Exception as e:
            logger.error(f"Failed to add book: {str(e)}")
            raise e

    def borrow_book(self, input_data: interfaces.BorrowBookInput,
                    penalty_rate_per_day=0.5) -> interfaces.BorrowBookOutput:
        try:
            with transaction.atomic():
                logger.info(f"Borrowing book with data: {input_data}")
                book = Book.objects.get(id=input_data.book_title)
                if book.quantity > 0:
                    book.quantity -= 1
                    book.save()
                    borrowed_book = BorrowedBook.objects.create(
                        username=input_data.username,
                        book_title=input_data.book_title,
                        due_date=input_data.due_date
                    )
                    penalty = borrowed_book.calculate_penalty(penalty_rate_per_day)
                    logger.info(f"Book borrowed: {borrowed_book} with penalty: {penalty}")
                    return interfaces.BorrowBookOutput(
                        id=borrowed_book.id,
                        username=input_data.username,
                        book_title=input_data.book_title,
                        borrowed_date=str(borrowed_book.borrowed_date),
                        due_date=str(borrowed_book.due_date),
                        penalty=penalty
                    )
                else:
                    logger.info(f'Book" {input_data.book_title} is not available')
                    raise interfaces.BookNotAvailableException("Book is not available")
        except Book.DoesNotExist:
            logger.info(f'Book: {input_data.book_title} Not found')
            interfaces.BookNotFound(f'Book: {input_data.book_title} Not found')

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
            if filters.book_title:
                borrowed_books = borrowed_books.filter(book_title=filters.book_title)
            if filters.borrowed_date:
                borrowed_books = borrowed_books.filter(
                    borrowed_date__date=datetime.strptime(filters.borrowed_date, '%Y-%m-%d').date()
                )

            result = [
                interfaces.BorrowBookOutput(
                    id=borrowed_book.id,
                    username=borrowed_book.username,
                    book_title=borrowed_book.book_title,
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
                borrowed_book = BorrowedBook.objects.get(title=input_data.borrowed_book_title)
                book = Book.objects.get(title=borrowed_book.book_title)

                if book.quantity is not None:
                    book.quantity += 1
                    book.save()

                penalty = borrowed_book.calculate_penalty(penalty_rate_per_day)
                borrowed_book.borrowed_date = datetime.now().date()
                borrowed_book.save()

                logger.info(f"Book returned: {borrowed_book} with penalty: {penalty}")
                result = interfaces.ReturnBookOutput(
                    id=borrowed_book.id,
                    username=input_data.username,
                    book_title=borrowed_book.book_title,
                    return_date=str(datetime.now().date()),
                    penalty=penalty
                )
                logger.info(f'result: {result}')
                return result

        except BorrowedBook.DoesNotExist:
            logger.error("Borrowed book record not found.")
            raise interfaces.BorrowedBookNotFound("Borrowed book record not found.")
        except Book.DoesNotExist:
            logger.error("Book record not found.")
            raise interfaces.BookNotFound("Book record not found.")
        except Exception as e:
            logger.error(f"Failed to return book: {str(e)}")
            raise e

    def get_book_by_title(
            self,
            book_title: str
    ) -> interfaces.BookInfo:
        try:
            book = Book.objects.get(title=book_title)
        except Book.DoesNotExist:
            logger.info(f'book not found with title: {book_title}')
            raise interfaces.BookNotFound(f'book not found with title: {book_title}')
        result = self._convert_book_to_book_info(book)
        logger.info(f'result: {result}')
        return result

    @staticmethod
    def _convert_book_to_book_info(book: Book) -> interfaces.BookInfo:
        return interfaces.BookInfo(
            title=book.title,
            id=book.id,
            author=book.author,
            quantity=book.quantity,
            topic=book.topic,
            publisher=book.publisher,
            date_published=str(book.date_published),
        )

