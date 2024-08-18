import datetime
import decimal
from typing import Optional
from decimal import Decimal
from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
    model_validator,
    EmailStr,
    AnyUrl,
    StringConstraints,
    NonNegativeInt,
    NonNegativeFloat,
    NegativeInt,
    NegativeFloat,
    IPvAnyAddress,
    Field,
    condecimal,
)
from pydantic_core import PydanticCustomError, core_schema
import phonenumbers
from pydantic_core.core_schema import FieldValidationInfo
from typing import Annotated
from pydantic.functional_validators import AfterValidator, BeforeValidator
from .validators import national_code_field_validator, iban_field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_extra_types.payment import PaymentCardNumber
from . import validators


class File(BaseModel):
    buffer: bytes
    name: str


class BaseFilter(BaseModel):
    order_by: str = '-id'
    limit: Optional[int] = None
    offset: Optional[int] = None

    @field_validator('limit')
    def limit_must_be_gt_one(cls, value, info: FieldValidationInfo):
        if value is not None and value < 1:
            raise PydanticCustomError('value_error', 'Limit should be greater than 1')
        return value

    @field_validator('offset')
    def limit_must_be_positive(cls, value, info: FieldValidationInfo):
        if value is not None and value < 0:
            raise PydanticCustomError('value_error', 'Offset should be positive')
        return value

    @model_validator(mode='after')
    def check_limit_offset_default(cls, filter_obj: 'BaseFilter'):
        if filter_obj.limit is None or filter_obj.offset is None:
            filter_obj.limit = 20
            filter_obj.offset = 0
        return filter_obj

    def as_dict(self):
        return {k: v for (k, v) in self.model_dump().items() if v is not None
                and k not in ['limit', 'offset', 'order_by']}


class JalaliDateField(BaseModel):
    year: int = Field(ge=1200, le=1500)
    month: int = Field(ge=0, le=12)
    day: int = Field(ge=0, le=31)


class CustomPhoneNumber(PhoneNumber):
    @classmethod
    def _validate(cls, phone_number: str, _: core_schema.ValidationInfo) -> str:
        try:
            parsed_number = phonenumbers.parse(phone_number, cls.default_region_code)
        except phonenumbers.phonenumberutil.NumberParseException as exc:
            raise PydanticCustomError('value_error', 'value is not a valid phone number') from exc
        if not phonenumbers.is_valid_number(parsed_number):
            raise PydanticCustomError('value_error', 'value is not a valid phone number')

        return phone_number


# --------------------------- Add pydantic fields ---------------------------

NationalCodeField = Annotated[str, AfterValidator(national_code_field_validator)]
IbanField = Annotated[str, AfterValidator(iban_field_validator)]
PhoneNumberField = CustomPhoneNumber
EmailField = EmailStr
UrlField = AnyUrl
PaymentCardNumberField = PaymentCardNumber
UUIDField = Annotated[str, BeforeValidator(validators.validate_uuid)]
UIDField = Annotated[str, StringConstraints(to_lower=True, pattern=r'^[a-zA-Z0-9_-]{5,64}$')]
UIDContainsField = Annotated[str, StringConstraints(to_lower=True, pattern=r'^[a-zA-Z0-9_-]+$')]
PositiveIntField = NonNegativeInt
NegativeIntField = NegativeInt
PositiveFloatField = NonNegativeFloat
NegativeFloatField = NegativeFloat
IPField = IPvAnyAddress
LatinNameField = Annotated[str, StringConstraints(pattern=r'^[a-zA-Z\s]+$')]
PersianNameField = Annotated[str, AfterValidator(validators.persian_name_field_validator)]
DomainField = Annotated[str, StringConstraints(pattern=r"^([a-zA-Z0-9_-]+)(?:\.[a-zA-Z0-9_-]+)+$")]
PassportField = Annotated[str, StringConstraints(pattern=r'^[a-zA-Z0-9]{6,20}$')]
DateField = Annotated[str, StringConstraints(pattern=r'[0-9]{4}-[0-9]{2}-[0-9]{2}')]
TelephoneNumberField = Annotated[str, StringConstraints(pattern=r'^[\+][0-9]{7,14}$')]
CurrencyField = str  # TODO: change this
DecimalField = condecimal(allow_inf_nan=True)
PositiveDecimalField = condecimal(gt=0, allow_inf_nan=True)
NonNegativeDecimalField = condecimal(ge=0, allow_inf_nan=True)

NonEnglishNameField = Annotated[str, AfterValidator(validators.non_english_names)]
NonEnglishTextField = Annotated[str, AfterValidator(validators.non_english_texts)]

EnglishNameField = Annotated[str, StringConstraints(pattern=r'^[a-zA-Z]+$')]
EnglishTextField = Annotated[str, StringConstraints(pattern=r'^[0-9a-zA-Z\-_.]+$')]


class CustomStringValidator:

    @classmethod
    def max_length_string(cls, max_length):
        return Annotated[str, StringConstraints(max_length=max_length)]
