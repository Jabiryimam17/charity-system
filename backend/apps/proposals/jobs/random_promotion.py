from django.db import transaction
from django.utils import timezone
from apps.proposals.models import Proposal, ProposalReview, ProposalRoleScoreset, TemporaryPromotion, PromotionHistory, \
    PromotionType
from apps.proposals.constants import HIGHEST_LEVEL, get_next_level


def run_random_promotion():
    now = timezone.now()
    with transaction.atomic():
        expired = TemporaryPromotion.objects.select_for_update().filter(
            promotion_type=PromotionType.RANDOM,
            expires_at_lte=now
        )

        history_rows = [
            PromotionHistory(
                proposal=ep.proposal,
                promotion_type=ep.promotion_type,
                promoted_from_level=ep.promoted_from_level,
                promoted_to_level=ep.promoted_to_level,
                started_at=ep.started_at,
                expired_at=ep.ended_at,
                trigger_reason=ep.trigger_reason
            ) for ep in expired
        ]

        PromotionHistory.objects.bulk_create(history_rows)
        expired.delete()

        already_promoted_ids = TemporaryPromotion.objects.filter(
            promotion_type=PromotionType.RANDOM,
        ).values_list('proposal_id', flag=True)

        candidates = (
            Proposal.objects.exclude(proposal_level=HIGHEST_LEVEL).exclude(id__in=already_promoted_ids).filter(
                proposal_status='active').order_by('?')[:5]
        )

        """
        Alternative Efficient Randomization
        pick_count = min(5, total)
        random_offset = random.randint(0, max(0, total - pick_count))
        
        candidates = (
            Proposal.objects
            .exclude(proposal_level=HIGHEST_LEVEL)
            .exclude(id__in=already_promoted_ids)
            .filter(proposal_status='active')
            [random_offset : random_offset + pick_count]
        )
        """

        promotions = []

        for proposal in candidates:
            next_level = get_next_level(proposal.proposal_level)
            if not next_level: continue
            promotions.append(
                TemporaryPromotion(
                    proposal=proposal,
                    promotion_type=PromotionType.RANDOM,
                    promoted_from_level=proposal.proposal_level,
                    promoted_to_level=next_level,
                    started_at=now,
                    expires_at=now + timezone.timedelta(hours=24),
                    trigger_reason="Random promotion"
                )
            )
        TemporaryPromotion.objects.bulk_create(promotions)
