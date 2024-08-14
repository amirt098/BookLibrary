from runner.bootstrap import get_bootstrapper
from .celery import app


@app.task
def update_ledger():
    get_bootstrapper().get_reporter_service().update_ledger()


@app.task
def send_balances():
    get_bootstrapper().get_reporter_service().send_balances()
