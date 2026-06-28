from django.core.management.base import BaseCommand
from apps.blockchain.jobs.polling_listener import run_polling_iteration
from apps.blockchain.block_tracker import BlockTracker
from web3 import Web3
from django.conf import settings
import time

class Command(BaseCommand):
    help = 'Start polling blockchain event listener'

    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=10, help='Polling interval in seconds')
        parser.add_argument('--start-block', type=int, default=None, help='Start block number')
        parser.add_argument('--reset', action='store_true', help='Reset block tracker to start block')
        parser.add_argument('--reset-to', type=int, default=None, help='Reset block tracker to specified block number')

    def handle(self, *args, **options):
        w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
        tracker = BlockTracker(w3)

        if options['reset'] or options['reset_to']:
            tracker.reset(options['reset_to'])
            self.stdout.write(self.style.WARNING(f"Reset block tracker to {tracker.last_block}"))
        
        if options['start_block'] is not None:
             tracker.update(options['start_block'])
             self.stdout.write(self.style.WARNING(f"Set start block to {options['start_block']}"))

        self.stdout.write(self.style.SUCCESS("Starting polling listener..."))
        
        while True:
            run_polling_iteration()
            time.sleep(options['interval'])
