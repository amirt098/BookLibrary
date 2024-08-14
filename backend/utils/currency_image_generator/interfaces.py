import abc
from typing import List

from pydantic import BaseModel

from lib import data_classes as lib_dataclasses


class CurrencyRow(BaseModel):
    currency_symbol: str
    balance: lib_dataclasses.DecimalField
    status: str


class CurrencyRowList(BaseModel):
    rows: List[CurrencyRow]
    name: str
    timestamp: lib_dataclasses.PositiveIntField


class AbstractImageGenerator(abc.ABC):
    def draw_rows_in_picture(self, data_rows: CurrencyRowList) -> str:
        raise NotImplementedError
