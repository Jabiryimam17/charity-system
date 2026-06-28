from decimal import Decimal

import pytest

from apps.proposals.models import Proposal, ProposalReview, ProposalRoleScoreset
from apps.proposals.services.submit_review import submit_review
from apps.users.models import User


@pytest.fixture
def proposer(db):
    return User.objects.create_user(
        username='proposer@example.com',
        first_name='Pro',
        last_name='Poser',
        email='proposer@example.com',
        password='password123',
        address_hash='hash-proposer',
    )


@pytest.fixture
def reviewer(db):
    user = User.objects.create_user(
        username='reviewer@example.com',
        first_name='Re',
        last_name='Viewer',
        email='reviewer@example.com',
        password='password123',
        address_hash='hash-reviewer',
    )
    user.wallet_address = '0x1111111111111111111111111111111111111111'
    return user


@pytest.fixture
def proposal(db, proposer):
    return Proposal.objects.create(
        title='Test proposal',
        description='Description',
        region_level='district',
        region_name='Somewhere',
        budget_estimate=100,
        beneficiaries_estimate='10 people',
        questions_criteria=['q1', 'q2'],
        proposal_file='proposals/test.txt',
        proposer=proposer,
    )


@pytest.mark.django_db
def test_submit_review_creates_review_and_updates_scores(monkeypatch, proposal, reviewer):
    monkeypatch.setattr('apps.proposals.services.submit_review.get_process_score', lambda *_args, **_kwargs: 5)

    review = submit_review(
        proposal_id=proposal.id,
        reviewer=reviewer,
        role_key='PLANNER',
        question_scores=[10, 10],
        outcome='support',
        justification='Looks good',
    )

    assert isinstance(review, ProposalReview)
    assert review.raw_score == Decimal('1')
    assert review.reputation_at_time == Decimal('5')

    scoreset = ProposalRoleScoreset.objects.get(proposal=proposal)
    assert scoreset.review_count == 1
    assert scoreset.weighted_score_sum == Decimal('5')
    assert scoreset.reputation_sum == Decimal('5')
    assert scoreset.avg_weighted_score == Decimal('1')

    proposal.refresh_from_db()
    assert proposal.proposal_score == Decimal('5')
    assert proposal.daily_score_delta == Decimal('5')


@pytest.mark.django_db
def test_submit_review_rejects_question_count_mismatch(proposal, reviewer):
    with pytest.raises(ValueError, match='Question scores count must match proposal questions count'):
        submit_review(
            proposal_id=proposal.id,
            reviewer=reviewer,
            role_key='PLANNER',
            question_scores=[8],
            outcome='support',
            justification='Mismatch',
        )


@pytest.mark.django_db
def test_submit_review_rejects_duplicate(monkeypatch, proposal, reviewer):
    monkeypatch.setattr('apps.proposals.services.submit_review.get_process_score', lambda *_args, **_kwargs: 2)

    submit_review(
        proposal_id=proposal.id,
        reviewer=reviewer,
        role_key='PLANNER',
        question_scores=[8, 9],
        outcome='support',
        justification='First',
    )

    with pytest.raises(ValueError, match='Review already exists'):
        submit_review(
            proposal_id=proposal.id,
            reviewer=reviewer,
            role_key='PLANNER',
            question_scores=[9, 9],
            outcome='support',
            justification='Duplicate',
        )


@pytest.mark.django_db
def test_submit_review_promotes_after_threshold(monkeypatch, proposal):
    monkeypatch.setattr('apps.proposals.services.submit_review.get_process_score', lambda *_args, **_kwargs: 10)

    for idx in range(3):
        reviewer = User.objects.create_user(
            username=f'reviewer{idx}@example.com',
            first_name='Re',
            last_name=f'Viewer{idx}',
            email=f'reviewer{idx}@example.com',
            password='password123',
            address_hash=f'hash-{idx}',
        )
        reviewer.wallet_address = f'0x{idx + 1:040x}'

        submit_review(
            proposal_id=proposal.id,
            reviewer=reviewer,
            role_key='PLANNER',
            question_scores=[10, 10],
            outcome='support',
            justification='Strong support',
        )

    proposal.refresh_from_db()
    assert proposal.proposal_level == 'L2'
