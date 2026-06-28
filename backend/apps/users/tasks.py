from celery import shared_task
from apps.reputation.models import ScoreEvents, Score
from apps.reputation.services.role_service import chain_id_to_role_key

@shared_task(bind=True, max_retries=3)
def update_user_score_task(
    self,
    user_address,
    role_id,
    criterion_id,
    delta,
    tx_hash,
    log_index,
    block_number,
    block_timestamp,
    role_key=None,
):
    from apps.reputation.models import ReputationCriterion, UserRole

    if ScoreEvents.objects.filter(tx_hash=tx_hash, log_index=log_index).exists():
        # Event already processed, skip
        return

    # Create a new ScoreEvents entry
    try:
        criterion = ReputationCriterion.objects.get(chain_id=criterion_id)
        if role_key:
            role = UserRole.objects.get(key=role_key)
        else:
            role = UserRole.objects.get(key=chain_id_to_role_key(role_id))

        ScoreEvents.objects.create(
            tx_hash=tx_hash,
            log_index=log_index,
            block_number=block_number,
            block_timestamp=block_timestamp,
            user_address=user_address,
            criterion=criterion,
            role=role,
            delta=delta
        )

        score, created = Score.objects.get_or_create(
            address=user_address,
            criterion=criterion,
            defaults={'score': 0, 'last_update': block_timestamp}
        )

        if not created:
            score.score += delta
            score.last_update = max(score.last_update, block_timestamp)
            score.save()
        else:
            score.score = delta
            score.save()
    except Exception as e:
        self.retry(exc=e, countdown=10)