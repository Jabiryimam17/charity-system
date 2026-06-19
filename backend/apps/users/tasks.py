from celery import shared_task
from .models import ScoreEvents, Score

@shared_task(bind=True, max_retries=3)
def update_user_score_task(self, user_address, score_id, delta, tx_hash, log_index, block_number, block_timestamp):
    from .services import UserService
    if ScoreEvents.objects.filter(tx_hash=tx_hash, log_index=log_index).exists():
    # Event already processed, skip
        return
    # Create a new ScoreEvents entry
    ScoreEvents.objects.create(
        tx_hash=tx_hash,
        log_index=log_index,
        block_number=block_number,
        block_timestamp=block_timestamp,
        user_address=user_address,
        score_id=score_id,
        delta=delta
    )
    score, created = Score.objects.get_or_create(
        address=user_address, 
        score_id=score_id,
        defaults={'score_val': 0, 'last_update': block_timestamp}
    )
    if not created:
        score.score_val += delta
        score.last_update = max(score.last_update, block_timestamp)
        score.save()
    else:
        score.score_val = delta
        score.save()