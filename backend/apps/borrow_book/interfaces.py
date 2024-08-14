import abc
from typing import List

from lib import data_classes as lib_dataclasses
from apps.account import interfaces as account_interfaces
from utils.date_time.interfaces import DateTime


class BorrowedFilter(lib_dataclasses.BaseFilter):
    book_title__contains: str | None = None
    author__contains: str | None = None
    publisher__contains: str | None = None
    published_at__gte: int | None = None
    published_at__lte: int | None = None
    quantity_at__gte: int | None = None


class BorrowedBook(lib_dataclasses.BaseModel):
    title: str
    author: str | None = None
    publisher: str | None = None
    published_date: DateTime | None = None
    status: str
    quantity: int


class BorrowedBookList(lib_dataclasses.BaseModel):
    result: List[BorrowedBook]
    count: int


class BookNotFound(Exception):
    pass


class AbstractBorrowBook(abc.ABC):

    def borrow_book(self, caller: account_interfaces.UserClaim, book_title: str):
        """
        Raise:
            BookNotAvailable
            BookNotFound
        """
        raise NotImplementedError

    def get_borrowed_books(self, caller: account_interfaces.UserClaim, filters: BorrowedFilter) -> BorrowedBookList:
        """

        """
        raise NotImplementedError

    def postpone_borrowed_book(self, caller: account_interfaces.UserClaim, book_title: str, postponement_days: int):
        """
        Raise:
            NotFoundBook
            BookNotBorrowed
        """
        raise NotImplementedError

    def return_book(self, caller: account_interfaces.UserClaim, book_title: str):
        """
        Calculate the delay penalty and what?

        Raise:
            NotFoundBook
            BookNotBorrowed
        """
        raise NotImplementedError
