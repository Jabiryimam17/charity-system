import pytest

from apps.auths.enums import Roles
from apps.reputation.services import role_service


def test_to_app_role_value_from_enum_name():
    assert role_service.to_app_role_value('PLANNER') == Roles.PLANNER.value


def test_to_app_role_value_from_role_key_alias(monkeypatch):
    monkeypatch.setattr(role_service, 'role_key_to_app_role_value', lambda key: Roles.DONATOR.value)
    assert role_service.to_app_role_value('donor') == Roles.DONATOR.value


def test_to_app_role_value_invalid_role():
    with pytest.raises(ValueError):
        role_service.to_app_role_value('unknown-role')
