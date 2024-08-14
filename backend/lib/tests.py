from typing import Optional
from uuid import uuid4
from pydantic import ValidationError

from django.test import TestCase
from .data_classes import (
    BaseFilter, PositiveIntField, PositiveFloatField, DomainField,
    NationalCodeField, IbanField, PhoneNumberField, EmailField,
    UrlField, UIDField, UUIDField, PaymentCardNumberField, IPField,
    PersianNameField, LatinNameField, PassportField, DateField, JalaliDateField,
    CountryCodeField, UIDContainsField, TelephoneNumberField, CustomStringValidator,
    BaseModel, NonEnglishNameField, NonEnglishTextField, EnglishNameField, EnglishTextField
)


class EnglishFields(BaseModel):
    name_field: EnglishNameField | None = None
    text_field: EnglishTextField | None = None


class NonEnglishFields(BaseModel):
    name_field: NonEnglishNameField | None = None
    text_field: NonEnglishTextField | None = None


class TestDataClassWithOrderDefault(BaseFilter):
    order_by: str = '-joined_at'
    field_1: Optional[int] = None
    field_2: Optional[str] = None


class TestDataClassWithoutOrderDefault(BaseFilter):
    field_1: Optional[int] = None
    field_2: Optional[str] = None


class TestBaseField(BaseFilter):
    national_code: Optional[NationalCodeField] = None
    iban: Optional[IbanField] = None
    phone_number: Optional[PhoneNumberField] = None
    email: Optional[EmailField] = None
    url: Optional[UrlField] = None
    uid: Optional[UIDField] = None
    uuid: Optional[UUIDField] = None
    card: Optional[PaymentCardNumberField] = None
    ip: Optional[IPField] = None
    persian_name: Optional[PersianNameField] = None
    latin_name: Optional[LatinNameField] = None
    positive_int: Optional[PositiveIntField] = None
    positive_float: Optional[PositiveFloatField] = None
    passport: Optional[PassportField] = None
    domain: Optional[DomainField] = None
    date: Optional[DateField] = None
    country_code: Optional[CountryCodeField] = None
    telephone_number: Optional[TelephoneNumberField] = None
    uid_contains: Optional[UIDContainsField] = None


class TestJalaliDate(BaseFilter):
    j_date: JalaliDateField


class BaseFilterTestCase(TestCase):
    def test_filter_data_class(self):
        object_with_default_order = TestDataClassWithOrderDefault(field_1=1234, limit=5)
        object_without_default_order = TestDataClassWithoutOrderDefault(field_2="1234", limit=4, offset=2)

        self.assertNotIn('limit', object_with_default_order.as_dict())
        self.assertNotIn('offset', object_with_default_order.as_dict())
        self.assertNotIn('order_by', object_with_default_order.as_dict())
        self.assertIn('field_1', object_with_default_order.as_dict())
        self.assertNotIn('field_2', object_with_default_order.as_dict())
        self.assertIsNone(object_with_default_order.field_2)
        self.assertEqual(object_with_default_order.order_by, '-joined_at')
        self.assertEqual(object_with_default_order.limit, 20)
        self.assertEqual(object_with_default_order.offset, 0)

        self.assertNotIn('limit', object_without_default_order.as_dict())
        self.assertNotIn('offset', object_without_default_order.as_dict())
        self.assertNotIn('order_by', object_without_default_order.as_dict())
        self.assertIn('field_2', object_without_default_order.as_dict())
        self.assertNotIn('field_1', object_without_default_order.as_dict())
        self.assertIsNone(object_without_default_order.field_1)
        self.assertEqual(object_without_default_order.order_by, '-id')
        self.assertEqual(object_without_default_order.limit, 4)
        self.assertEqual(object_without_default_order.offset, 2)

        with self.assertRaises(ValidationError) as e:  # wrong limit
            TestDataClassWithOrderDefault(limit=0, offset=2)

        with self.assertRaises(ValidationError) as e:  # wrong offset
            TestDataClassWithOrderDefault(limit=5, offset=-2)


class BaseFieldTestCase(TestCase):

    def test_language_aware_non_english_fields(self):
        all_arabic_chars = "ضصثقفغعهخحجدشسيبلاتنمكطئءؤرﻻىةوزظ"
        all_persian_chars = "ضصثقفغعهخحجچشسیبلاتنمکگظطزرذدپو"
        turkish_chars = "abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
        arabic_numbers = "١٢٣٤٥٦٧٨٩٠"
        persian_numbers = "۱۲۳۴۵۶۷۸۹۰"

        NonEnglishFields(
            name_field=all_arabic_chars
        )
        NonEnglishFields(
            name_field=all_persian_chars
        )
        NonEnglishFields(
            name_field=turkish_chars
        )

        with self.assertRaises(ValidationError):
            NonEnglishFields(name_field=arabic_numbers)
        with self.assertRaises(ValidationError):
            NonEnglishFields(name_field=persian_numbers)
        with self.assertRaises(ValidationError):
            NonEnglishFields(name_field=".-_")
        with self.assertRaises(ValidationError):
            NonEnglishFields(name_field="123456789")
        NonEnglishFields(
            text_field=all_arabic_chars + arabic_numbers
        )
        NonEnglishFields(
            text_field=all_persian_chars + persian_numbers
        )
        NonEnglishFields(
            text_field=turkish_chars + "-_." + "0123456789"
        )

        NonEnglishFields(
            text_field=all_arabic_chars + arabic_numbers + "-_."
        )
        NonEnglishFields(
            text_field=all_persian_chars + persian_numbers + "-_."
        )


    def test_english_fields(self):
        all_english_chars = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        EnglishFields(
            name_field=all_english_chars
        )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + ".-_"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + "123"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + "ضصثقفغعهخحجدشسيبلاتنمكطئءؤرﻻىةوزظ"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + "ضصثقفغعهخحجچشسیبلاتنمکگظطزرذدپو"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + "abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + "١٢٣٤٥٦٧٨٩٠"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                name_field=all_english_chars + "۱۲۳۴۵۶۷۸۹۰"
            )

        EnglishFields(
            text_field=all_english_chars
        )
        EnglishFields(
            text_field=all_english_chars + ".-_"
        )
        EnglishFields(
            text_field=all_english_chars + "123"
        )
        with self.assertRaises(ValidationError):
            EnglishFields(
                text_field=all_english_chars + "ضصثقفغعهخحجدشسيبلاتنمكطئءؤرﻻىةوزظ"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                text_field=all_english_chars + "ضصثقفغعهخحجچشسیبلاتنمکگظطزرذدپو"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                text_field=all_english_chars + "abcçdefgğhıijklmnoöprsştuüvyzABCÇDEFGĞHIİJKLMNOÖPRSŞTUÜVYZ"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                text_field=all_english_chars + "١٢٣٤٥٦٧٨٩٠"
            )
        with self.assertRaises(ValidationError):
            EnglishFields(
                text_field=all_english_chars + "۱۲۳۴۵۶۷۸۹۰"
            )

    def test_national_code(self):
        TestBaseField(national_code="0022988556")
        with self.assertRaises(ValidationError):
            TestBaseField(national_code="0022988557")

    def test_j_date(self):
        TestJalaliDate(j_date=JalaliDateField(day=4, month=4, year=1378))
        with self.assertRaises(ValidationError):
            TestJalaliDate(j_date=JalaliDateField(day=32, month=4, year=1378))
        with self.assertRaises(ValidationError):
            TestJalaliDate(j_date=JalaliDateField(day=4, month=13, year=1378))
        with self.assertRaises(ValidationError):
            TestJalaliDate(j_date=JalaliDateField(day=4, month=4, year=1501))

    def test_date(self):
        TestBaseField(date="2022-04-04")
        with self.assertRaises(ValidationError):
            TestBaseField(national_code="2022/04/04")
        with self.assertRaises(ValidationError):
            TestBaseField(national_code="22-04-04")
        with self.assertRaises(ValidationError):
            TestBaseField(national_code="04-04-2022")

    def test_iban(self):
        TestBaseField(iban="IR230700001000118608257001")
        with self.assertRaises(ValidationError):
            TestBaseField(iban="IR230700001000118608257008")
        with self.assertRaises(ValidationError):
            TestBaseField(iban="230700001000118608257001")

    def test_phone_number(self):
        TestBaseField(phone_number="+989336461731")  # iran
        TestBaseField(phone_number="+96433646173")  # iraq
        TestBaseField(phone_number="+903122132965")  # turkey
        test = TestBaseField(phone_number="+784951234575")  # russia
        self.assertEqual(test.phone_number, "+784951234575")
        test = TestBaseField(phone_number="+93205123457")  # afghan
        self.assertEqual(test.phone_number, "+93205123457")

        with self.assertRaises(ValidationError):
            TestBaseField(phone_number="09336461731")
        with self.assertRaises(ValidationError):
            TestBaseField(phone_number="+652336461731")

    def test_email(self):
        TestBaseField(email="a.h@gmail.com")
        with self.assertRaises(ValidationError):
            TestBaseField(email="a.h.com")

    def test_url(self):
        TestBaseField(url="https://runc.com")
        TestBaseField(url="https://runc.ir")
        TestBaseField(url="https://runc.app")
        TestBaseField(url="https://runc.app/some")
        TestBaseField(url="https://runc.app/some/dfdf")
        TestBaseField(url="https://runc.app/some?q=some")
        with self.assertRaises(ValidationError):
            TestBaseField(url="runc.com")
        with self.assertRaises(ValidationError):
            TestBaseField(url="runc")

    def test_uid(self):
        TestBaseField(uid="ali_reza_78")
        test = TestBaseField(uid="Ali_reza_78")
        self.assertEqual(test.uid, "ali_reza_78")
        with self.assertRaises(ValidationError):
            TestBaseField(uid="ali7")
        with self.assertRaises(ValidationError):
            TestBaseField(uid="a123456789a123456789a123456789a123456789a123456789a12345678912345")
        with self.assertRaises(ValidationError):
            TestBaseField(uid="ali.reza.78")

    def test_uuid(self):
        TestBaseField(uuid=str(uuid4()))
        with self.assertRaises(ValidationError):
            TestBaseField(uuid=str(uuid4())[0:14])

    def test_card(self):
        TestBaseField(card="6104337586755850")
        with self.assertRaises(ValidationError):
            TestBaseField(card="6104337586755857")

    def test_ip(self):
        TestBaseField(ip="127.0.0.1")
        TestBaseField(ip="fe80::9857:8d54:8248:5674")
        with self.assertRaises(ValidationError):
            TestBaseField(ip="127.222.1.333333")
        with self.assertRaises(ValidationError):
            TestBaseField(ip="1272222")

    def test_persian_name(self):
        TestBaseField(persian_name="امیرحسین")  # ی
        TestBaseField(persian_name="امیرحسين")  # ي
        TestBaseField(persian_name="علیرضا")
        with self.assertRaises(ValidationError):
            TestBaseField(persian_name="amir")
        with self.assertRaises(ValidationError):
            TestBaseField(persian_name="*!")

    def test_latin_name(self):
        TestBaseField(latin_name="amir ali")
        TestBaseField(latin_name="ali")
        with self.assertRaises(ValidationError):
            TestBaseField(latin_name="امیر")
        with self.assertRaises(ValidationError):
            TestBaseField(latin_name="amir78")

    def test_positive_int(self):
        TestBaseField(positive_int=100)
        TestBaseField(positive_int=0)
        with self.assertRaises(ValidationError):
            TestBaseField(positive_int=-1)
        with self.assertRaises(ValidationError):
            TestBaseField(positive_int=-100)

    def test_positive_float(self):
        TestBaseField(positive_float=100)
        TestBaseField(positive_float=100.0)
        TestBaseField(positive_float=0.0)
        TestBaseField(positive_float=0)
        TestBaseField(positive_float=1.1)
        with self.assertRaises(ValidationError):
            TestBaseField(positive_float=-0.1)
        with self.assertRaises(ValidationError):
            TestBaseField(positive_float=-100)

    def test_passport(self):
        TestBaseField(passport="A12355858255545545")
        TestBaseField(passport="A656458B")
        TestBaseField(passport="AB12355858255545545")

        with self.assertRaises(ValidationError):
            TestBaseField(passport="A1235585825554556645454554545455445")
        with self.assertRaises(ValidationError):
            TestBaseField(passport="A1235585825554554_5")

    def test_domain(self):
        TestBaseField(domain="runc.ir")
        TestBaseField(domain="runc.app")
        TestBaseField(domain="runc-1402.com")

        with self.assertRaises(ValidationError):
            TestBaseField(domain="runc_app")
        with self.assertRaises(ValidationError):
            TestBaseField(domain="runc")
        with self.assertRaises(ValidationError):
            TestBaseField(domain="https://runc.app")
        with self.assertRaises(ValidationError):
            TestBaseField(domain="https://runc.app/some")
        with self.assertRaises(ValidationError):
            TestBaseField(domain="runc.app/some")

    def test_country_code(self):
        TestBaseField(country_code="IR")
        TestBaseField(country_code="IQ")
        TestBaseField(country_code="LB")
        TestBaseField(country_code="RU")
        TestBaseField(country_code="TR")

        with self.assertRaises(ValidationError):
            TestBaseField(country_code="TRK")
        with self.assertRaises(ValidationError):
            TestBaseField(country_code="+98")
        with self.assertRaises(ValidationError):
            TestBaseField(country_code="MJ")
        with self.assertRaises(ValidationError):
            TestBaseField(country_code="iran")

    def test_telephone_number(self):
        TestBaseField(telephone_number="+9802177901467")
        TestBaseField(telephone_number="+78013562456565")
        TestBaseField(telephone_number="+98013562456565")

        with self.assertRaises(ValidationError):
            TestBaseField(telephone_number="021779014676765656")
        with self.assertRaises(ValidationError):
            TestBaseField(telephone_number="98013562456565")

    def test_uid_contains(self):
        TestBaseField(uid_contains="ali_reza_78")
        TestBaseField(uid_contains="Agfgfjjhjjhgjhgjgjgjhgjsdkhdshdkjskhdkshkdjhkjh8")

        with self.assertRaises(ValidationError):
            TestBaseField(uid_contains="+uhhhjk%")
        with self.assertRaises(ValidationError):
            TestBaseField(uid_contains="ghgjhgjgjh#")


class CustomStringValidationTestCase(TestCase):

    def test_max_length_string(self):
        class MyModel(BaseModel):
            string_field: CustomStringValidator.max_length_string(2)
            string_Nullable: CustomStringValidator.max_length_string(2) | None = None

        test_model = MyModel(
            string_field='2',
        )
        test_model = MyModel(
            string_field='22',
            string_Nullable='12'
        )
        with self.assertRaises(Exception) as e:
            MyModel(
                string_field='222',
                string_Nullable='12'
            )
        with self.assertRaises(Exception) as e:
            MyModel(
                string_field='22',
                string_Nullable='122'
            )
        with self.assertRaises(Exception) as e:
            MyModel(
                string_Nullable='12'
            )
