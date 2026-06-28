from decimal import Decimal

from django.db import transaction
from django.db.models import F

from apps.proposals.constants import (
    LEVEL_PROMOTION_REQUIREMENTS,
    PROPOSAL_LEVELS,
    QUESTION_MAX,
    QUESTION_MIN,
)
from apps.proposals.models import Proposal, ProposalReview, ProposalRoleScoreset
from apps.reputation.services.chain_service import get_process_score
from apps.reputation.services.role_service import to_app_role_value


def submit_review(proposal_id, reviewer, role_key, question_scores, outcome, justification):
    proposal = Proposal.objects.get(id=proposal_id)

    if len(question_scores) != len(proposal.questions_criteria):
        raise ValueError('Question scores count must match proposal questions count')

    if ProposalReview.objects.filter(proposal=proposal, reviewer=reviewer).exists():
        raise ValueError('Review already exists')

    avg_score = Decimal(sum(question_scores)) / Decimal(len(question_scores))
    raw_score = (avg_score - Decimal(QUESTION_MIN)) / Decimal(QUESTION_MAX - QUESTION_MIN)

    reputation = Decimal(
        get_process_score(reviewer.wallet_address, 'proposal_review', role_key)
    )
    weighted = raw_score * reputation
    app_role = to_app_role_value(role_key)

    with transaction.atomic():
        proposal = Proposal.objects.select_for_update().get(id=proposal_id)
        scoreset, _ = ProposalRoleScoreset.objects.select_for_update().get_or_create(
            proposal=proposal,
            proposal_role=app_role,
            defaults={
                'weighted_score_sum': Decimal('0'),
                'reputation_sum': Decimal('0'),
                'avg_weighted_score': Decimal('0'),
                'review_count': 0,
            },
        )

        review = ProposalReview.objects.create(
            proposal=proposal,
            reviewer=reviewer,
            reviewer_role=app_role,
            raw_score=raw_score,
            reputation_at_time=reputation,
            outcome=outcome,
            review_justification=justification,
        )

        scoreset.weighted_score_sum = scoreset.weighted_score_sum + weighted
        scoreset.reputation_sum = scoreset.reputation_sum + reputation
        scoreset.review_count = scoreset.review_count + 1
        if scoreset.reputation_sum == 0:
            scoreset.avg_weighted_score = Decimal('0')
        else:
            scoreset.avg_weighted_score = scoreset.weighted_score_sum / scoreset.reputation_sum
        scoreset.save(
            update_fields=['weighted_score_sum', 'reputation_sum', 'review_count', 'avg_weighted_score']
        )

        Proposal.objects.filter(id=proposal.id).update(
            proposal_score=F('proposal_score') + weighted,
            daily_score_delta=F('daily_score_delta') + weighted,
        )

        _check_and_promote(proposal)

    return review


def _check_and_promote(proposal):
    current_level = proposal.proposal_level
    requirements = LEVEL_PROMOTION_REQUIREMENTS.get(current_level)
    if requirements is None:
        return

    scoresets = ProposalRoleScoreset.objects.filter(proposal=proposal)
    total_reviews = sum(scoreset.review_count for scoreset in scoresets)
    total_weighted = sum(scoreset.weighted_score_sum for scoreset in scoresets)
    total_reputation = sum(scoreset.reputation_sum for scoreset in scoresets)

    if total_reputation == 0:
        return

    overall_avg = total_weighted / total_reputation
    if (
        overall_avg >= Decimal(str(requirements['score_threshold']))
        and total_reviews >= requirements['min_reviewers']
    ):
        current_idx = PROPOSAL_LEVELS.index(current_level)
        if current_idx + 1 < len(PROPOSAL_LEVELS):
            next_level = PROPOSAL_LEVELS[current_idx + 1]
            Proposal.objects.filter(id=proposal.id).update(proposal_level=next_level)