import datetime
import re
import logging
import uuid
from pydantic_core import PydanticCustomError


logger = logging.getLogger(__name__)


def validate_national_code(a: str):
    if a and a == len(a) * a[0]:
        return False
    if len(a) == 8:
        a = '00' + a
    if len(a) == 9:
        a = '0' + a
    if len(a) == 10:
        r = 0
        for i in range(0, 9):
            r1 = int(a[i]) * (10 - i)
            r = r1 + r
        c = r % 11
        if (int(a[9]) == 1) and (c == 1):
            return True
        elif (int(a[9]) == 0) and (c == 0):
            return True
        elif int(a[9]) == 11 - c:
            return True

        return False
    return False


def national_code_field_validator(value: str):
    if value and value == len(value) * value[0]:
        raise PydanticCustomError("value_error", "national code is invalid")
    if len(value) == 8:
        value = '00' + value
    if len(value) == 9:
        value = '0' + value
    if len(value) == 10:
        r = 0
        for i in range(0, 9):
            r1 = int(value[i]) * (10 - i)
            r = r1 + r
        c = r % 11
        if (int(value[9]) == 1) and (c == 1):
            return value
        elif (int(value[9]) == 0) and (c == 0):
            return value
        elif int(value[9]) == 11 - c:
            return value

    raise PydanticCustomError("value_error", "national code is invalid")


def validate_name(name):
    #    \u0600-\u06FF  Persian and Arabic characters
    #    \u0750-\u077F  Arabic Supplement characters
    #    \uFB8A-\uFBFE  Arabic Extended-A characters
    #    \u0621-\u064A  More Persian and Arabic characters

    PERSIAN_ARABIC_PATTERN = re.compile(r'^[\u0600-\u06FF\u0750-\u077F\uFB8A-\uFBFE\u0621-\u064A\s]+$')
    if not isinstance(name, str):
        return False
    name = name.replace(" ", "")
    if not name:
        return False
    if not 3 <= len(name) <= 60:
        return False
    if not PERSIAN_ARABIC_PATTERN.match(name):
        return False
    return True


def persian_name_field_validator(name):
    # TODO: piraye was removed.
    return name


def non_english_names(name):
    persian_arabic_pattern = "گکچپژیلفقهموﻻء-ي"
    russian_pattern = "\u0400-\u052F"

    turkish_pattern = "a-zA-ZÇçĞğİıÖöŞşÜü"

    regex_pattern = re.compile(r"^["+persian_arabic_pattern+russian_pattern+turkish_pattern+"]+$")

    if not regex_pattern.match(name):
        raise PydanticCustomError("value_error", "value is not a valid string")
    return name


def non_english_texts(name):
    persian_arabic_pattern = "گکچپژیلفقهموﻻ۰-۹ء-ي٠-٩"
    russian_pattern = "0-9\u0400-\u052F"
    turkish_pattern = "a-zA-ZÇçĞğİıÖöŞşÜü"

    specials = "\-._"

    regex_pattern = re.compile(r"^["+persian_arabic_pattern+russian_pattern+turkish_pattern+specials+"]+$")

    if not regex_pattern.match(name):
        raise PydanticCustomError("value_error", "value is not a valid string")
    return name


def validate_mobile_number(phone_number: str, valid_country_mobile_codes: [str]) -> bool:
    logger.debug(f'phone number: {phone_number}, is {phone_number.startswith("+98")}')
    if not any(re.match(r'^\+' + code + r'[0-9]{10,13}$', phone_number) for code in valid_country_mobile_codes):
        return False
    if phone_number.startswith('+98') and len(phone_number) != 13:
        return False
    return True


def validate_card_number(card_number):
    card_number = card_number.replace(' ', '').replace('-', '')

    if not re.match(r'^\d{16}$', card_number):
        return False

    checksum = int(card_number[-1])
    digits = [int(x) for x in card_number[:-1]]
    for i in range(len(digits)):
        if i % 2 == 0:
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
    return (sum(digits) * 9) % 10 == checksum


def iban_field_validator(iban: str) -> str:
    if not iban.startswith("IR"):
        raise PydanticCustomError("value_error", "iban format is invalid.")
    numeric_iban = iban[2:]
    if not numeric_iban.isnumeric():
        raise PydanticCustomError("value_error", "iban format is invalid.")
    number_check = numeric_iban[2:] + "1827" + numeric_iban[:2]  # iban of IR =1827
    if int(number_check) % 97 != 1:
        raise PydanticCustomError("value_error", "iban format is invalid.")
    return iban


def validate_iban(iban: str) -> bool:
    if not iban.startswith("IR"):
        return False
    iban = iban[2:]
    logger.debug(f'iban = {iban}')
    if not iban.isnumeric():
        logger.debug(f'bank account number {iban} is invalid')
        return False
    number_check = iban[2:] + "1827" + iban[:2]  # iban of IR =1827
    if int(number_check) % 97 != 1:
        logger.debug(f'bank account number {iban} is invalid')
        return False
    return True


def validate_gregorian_date(date: str) -> datetime.date:
    pattern = r'[0-9]{4}-[0-9]{2}-[0-9]{2}'

    if not re.match(pattern, date):
        raise PydanticCustomError('value_error', "date format is invalid.")

    year, month, day = date.split('-')

    return datetime.date(
        year=int(year),
        month=int(month),
        day=int(day),
    )


def validate_uuid(value: str) -> str:
    try:
        uuid.UUID(str(value))
    except ValueError:
        raise PydanticCustomError('value_error', 'uuid4 format is invalid')

    return str(value)


