from celery import shared_task
from .jobs.polling_listener import run_polling_iteration
from .jobs.ws_listener import run_ws_listener

@shared_task
def run_polling_listener_task():
    run_polling_iteration()

@shared_task
def run_websocket_listener_task():
    # Note: This task will run indefinitely if run_ws_listener doesn't return
    run_ws_listener()
