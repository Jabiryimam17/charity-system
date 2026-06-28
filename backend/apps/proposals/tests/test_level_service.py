from decimal import Decimal
from types import SimpleNamespace

from apps.proposals.services.level_service import (
    _normalize_to_percentage,
    get_initial_level_and_score,
)


def test_normalize_to_percentage():
    result = _normalize_to_percentage(score=50, min_score=-100, max_score=100)
    assert result == Decimal('75')


def test_get_initial_level_and_score(monkeypatch):
    user = SimpleNamespace(address_hash='0x1111111111111111111111111111111111111111', role_key='planner')

    def fake_get_process_score(user_address, process_key, role_key):
        assert user_address == user.address_hash
        assert process_key == 'proposal_submission'
        assert role_key == user.role_key
        return 50

    monkeypatch.setattr('apps.proposals.services.level_service.get_process_score', fake_get_process_score)

    level, initial_score = get_initial_level_and_score(user=user, min_score=-100, max_score=100)

    assert level == 'L4'
    assert initial_score == Decimal('0.7500')
