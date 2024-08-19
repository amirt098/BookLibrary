from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, List

from apps.account import interfaces as account_interfaces


class BookNotAvailableException(Exception):
    pass


class BookNotFound(Exception):
    pass


class BorrowedBookNotFound(Exception):
    pass


class AddBookInput(BaseModel):
    title: str
    writer: str
    quantity: int
    topic: Optional[str] = None
    publisher: Optional[str] = None
    date_published: Optional[str] = None


class AddBookOutput(BaseModel):
    id: int
    title: str
    quantity: int
    topic: Optional[str] = None
    publisher: Optional[str] = None
    date_published: Optional[str] = None


class BorrowBookInput(BaseModel):
    username: str
    book_title: str


class BorrowBookOutput(BaseModel):
    id: int
    username: str
    book_title: str
    borrowed_at: int
    due_at: int
    return_at: int | None = None
    penalty: Optional[float] = None


class BookFilter(BaseModel):
    title: Optional[str] = None
    writer: Optional[str] = None
    topic: Optional[str] = None
    publisher: Optional[str] = None
    date_published: Optional[str] = None


class BorrowedBookFilter(BaseModel):
    username: Optional[str] = None
    book_title: Optional[str] = None
    borrowed_at: Optional[int] = None
    return_at: int | None = None
    return_at__isnull: bool | None = None
    due_at: int | None = None


class ReturnBookOutput(BaseModel):
    id: int
    username: str
    book_title: str
    return_at: int
    penalty: int | None = None


class ReturnBookInput(BaseModel):
    borrowed_book_title: str
    username: str


class BookInfo(BaseModel):
    title: str
    id: int | None = None
    writer: str | None = None
    quantity: int | None = None
    topic: str | None = None
    publisher: str | None = None
    date_published: str | None = None


class AbstractLibraryFacade(ABC):

    @abstractmethod
    def add_book(self, input_data: AddBookInput) -> AddBookOutput:
        raise NotImplementedError

    @abstractmethod
    def borrow_book(self, input_data: BorrowBookInput,
                    penalty_rate_per_day=0.5) -> BorrowBookOutput:
        raise NotImplementedError

    @abstractmethod
    def get_books(self, filters: BookFilter) -> List[AddBookOutput]:
        raise NotImplementedError

    @abstractmethod
    def get_borrowed_books(self, filters: BorrowedBookFilter) -> List[BorrowBookOutput]:
        raise NotImplementedError

    @abstractmethod
    def return_book(
            self,
            input_data: ReturnBookInput,
            penalty_rate_per_day=0.5
    ) -> ReturnBookOutput:
        raise NotImplementedError

    @abstractmethod
    def get_book_by_title(self,
                          book_title: str
                          ) -> BookInfo:
        raise NotImplementedError

    @abstractmethod
    def get_borrowed_book_by_id(
            self,
            id: int
    ) -> BorrowBookOutput:
        raise NotImplementedError

    def has_user_borrowed_book(self, user_claim: account_interfaces.UserClaim, book_title) -> bool:
        if len(
                self.get_borrowed_books(
                    BorrowedBookFilter(
                        username=user_claim.username,
                        book_title=book_title,
                        return_at__isnull=True
                    )
                )
        ) > 0:
            return True
        return False
