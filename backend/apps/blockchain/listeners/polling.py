import time
import logging
from web3 import Web3
from apps.blockchain.block_tracker import BlockTracker
from django.conf import settings

from apps.blockchain.routers import route_event

logger = logging.getLogger(__name__)

http_provider = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))



def run_polling_listener(poll_interval=10, start_block=None):
    if start_block is None: start_block=http_provider.eth.block_number
    tracker = BlockTracker(
        socket=http_provider,
        start_block=start_block
    )
    target_addresses = [
        settings.USER_REGISTRAR_CONTRACT_ADDRESS
    ]
    logger.info(f"Polling for new blocks every {poll_interval} seconds")
    while True:
        try:
            from_block, to_block = tracker.range()
            raw_logs = http_provider.eth.get_logs(
                {"fromBlock": from_block, "toBlock": to_block, "address": target_addresses}
            )
            for log in raw_logs:
                logger.info(f"[poll] {log['topics'][0]} from {log['address']} at block {log['blockNumber']}")
                try:
                    route_event(log)
                except Exception as e:
                    logger.error(f"Error processing log: {e}")
            tracker.update(to_block)
        except Exception as e:
            logger.error(f"Error in polling listener: {e}")
        time.sleep(poll_interval)


