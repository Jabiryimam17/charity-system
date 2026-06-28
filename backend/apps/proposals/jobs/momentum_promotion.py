from django.db import transaction
from django.utils import timezone
from apps.proposals.models import Proposal, ProposalReview, ProposalRoleScoreset, TemporaryPromotion, PromotionHistory, PromotionType
from apps.proposals.constants import get_next_level, HIGHEST_LEVEL

def run_momentum_promotion():
    now = timezone.now()

    with transaction.atomic():

        expired = TemporaryPromotion.objects.select_for_update().filter(
            expires_at_lte=now,
            promotion_type=PromotionType.MOMENTUM
        )

        history_rows = [
            PromotionHistory(
                proposal=ep.proposal,
                promotion_type = ep.promotion_type,
                promoted_from_level=ep.promoted_from_level,
                promoted_to_level=ep.promoted_to_level,
                started_at=ep.started_at,
                expired_at=ep.ended_at,
                trigger_reason=ep.trigger_reason
            ) for ep in expired
        ]

        PromotionHistory.objects.bulk_create(history_rows)

        expired.delete()

