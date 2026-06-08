from celery import shared_task
from models import ScoreEvents, Score

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
    score = Score.objects.filter(address=user_address, score_id=score_id).first()
    score.score_val += delta
    score.last_update = max(score.last_update, block_timestamp)
    Score.objects.update_or_create(address=user_address, defaults={'score_id': score_id, 'score_val': score.score_val})