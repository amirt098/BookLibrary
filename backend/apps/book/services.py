import logging
from .models import Book
import interfaces
from apps.account.interfaces import UserClaim

logger = logging.getLogger(__name__)


class BookService(interfaces.AbstractBookService):

    def add_new_book(self, caller: UserClaim, book: interfaces.BookInfo) -> interfaces.BookInfo:
        logger.info(f"add_new_book called with: {book}, by user: {caller.username}")

        try:
            existing_book = Book.objects.get(isbn=book.title)
            existing_book.quantity += book.quantity
            existing_book.save()
            logger.info(f"Existing book found, updated quantity: {existing_book.quantity}")
            return self._convert_book_to_dataclass(existing_book)

        except Book.DoesNotExist:
            new_book = Book.objects.create(
                title=book.title,
                author=book.author,
                publisher=book.publisher,
                published_date=book.published_date,
                status=book.status,
                quantity=book.quantity
            )
            logger.info(f"New book created with title: {new_book.title}")
            return self._convert_book_to_dataclass(new_book)

    def get_books(self, caller: UserClaim, filters: interfaces.BookFilter) -> interfaces.BookList:
        logger.info(f"get_books called with filters: {filters}, by user: {caller.username}")

        queryset = Book.objects.filter(**filters.as_dict()).order_by(filters.order_by)
        count = queryset.count()
        books_query = queryset[filters.offset: filters.offset + filters.limit]

        books_list = [self._convert_book_to_dataclass(book) for book in books_query]
        result = interfaces.BookList(result=books_list, count=count)

        logger.info(f"get_books returning {len(books_list)} books")
        return result

    def disable_book(self, caller: UserClaim, book_title: str) -> None:
        logger.info(f"disable_book called with book_title: {book_title}, by user: {caller.username}")

        try:
            book = Book.objects.get(title=book_title)
            book.status = 'disabled'
            book.save()
            logger.info(f"Book {book_title} disabled successfully.")
        except Book.DoesNotExist:
            logger.error(f"BookNotFound: No book found with title {book_title}")
            raise interfaces.BookNotFound(f"No book found with title {book_title}")

    def get_book_info(self, caller: UserClaim, book_title: str) -> interfaces.BookInfo:
        logger.info(f"get_book_info called with book_title: {book_title}, by user: {caller.username}")

        try:
            book = Book.objects.get(title=book_title)
            book_info = self._convert_book_to_dataclass(book)
            logger.info(f"Returning info for book: {book_title}")
            return book_info
        except Book.DoesNotExist:
            logger.error(f"BookNotFound: No book found with title {book_title}")
            raise interfaces.BookNotFound(f"No book found with title {book_title}")

    @staticmethod
    def _convert_book_to_dataclass(book: Book) -> interfaces.BookInfo:
        return interfaces.BookInfo(
            title=book.title,
            author=book.author,
            publisher=book.publisher,
            published_date=book.published_date,
            status=book.status,
            quantity=book.quantity,
        )

