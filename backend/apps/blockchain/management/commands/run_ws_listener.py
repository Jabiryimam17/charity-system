from django.core.management.base import BaseCommand
from apps.blockchain.jobs.ws_listener import run_ws_listener


class Command(BaseCommand):
    help = "Start WebSocket blockchain event listener"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting WebSocket listener...")
        run_ws_listener()
