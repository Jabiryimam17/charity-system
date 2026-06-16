from eth_utils import keccak, to_hex
from apps.blockchain.handlers.score_updated import ScoreUpdateHandler


EVENT_HANDLERS = {
    to_hex(keccak(b"ScoreUpdate(address,uint8,uint8,int32)")): ScoreUpdateHandler(),
}

def route_event(event):
    handler = EVENT_HANDLERS.get(event['topics'][0])
    if not handler: return
    handler.process(event)