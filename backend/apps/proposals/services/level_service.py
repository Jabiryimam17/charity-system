from decimal import Decimal

from apps.reputation.services.chain_service import get_process_score

from ..constants import LEVEL_THRESHOLDS


def _normalize_to_percentage(score: int, min_score: int, max_score: int) -> Decimal:
    """
    Maps calc_score output from [min_score, max_score] → [0, 100].
    """
    span = max_score - min_score
    if span == 0:
        return Decimal('0')
    return Decimal(score - min_score) / Decimal(span) * 100


def get_initial_level_and_score(user, min_score: int, max_score: int) -> tuple[str, Decimal]:
    """
    Returns (proposal_level, initial_proposal_score).

    1. Call calc_score on contract for proposal_submission process
    2. Normalize to percentage [0, 100]
    3. Assign level by threshold
    4. initial_score = percentage × 0.01  →  [0.00, 1.00]
    """
    user_address = getattr(user, 'wallet_address', None) or getattr(user, 'address_hash', None)
    role_key = getattr(user, 'primary_role_key', None) or getattr(user, 'role_key', None)
    if not user_address or not role_key:
        return 'L1', Decimal('0.0000')

    raw = get_process_score(
        user_address=user_address,
        process_key='proposal_submission',
        role_key=role_key,
    )

    percentage = _normalize_to_percentage(raw, min_score, max_score)

    level = 'L1'
    for threshold, lvl in LEVEL_THRESHOLDS:
        if percentage <= threshold:
            level = lvl
            break

    initial_score = (percentage * Decimal('0.01')).quantize(Decimal('0.0001'))

    return level, initial_score
