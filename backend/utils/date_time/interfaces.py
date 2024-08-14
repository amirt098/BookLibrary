import abc
import datetime

from pydantic import BaseModel
from enum import Enum


class CalendarType(Enum):
    JALALI = 1
    GREGORIAN = 2


class DateTime(BaseModel):
    year: int
    month: int
    day: int
    hour: int = 0
    minute: int = 0
    second: int = 0
    millisecond: int = 0


class AbstractDateTimeUtils(abc.ABC):
    def get_current_timestamp(self) -> int:
        """return milliseconds"""

        raise NotImplementedError

    def convert_timestamp_to_date_time(self, timestamp: int, calendar_type: CalendarType,
                                       time_zone: str = 'Asia/Tehran') -> DateTime:
        raise NotImplementedError

    def convert_timestamp_to_python_date_time(self, timestamp: int,
                                              time_zone: str = 'Asia/Tehran') -> datetime.datetime:
        raise NotImplementedError

    def convert_date_time_to_timestamp(self, date_time: DateTime, calendar_type: CalendarType,
                                       time_zone: str = 'Asia/Tehran') -> int:
        """return milliseconds"""

        raise NotImplementedError

    def convert_gregorian_to_jalali_datetime(self, date_time: DateTime):
        raise NotImplementedError

    def find_previous_day(self, timestamp: int, number_of_days: int):
        raise NotImplementedError

    def find_days_between_two_timestamps(self, first_timestamp, second_timestamp) -> int:
        raise NotImplementedError

    def is_date_equal(self, first_date_time: DateTime, second_date_time: DateTime) -> bool:
        raise NotImplementedError

    def get_start_of_day_timestamp(self, calendar_type: CalendarType = CalendarType.GREGORIAN,
                                   time_zone: str = 'Asia/Tehran') -> int:
        current_datetime = self.convert_timestamp_to_date_time(self.get_current_timestamp(), CalendarType.GREGORIAN,
                                                               time_zone)

        last_midnight = DateTime(
            year=current_datetime.year,
            month=current_datetime.month,
            day=current_datetime.day,
        )

        return self.convert_date_time_to_timestamp(last_midnight, calendar_type=CalendarType.GREGORIAN,
                                                   time_zone=time_zone)

    def get_end_of_day_timestamp(self, calendar_type: CalendarType = CalendarType.GREGORIAN,
                                 time_zone: str = 'Asia/Tehran') -> int:
        start_of_day_timestamp = self.get_start_of_day_timestamp(calendar_type, time_zone)
        return start_of_day_timestamp + 3600 * 24 * 1000
