from apps.blockchain.handlers.UserRegistrarHandlers import ScoreUpdateHandler


EVENT_HANDLERS = {
    # ScoreUpdate(address,uint8,uint8,int32)
    "0x69c2780775d7c48f22036c050a417036d64939768a8818da25754b2b1da79c78": ScoreUpdateHandler(),
}

def route_event(event):
    topic0 = event['topics'][0]
    if isinstance(topic0, bytes):
        topic0 = '0x' + topic0.hex()
    elif hasattr(topic0, 'hex'):
        topic0 = topic0.hex()
    handler = EVENT_HANDLERS.get(topic0)
    if not handler: return
    handler.process(event)