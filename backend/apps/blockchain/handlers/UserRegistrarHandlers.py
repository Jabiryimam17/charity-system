from .base import BaseEventHandler
from apps.users.services import UserService
from apps.blockchain.events_abi import USER_REGISTRAR_ABI
from web3 import Web3
w3=Web3()
class ScoreUpdateHandler(BaseEventHandler):
    event_name =  "ScoreUpdate"

    def handle(self, raw_event):
        event = self.decode_event(raw_event)
        user = event['args']['user']
        role = int(event['args']['role'])
        score_type = int(event['args']['scoreType'])
        score_delta = int(event['args']['score_delta'])
        tx_hash = event['transactionHash'].hex()
        log_index = event['logIndex']
        block_number = event['blockNumber']
        block_timestamp = event['blockTimestamp']
        UserService.on_score_updated(user, score_type, score_delta, tx_hash, log_index, block_number, block_timestamp)
    def decode_event(self, event):
        decoded = w3.codec.decode_event(USER_REGISTRAR_ABI[event_name], event)
        return decoded
