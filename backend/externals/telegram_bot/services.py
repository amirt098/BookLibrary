import logging
from telegram.ext import ApplicationBuilder

from . import interfaces

logger = logging.getLogger(__name__)


class TelegramApplicationFactory(interfaces.AbstractTelegramApplicationFactory):
    def get_telegram_application(
            self,
            token: str,
            proxy: str = None,
            base_api_address: str = None,
            base_file_address: str = None,
    ) -> interfaces.AbstractTelegramApplication:
        logger.debug(f'token: {token}, proxy: {proxy}, base_api_address: {base_api_address}, base_file_address: {base_file_address}')
        app_builder = ApplicationBuilder()
        app_builder.token(token)
        if base_api_address:
            app_builder.base_url(base_api_address)  # default: https://api.telegram.org/bot
        if base_file_address:
            app_builder.base_file_url(base_file_address)  # default: https://api.telegram.org/file/bot
        app = app_builder.build()
        return app
