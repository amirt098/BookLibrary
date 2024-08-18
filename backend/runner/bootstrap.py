import logging
import os
from typing import List

from apps.account.interfaces import AbstractAccountService
from apps.account.services import AccountService
from apps.borrowing_book.interfaces import AbstractLibraryFacade
from apps.borrowing_book.services import LibraryFacade
from apps.telegram_bot.services import TelegramBotService
# apps abstractions


# apps services


# externals
from externals.telegram_bot.services import TelegramApplicationFactory

# utils
from utils.date_time.services import DateTimeUtils
from utils.number_formatter.services import NumberFormatter

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
        # _telegram_admin_user_ids = get_list_setting('telegram_admin_user_ids', **kwargs)

        # externals
        _telegram_application_factory = kwargs.get('telegram_application_factory', TelegramApplicationFactory())

        self._account_service = kwargs.get('account_service', AccountService())
        self._borrowing_book_service = kwargs.get('borrowing_book_service', LibraryFacade())

        self._telegram_bot = kwargs.get(
            'telegram_bot_service',
            TelegramBotService(
                telegram_application_factory=_telegram_application_factory,
                telegram_api_address=_telegram_base_address,
                telegram_proxy=_telegram_proxy,
                account_service=self._account_service,
                borrowing_book=self._borrowing_book_service,
                date_time_utils=_date_time_utils,
                token=_telegram_bot_token,
            )
                                       )

    def get_account_service(self) -> AbstractAccountService:
        return self._account_service

    def get_book_service(self) -> AbstractLibraryFacade:
        return self._borrowing_book_service

    def get_telegram_bot(self):
        return self._telegram_bot


def get_bootstrapper(**kwargs) -> Bootstrapper:
    return Bootstrapper(**kwargs)
