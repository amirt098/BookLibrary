import abc
from typing import List
from enum import Enum
from lib import data_classes as lib_dataclasses
from apps.account import interfaces as account_interfaces
from utils.date_time.interfaces import DateTime


class BookFilter(lib_dataclasses.BaseFilter):
    book_title__contains: str | None = None
    author__contains: str | None = None
    publisher__contains: str | None = None
    published_at__gte: int | None = None
    published_at__lte: int | None = None
    quantity_at__gte: int | None = None


class BookInfo(lib_dataclasses.BaseModel):
    title: str
    author: str | None = None
    publisher: str | None = None
    published_date: DateTime | None = None
    status: str
    quantity: int


class BookList(lib_dataclasses.BaseModel):
    result: List[BookInfo]
    count: int


class BookNotFound(Exception):
    pass


class AbstractBookService(abc.ABC):

    def add_new_book(self, caller: account_interfaces.UserClaim, book: BookInfo):
        """
            if book already exist add to quantity
        """
        raise NotImplementedError

    def get_books(self, caller: account_interfaces.UserClaim, filters: BookFilter):
        """"""
        raise NotImplementedError

    def disable_book(self, caller: account_interfaces.UserClaim, book_title: str):
        """
        Raise:
            BookNotFound
        """
        raise NotImplementedError

    def get_book_info(self, caller: account_interfaces.UserClaim, book_title: str):
        """
        Raise:
            BookNotFound
        """
        raise NotImplementedError
