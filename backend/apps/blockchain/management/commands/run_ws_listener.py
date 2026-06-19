from django.core.management.base import BaseCommand
from apps.blockchain.listeners.websocket import run_websocket_listener


class Command(BaseCommand):
    help = "Start WebSocket blockchain event listener"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting WebSocket listener...")
        run_websocket_listener()
