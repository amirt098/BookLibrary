import abc
from typing import List
from enum import Enum

from asgiref.sync import async_to_sync, sync_to_async

from lib import data_classes as lib_dataclasses
from apps.account import interfaces as account_interfaces


class OfferedBookNotFound(Exception):
    pass


class OfferBookInfo(lib_dataclasses.BaseModel):
    uid: str
    offered_book_title: str
    topic: str
    author: str
    publisher: str
    proposer: str
    purchase_link: str
    is_purchased: bool
    offered_at: int


class OfferBookRequest(lib_dataclasses.BaseModel):
    offered_book_title: str
    topic: str
    author: str
    publisher: str
    proposer: str
    purchase_link: str


class OfferBookFilters(lib_dataclasses.BaseFilter):
    uid: str | None = None
    offered_book_title__contains: str | None = None
    topic__contains: str | None = None
    author__contains: str | None = None
    publisher__contains: str | None = None
    proposer__contains: str | None = None
    purchase_link__contains: str | None = None
    is_purchased: bool | None = None


class OfferBookList(lib_dataclasses.BaseModel):
    count: int
    results: List[OfferBookInfo]


class AbstractOfferBookService(abc.ABC):

    @abc.abstractmethod
    def add_offer_book(self, caller: account_interfaces.UserClaim, request: OfferBookRequest) -> OfferBookInfo:
        """
        """
        raise NotImplementedError

    async def async_add_offer_book(self, *args, **kwargs) -> OfferBookInfo:
        return await sync_to_async(self.add_offer_book)(*args, **kwargs)

    @abc.abstractmethod
    def get_offer_books(self, caller: account_interfaces.UserClaim, filters: OfferBookFilters) -> OfferBookList:
        raise NotImplementedError

    async def async_get_offer_books(self, *args, **kwargs)-> OfferBookList:
        return await sync_to_async(self.get_offer_books)(*args, **kwargs)

    @abc.abstractmethod
    def declare_purchase_book(self, caller: account_interfaces.UserClaim, offered_book_title, quantity):
        """
            OfferedBookNotFound
        """

    def get_offered_book(self, caller: account_interfaces.UserClaim, uid) -> OfferBookInfo:
        result = self.get_offer_books(caller=caller, filters=OfferBookFilters(uid=uid))
        if result.count != 1:
            raise OfferedBookNotFound(f'offered book not found with uid : {uid}')
        return result.results[0]
