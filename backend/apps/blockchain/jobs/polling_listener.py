import logging
from web3 import Web3
from apps.blockchain.block_tracker import BlockTracker
from django.conf import settings
from apps.blockchain.routers import route_event

logger = logging.getLogger(__name__)

http_provider = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))

def run_polling_iteration():
    """Runs a single iteration of blockchain polling."""
    tracker = BlockTracker(
        socket=http_provider,
    )
    target_addresses = [
        settings.USER_REGISTRAR_CONTRACT_ADDRESS
    ]
    try:
        from_block, to_block = tracker.range()
        if from_block > to_block:
            logger.info("No new blocks to poll.")
            return

        logger.info(f"Polling blocks from {from_block} to {to_block}")
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
        logger.error(f"Error in polling iteration: {e}")
