from apps.blockchain.handlers.score_updated import ScoreUpdatedHandler
EVENT_HANDLERS = {
    'ScoreUpdated': ScoreUpdatedHandler(),
}

def route_event(event_name, event):
    handler = EVENT_HANDLERS.get(event_name)
    if not handler:
        raise ValueError(f"No handler found for event: {event_name}")
    handler.process(event)