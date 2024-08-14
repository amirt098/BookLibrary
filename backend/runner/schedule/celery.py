import os
import logging
from celery import Celery
from celery.schedules import crontab

logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runner.settings')

app = Celery('backend',
             broker=os.getenv("BROKER_URL", "amqp://rabbitmq:5672"),
             config_source='runner.schedule.celery_config')

app.conf.beat_schedule = {
    'update_ledger': {
        'task': 'runner.schedule.tasks.update_ledger',
        'schedule': 1800,
    },
    'send_balances': {
        'task': 'runner.schedule.tasks.send_balances',
        'schedule': crontab(minute=0, hour=18),
    },
}
