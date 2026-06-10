from .base import BaseEventHandler
from apps.users.services import UserService
class ScoreUpdateHandler(BaseEventHandler):
    event_name =  "ScoreUpdated"

    def handle(self, event):
        user = event['args']['user']
        role = int(event['args']['role'])
        score_type = int(event['args']['scoreType'])
        score_delta = int(event['args']['score_delta'])
        tx_hash = event['transactionHash'].hex()
        log_index = event['logIndex']
        block_number = event['blockNumber']
        block_timestamp = event['blockTimestamp']
        UserService.on_score_updated(user, score_type, score_delta, tx_hash, log_index, block_number, block_timestamp)