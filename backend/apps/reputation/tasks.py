from celery import shared_task
from django.core.cache import cache

@shared_task
def sync_score_events_task():
    try:
        from apps.reputation.services.event_listener import sync_score_events
    except (ImportError, ModuleNotFoundError):
        # Fallback or placeholder if event_listener doesn't exist yet
        return

    last_block = cache.get('last_synced_block', 0)
    synced = sync_score_events(from_block=last_block)
    if synced:
        from .services.chain_service import w3
        cache.set('last_synced_block', w3.eth.block_number)
