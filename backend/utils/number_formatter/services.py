from decimal import Decimal

from . import interfaces


class NumberFormatter(interfaces.AbstractNumberFormatter):
    def format_decimal(self, number: Decimal) -> str:
        string_number = str(number)
        sp = string_number.split('.')
        left_int = int(sp[0])
        right_int = int(sp[1]) if len(sp) > 1 else 0
        left_formatted_string = "{:,}".format(left_int)
        right_digits = 5 - len(str(left_int))
        if right_int == 0 or right_digits <= 0:
            return left_formatted_string
        return left_formatted_string + '.' + str(right_int)[:right_digits]
