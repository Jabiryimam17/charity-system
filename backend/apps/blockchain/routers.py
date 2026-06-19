from eth_utils import keccak, to_hex
from apps.blockchain.handlers.UserRegistrarHandlers import ScoreUpdateHandler


EVENT_HANDLERS = {
    # ScoreUpdate(address,uint8,uint8,int32)
    "0x69c2780775d7c48f22036c050a417036d64939768a8818da25754b2b1da79c78": ScoreUpdateHandler(),
}

def route_event(event):
    handler = EVENT_HANDLERS.get(event['topics'][0])
    if not handler: return
    handler.process(event)