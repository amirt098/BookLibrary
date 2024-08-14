from logging import Logger

from apps.book import interfaces as book_interfaces
from utils.date_time import interfaces as date_time_interfaces
from apps.account import interfaces as account_interfaces

from models import BorrowBook
import interfaces

logger = Logger(__name__)


class BorrowBookService(interfaces.AbstractBorrowBook):

    def __init__(
            self,
            date_time: date_time_interfaces.AbstractDateTimeUtils,
            book_service: book_interfaces.AbstractBookService,
    ):
        self.date_time_util = date_time
        self.book_service = book_service

    def borrow_book(self, caller: account_interfaces.UserClaim, book_title: str):
        logger.info(f'caller: {caller}, book_title: {book_title}')
        try:
            borrow_book = self.book_service.get_book_info(caller=caller, book_title=book_title)
            logger.info(f'borrow_book: {borrow_book}')
        except book_interfaces.BookNotFound:
            logger.info(f'book not found')
            raise interfaces.BookNotFound(f'book with title: {book_title} not found')
        borrowed_books = BorrowBook.objects.filter(book_title=book_title).count()
        if borrow_book.quantity < borrowed_books:
            logger.info(f'')

        raise NotImplementedError

    def get_borrowed_books(self, caller: account_interfaces.UserClaim, filters: interfaces.BorrowedFilter) -> \
            interfaces.BorrowedBookList:

        raise NotImplementedError

    def postpone_borrowed_book(self, caller: account_interfaces.UserClaim, book_title: str, postponement_days: int):

        raise NotImplementedError

    def return_book(self, caller: account_interfaces.UserClaim, book_title: str):

        raise NotImplementedError
