import logging
from datetime import datetime
from typing import List, override

from django.db import transaction

from utils.date_time import interfaces as date_time_interfaces

from .models import Book, BorrowedBook
from . import interfaces
from ..telegram_bot.interfaces import BotIdentifier

logger = logging.getLogger(__name__)


class LibraryFacade(interfaces.AbstractLibraryFacade):
    def __init__(
            self,
            date_time_utils: date_time_interfaces.AbstractDateTimeUtils,
            days_return_commitment: int = 7

    ):
        self.date_time_utils = date_time_utils
        self.days_return_commitment_in_milliseconds = days_return_commitment * 24 * 60 * 60 * 1000

    def add_book(self, input_data: interfaces.AddBookInput) -> interfaces.AddBookOutput:
        try:
            logger.info(f"Adding book with data: {input_data}")
            book, created = Book.objects.get_or_create(
                title=input_data.title,
                writer=input_data.writer,
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
                book = Book.objects.get(title=input_data.book_title)
                if book.quantity > 0:
                    book.quantity -= 1
                    book.save()
                    borrowed_book = BorrowedBook.objects.create(
                        username=input_data.username,
                        book_title=input_data.book_title,
                        borrowed_at=self.date_time_utils.get_current_timestamp(),
                        due_at=self.date_time_utils.get_current_timestamp() + self.days_return_commitment_in_milliseconds,

                    )
                    # penalty = borrowed_book.calculate_penalty(penalty_rate_per_day)
                    result = self._convert_borrowed_book_to_dataclass(borrowed_book)
                    logger.info(f"Book borrowed: {result}")
                    return result

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
            if filters.writer:
                books = books.filter(writer__contains=filters.writer)
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
            if filters.return_at__isnull:
                borrowed_books = borrowed_books.filter(return_at__isnull=filters.return_at__isnull)

            result = [
                (
                    self._convert_borrowed_book_to_dataclass(borrowed_book)
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
                borrowed_book = BorrowedBook.objects.get(book_title=input_data.borrowed_book_title,
                                                         username=input_data.username,
                                                         return_at__isnull=True
                                                         )
                book = Book.objects.get(title=borrowed_book.book_title)

                if book.quantity is not None:
                    book.quantity += 1
                    book.save()

                # penalty = borrowed_book.calculate_penalty(penalty_rate_per_day)
                borrowed_book.return_at = self.date_time_utils.get_current_timestamp()
                borrowed_book.save()

                logger.info(f"Book returned: {borrowed_book}")
                result = interfaces.ReturnBookOutput(
                    id=borrowed_book.id,
                    username=input_data.username,
                    book_title=borrowed_book.book_title,
                    return_at=borrowed_book.return_at,
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

    def get_borrowed_book_by_id(
            self,
            id: int,
    ) -> interfaces.BorrowBookOutput:
        try:
            borrowed_book = BorrowedBook.objects.get(id=id)
        except BorrowedBook.DoesNotExist:
            logger.info(f'borrowed book not found with id: {id}')
            raise interfaces.BorrowedBookNotFound(f"borrowed book not found with id: {id}'")
        result = self._convert_borrowed_book_to_dataclass(borrowed_book)
        logger.info(f'result: {result}')
        return result

    @staticmethod
    def _convert_book_to_book_info(book: Book) -> interfaces.BookInfo:
        return interfaces.BookInfo(
            title=book.title,
            id=book.id,
            writer=book.writer,
            quantity=book.quantity,
            topic=book.topic,
            publisher=book.publisher,
            date_published=str(book.date_published),
        )

    @staticmethod
    def _convert_borrowed_book_to_dataclass(borrowed_book: BorrowedBook) -> interfaces.BorrowBookOutput:
        return interfaces.BorrowBookOutput(
            id=borrowed_book.id,
            username=borrowed_book.username,
            book_title=borrowed_book.book_title,
            borrowed_at=borrowed_book.borrowed_at,
            return_at=borrowed_book.return_at,
            due_at=borrowed_book.due_at,
        )
