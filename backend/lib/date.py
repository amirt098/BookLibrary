from django.utils.dateparse import parse_date
from datetime import date


def convert_str_to_date_field(date: str) -> date:
    return parse_date(date) if date is not None else None

def convert_date_field_to_str(date: date) -> str:
    return None if date is None else str(date)
