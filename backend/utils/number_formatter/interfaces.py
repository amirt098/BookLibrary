import abc
from decimal import Decimal


class AbstractNumberFormatter(abc.ABC):
    def format_decimal(self, number: Decimal) -> str:
        raise NotImplementedError
