import logging
import os
from typing import List

from apps.account.interfaces import AbstractAccountService
from apps.account.services import AccountService
from apps.book.interfaces import AbstractBookService
from apps.book.services import BookService
# apps abstractions


# apps services


# externals
from externals.telegram_bot.services import TelegramApplicationFactory

# utils
from utils.date_time.services import DateTimeUtils
from utils.number_formatter.services import NumberFormatter
from utils.currency_image_generator.services import CurrencyImageGeneratorService

logger = logging.getLogger(__name__)


def get_setting(setting_key: str, default: any = None, **kwargs) -> str:
    default_env = os.getenv(setting_key.upper(), str(default) if default else None)
    return kwargs.get(setting_key, default_env)


def get_list_setting(setting_key, default: list = None, **kwargs) -> List[str]:
    setting_str = get_setting(setting_key, ','.join([str(x) for x in (default or [])]), **kwargs)
    if isinstance(setting_str, str):
        return [s.strip() for s in setting_str.split(',') if s]
    return [str(x) for x in setting_str]


class Bootstrapper:
    def __init__(self, **kwargs) -> None:
        logger.debug(f'kwargs:{kwargs}')

        # utils
        _date_time_utils = kwargs.get('date_time_utils', DateTimeUtils())
        _number_formatter = kwargs.get('number_formatter', NumberFormatter())

        # externals env

        # apps env
        _telegram_base_address = get_setting('telegram_base_address', default='https://api.telegram.org/bot', **kwargs)
        _telegram_file_address = get_setting('telegram_file_address', default='https://api.telegram.org/file/bot',
                                             **kwargs)
        _telegram_proxy = get_setting('telegram_proxy', **kwargs)
        _telegram_bot_token = get_setting('telegram_bot_token', **kwargs)
        _telegram_admin_user_ids = get_list_setting('telegram_admin_user_ids', **kwargs)

        # externals
        _telegram_application_factory = kwargs.get('telegram_application_factory', TelegramApplicationFactory())

        self._account_service = kwargs.get('account_service', AccountService())
        self._book_service = kwargs.get('account_service', BookService())

    def get_account_service(self) -> AbstractAccountService:
        return self._account_service

    def get_book_service(self) -> AbstractBookService:
        return self._book_service


def get_bootstrapper(**kwargs) -> Bootstrapper:
    return Bootstrapper(**kwargs)
