from apps.auths.enums import Roles
from apps.reputation.models import UserRole


ROLE_NAME_ALIASES: dict[str, str] = {
    'DONOR': 'DONATOR',
}


def normalize_role_key(role_key: str) -> str:
    return role_key.strip().lower()


def _normalize_role_name(role_name: str) -> str:
    normalized = role_name.strip().upper()
    if normalized in ROLE_NAME_ALIASES:
        return ROLE_NAME_ALIASES[normalized]
    return normalized


def role_key_to_chain_id(role_key: str) -> int:
    key = normalize_role_key(role_key)
    try:
        return UserRole.objects.only('chain_id').get(key=key).chain_id
    except UserRole.DoesNotExist as exc:
        raise ValueError(f'Unknown role key: {role_key}') from exc


def chain_id_to_role_key(chain_role_id: int) -> str:
    try:
        return UserRole.objects.only('key').get(chain_id=int(chain_role_id)).key
    except UserRole.DoesNotExist as exc:
        raise ValueError(f'Unknown chain role id: {chain_role_id}') from exc


def role_key_to_app_role_value(role_key: str) -> int:
    enum_name = _normalize_role_name(role_key)
    try:
        return Roles[enum_name].value
    except KeyError as exc:
        raise ValueError(f'Unknown application role key: {role_key}') from exc


def chain_id_to_app_role_value(chain_role_id: int) -> int:
    role_key = chain_id_to_role_key(chain_role_id)
    return role_key_to_app_role_value(role_key)


def to_app_role_value(role) -> int:
    if isinstance(role, Roles):
        return role.value

    if isinstance(role, int):
        try:
            Roles(role)
        except ValueError as exc:
            raise ValueError(f'Unknown role value: {role}') from exc
        return role

    if isinstance(role, str):
        candidate = role.strip()
        if not candidate:
            raise ValueError('Role cannot be empty')
        if candidate.isdigit():
            return to_app_role_value(int(candidate))
        try:
            return role_key_to_app_role_value(candidate)
        except ValueError:
            enum_name = _normalize_role_name(candidate)
            try:
                return Roles[enum_name].value
            except KeyError as exc:
                raise ValueError(f'Unknown role name: {candidate}') from exc

    raise ValueError(f'Unsupported role type: {type(role).__name__}')
