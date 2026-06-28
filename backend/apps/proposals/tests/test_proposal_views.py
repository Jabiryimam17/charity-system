from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from apps.proposals.models import Proposal, ProposalComment, ProposalRoleScoreset
from apps.users.models import User


@pytest.fixture
def proposer(db):
    return User.objects.create_user(
        username='prop@example.com',
        first_name='Prop',
        last_name='Oser',
        email='prop@example.com',
        password='password123',
        address_hash='hash-prop',
    )


@pytest.fixture
def reviewer_user(db):
    return User.objects.create_user(
        username='reviewer-view@example.com',
        first_name='Re',
        last_name='Viewer',
        email='reviewer-view@example.com',
        password='password123',
        address_hash='hash-reviewer-view',
    )


@pytest.fixture
def proposal(db, proposer):
    return Proposal.objects.create(
        title='Proposal',
        description='Description',
        region_level='city',
        region_name='Addis',
        budget_estimate=120,
        beneficiaries_estimate='20 families',
        questions_criteria=['q1', 'q2'],
        proposal_file='proposals/file.txt',
        proposer=proposer,
    )


@pytest.mark.django_db
def test_review_get_returns_proposal_context(api_client, reviewer_user, proposal):
    ProposalRoleScoreset.objects.create(
        proposal=proposal,
        proposal_role=1,
        weighted_score_sum=3,
        reputation_sum=5,
        avg_weighted_score=0.6,
        review_count=2,
    )
    api_client.force_authenticate(user=reviewer_user)

    res = api_client.get(f'/proposals/{proposal.id}/reviews/')

    assert res.status_code == 200
    assert res.data['proposal_id'] == proposal.id
    assert res.data['proposal_level'] == proposal.proposal_level
    assert res.data['questions_criteria'] == ['q1', 'q2']
    assert len(res.data['role_scores']) == 1


@pytest.mark.django_db
def test_review_post_rejects_proposer_self_review(api_client, proposer, proposal):
    api_client.force_authenticate(user=proposer)

    res = api_client.post(
        f'/proposals/{proposal.id}/reviews/',
        {
            'role': 'PLANNER',
            'question_scores': [9, 8],
            'outcome': 'support',
            'justification': 'self review',
        },
        format='json',
    )

    assert res.status_code == 403
    assert 'Proposers cannot review their own proposal' in res.data['message']


@pytest.mark.django_db
def test_review_post_returns_201_on_success(monkeypatch, api_client, reviewer_user, proposal):
    reviewed_at = datetime.now(timezone.utc)

    def _fake_submit_review(**_kwargs):
        return SimpleNamespace(reviewed_at=reviewed_at)

    monkeypatch.setattr('apps.proposals.views.submit_review.submit_review', _fake_submit_review)
    api_client.force_authenticate(user=reviewer_user)

    res = api_client.post(
        f'/proposals/{proposal.id}/reviews/',
        {
            'role': 'PLANNER',
            'question_scores': [9, 8],
            'outcome': 'support',
            'justification': 'valid',
        },
        format='json',
    )

    assert res.status_code == 201
    assert res.data['proposal_id'] == proposal.id
    assert res.data['proposal_level'] == proposal.proposal_level
    assert res.data['outcome'] == 'support'


@pytest.mark.django_db
def test_review_post_returns_400_for_service_error(monkeypatch, api_client, reviewer_user, proposal):
    def _fake_submit_review(**_kwargs):
        raise ValueError('Review already exists')

    monkeypatch.setattr('apps.proposals.views.submit_review.submit_review', _fake_submit_review)
    api_client.force_authenticate(user=reviewer_user)

    res = api_client.post(
        f'/proposals/{proposal.id}/reviews/',
        {
            'role': 'PLANNER',
            'question_scores': [9, 8],
            'outcome': 'support',
            'justification': 'duplicate',
        },
        format='json',
    )

    assert res.status_code == 400
    assert res.data['message'] == 'Review already exists'


@pytest.mark.django_db
def test_comments_list_and_create(api_client, reviewer_user, proposal):
    ProposalComment.objects.create(proposal=proposal, user=reviewer_user, comment='Existing comment')
    api_client.force_authenticate(user=reviewer_user)

    list_res = api_client.get(f'/proposals/{proposal.id}/comments/')
    assert list_res.status_code == 200
    assert len(list_res.data['results']) == 1
    assert list_res.data['results'][0]['comment'] == 'Existing comment'

    create_res = api_client.post(
        f'/proposals/{proposal.id}/comments/',
        {'comment': 'New comment'},
        format='json',
    )
    assert create_res.status_code == 201
    assert create_res.data['comment'] == 'New comment'
    assert create_res.data['user_id'] == reviewer_user.id
    assert 'likes' in create_res.data
    assert 'dislikes' in create_res.data
