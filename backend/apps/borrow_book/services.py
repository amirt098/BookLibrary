from utils.date_time import interfaces as date_time_interfaces
from apps.account import interfaces as account_interfaces

from models import BorrowBook
import interfaces


class BorrowBookService(interfaces.AbstractBorrowBook):

    def __init__(
            self,
            date_time: date_time_interfaces.AbstractDateTimeUtils
    ):
        self.date_time_util = date_time

    def borrow_book(self, caller: account_interfaces.UserClaim, book_title: str):

        raise NotImplementedError

    def get_borrowed_books(self, caller: account_interfaces.UserClaim, filters: interfaces.BorrowedFilter) ->\
            interfaces.BorrowedBookList:

        raise NotImplementedError

    def postpone_borrowed_book(self, caller: account_interfaces.UserClaim, book_title: str, postponement_days: int):

        raise NotImplementedError

    def return_book(self, caller: account_interfaces.UserClaim, book_title: str):

        raise NotImplementedError
