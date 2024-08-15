from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing import Optional, List


class AddBookInput(BaseModel):
    title: str
    author: str
    isbn: str
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
    book_id: int
    due_date: str


class BorrowBookOutput(BaseModel):
    id: int
    username: str
    book_id: int
    borrowed_date: str
    due_date: str
    penalty: Optional[float] = None


class BookFilter(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    topic: Optional[str] = None
    publisher: Optional[str] = None
    date_published: Optional[str] = None


class BorrowedBookFilter(BaseModel):
    username: Optional[str] = None
    book_id: Optional[int] = None
    borrowed_date: Optional[str] = None


class ReturnBookOutput(BaseModel):
    id: int
    username: str
    book_id: int
    return_date: str
    penalty: int


class ReturnBookInput(BaseModel):
    borrowed_book_id: int
    username: str


class AbstractLibraryFacade(ABC):

    @abstractmethod
    def add_book(self, input_data: AddBookInput) -> AddBookOutput:
        pass

    @abstractmethod
    def borrow_book(self, input_data: BorrowBookInput,
                    penalty_rate_per_day=0.5) -> BorrowBookOutput:
        pass

    @abstractmethod
    def get_books(self, filters: BookFilter) -> List[AddBookOutput]:
        pass

    @abstractmethod
    def get_borrowed_books(self, filters: BorrowedBookFilter) -> List[BorrowBookOutput]:
        pass

    @abstractmethod
    def return_book(
            self,
            input_data: ReturnBookInput,
            penalty_rate_per_day=0.5
    ) -> ReturnBookOutput:
        pass
