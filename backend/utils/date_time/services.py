import datetime

import jdatetime
import pytz

from . import interfaces


class DateTimeUtils(interfaces.AbstractDateTimeUtils):
    def get_current_timestamp(self) -> int:
        return int(datetime.datetime.now().timestamp() * 1000)

    def convert_gregorian_to_jalali_datetime(self, date_time: interfaces.DateTime):

        date = datetime.datetime(
            year=date_time.year,
            month=date_time.month,
            day=date_time.day,
            hour=date_time.hour,
            minute=date_time.minute,
            second=date_time.second,
            microsecond=date_time.millisecond * 1000
        )
        timestamp = int(date.timestamp())
        jalali_date = jdatetime.datetime.fromtimestamp(
            timestamp)

        return interfaces.DateTime(
            year=jalali_date.year,
            month=jalali_date.month,
            day=jalali_date.day,
            hour=jalali_date.hour,
            minute=jalali_date.minute,
        )

    def convert_timestamp_to_date_time(self, timestamp: int,
                                       calendar_type: interfaces.CalendarType = interfaces.CalendarType.GREGORIAN,
                                       time_zone: str = 'Asia/Tehran') -> interfaces.DateTime:
        """timestamp is in millisecond"""

        tz = pytz.timezone(time_zone)
        date = datetime.datetime.fromtimestamp(timestamp / 1000, tz)
        date_time = interfaces.DateTime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=date.hour,
            minute=date.minute,
            second=date.second,
            millisecond=date.microsecond // 1000
        )
        if calendar_type == interfaces.CalendarType.GREGORIAN:
            return date_time
        elif calendar_type == interfaces.CalendarType.JALALI:
            return self.convert_gregorian_to_jalali_datetime(date_time)
        else:
            raise ValueError(f"Invalid calendar type: {calendar_type}")

    def convert_timestamp_to_python_date_time(self, timestamp: int,
                                              time_zone: str = 'Asia/Tehran') -> datetime.datetime:
        tz = pytz.timezone(time_zone)
        date_time = datetime.datetime.fromtimestamp(timestamp / 1000, tz)

        return date_time

    def convert_date_time_to_timestamp(self, date_time: interfaces.DateTime,
                                       calendar_type: interfaces.CalendarType = interfaces.CalendarType.GREGORIAN,
                                       time_zone: str = 'Asia/Tehran') -> int:
        """Returns the timestamp in milliseconds"""

        if calendar_type == interfaces.CalendarType.GREGORIAN:
            tz = pytz.timezone(time_zone)
            date = datetime.datetime(
                year=date_time.year,
                month=date_time.month,
                day=date_time.day,
                hour=date_time.hour,
                minute=date_time.minute,
                second=date_time.second,
                tzinfo=tz
            )
            return int(date.timestamp() * 1000)
        elif calendar_type == interfaces.CalendarType.JALALI:
            gregorian_datetime = self.convert_jalali_to_gregorian_datetime(date_time)
            return self.convert_date_time_to_timestamp(gregorian_datetime, interfaces.CalendarType.GREGORIAN, time_zone)
        else:
            raise ValueError(f"Invalid calendar type: {calendar_type}")

    def find_previous_day(self, timestamp: int, number_of_days: int, time_zone: str = 'Asia/Tehran'):
        tz = pytz.timezone(time_zone)
        date_time = datetime.datetime.fromtimestamp(timestamp / 1000, tz=tz)

        date_time = date_time - datetime.timedelta(days=number_of_days)

        return interfaces.DateTime(
            year=date_time.year,
            month=date_time.month,
            day=date_time.day,
            hour=date_time.hour,
            minute=date_time.minute,
            second=date_time.second,
        )

    def find_days_between_two_timestamps(self, first_timestamp, second_timestamp,
                                         time_zone: str = 'Asia/Tehran') -> int:
        tz = pytz.timezone(time_zone)
        first_date = datetime.datetime.fromtimestamp(first_timestamp / 1000, tz=tz)
        second_date = datetime.datetime.fromtimestamp(second_timestamp / 1000, tz=tz)

        return (second_date - first_date).days

    def is_date_equal(self, first_date_time: interfaces.DateTime, second_date_time: interfaces.DateTime) -> bool:
        return [first_date_time.day, first_date_time.month, first_date_time.year] == [second_date_time.day, second_date_time.month, second_date_time.year]

    def convert_jalali_to_gregorian_datetime(self, date_time: interfaces.DateTime) -> interfaces.DateTime:
        # Convert the Jalali datetime to a Unix timestamp
        pass
        # timestamp = jdatetime.datetime(
        #     year=date_time.year,
        #     month=date_time.month,
        #     day=date_time.day,
        #     hour=date_time.hour,
        #     minute=date_time.minute,
        #     second=date_time.second
        # ).timestamp()
        #
        # # Convert the Unix timestamp to a datetime object in the Gregorian calendar
        # gregorian_date = datetime.datetime.fromtimestamp(timestamp)
        #
        # return interfaces.DateTime(
        #     year=gregorian_date.year,
        #     month=gregorian_date.month,
        #     day=gregorian_date.day,
        #     hour=gregorian_date.hour,
        #     minute=gregorian_date.minute,
        #     second=gregorian_date.second,
        #     millisecond=gregorian_date.microsecond // 1000
        # )
