import logging
from django.core.management.base import BaseCommand
from runner.bootstrap import get_bootstrapper

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'listens to telegram in blocking mode'

    def handle(self, *args, **kwargs):
        service = get_bootstrapper().get_telegram_bot()
        service.start_polling()
