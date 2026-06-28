import logging

from .base import BaseEventHandler
from apps.users.services import UserService
from apps.blockchain.events_abi import USER_REGISTRAR_ABI
from apps.reputation.services.role_service import chain_id_to_role_key
from web3 import Web3

w3 = Web3()
logger = logging.getLogger(__name__)


class ScoreUpdateHandler(BaseEventHandler):
    event_name = "ScoreUpdate"

    def handle(self, raw_event):
        event = self.decode_event(raw_event)
        user = event['args']['user']
        role_id = int(event['args']['role'])
        try:
            role_key = chain_id_to_role_key(role_id)
        except ValueError:
            logger.warning('Skipping score event with unknown role_id=%s', role_id)
            return

        criterion_id = int(event['args']['criterion'])
        score_delta = int(event['args']['score_delta'])
        tx_hash_value = event['transactionHash']
        tx_hash = tx_hash_value.hex() if hasattr(tx_hash_value, 'hex') else str(tx_hash_value)
        log_index = event['logIndex']
        block_number = event['blockNumber']

        # We might need to fetch block to get timestamp if it's not in raw_event
        block_timestamp = event.get('blockTimestamp')
        if block_timestamp is None:
            # Fallback or fetch from w3
            try:
                block = w3.eth.get_block(block_number)
                block_timestamp = block['timestamp']
            except Exception:
                import time
                block_timestamp = int(time.time())

        UserService.on_score_updated(
            user,
            role_id,
            criterion_id,
            score_delta,
            tx_hash,
            log_index,
            block_number,
            block_timestamp,
            role_key=role_key,
        )

    def decode_event(self, event):
        decoded = w3.codec.decode_event(USER_REGISTRAR_ABI[self.event_name], event)
        return decoded
