import json
from pathlib import Path

from django.conf import settings
from web3 import Web3

from apps.reputation.models import GovernanceProcess, ReputationCriterion, UserRole
from apps.reputation.services.role_service import normalize_role_key

w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))


def _load_registrar_abi():
    artifact_path = Path(__file__).resolve().parents[4] / 'blockchain/out/User-Registral.sol/UserRegistrar.json'
    with open(artifact_path, 'r') as f:
        artifact = json.load(f)
    return artifact.get('abi', artifact)


def _get_registrar_contract():
    contract_address = settings.USER_REGISTRAR_CONTRACT_ADDRESS
    if not contract_address:
        raise ValueError('USER_REGISTRAR_CONTRACT_ADDRESS is not set')
    return w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=_load_registrar_abi())


def resolve(process_key: str | None, role_key: str, criterion_key: str = None):
    """Translate string keys to on-chain integer IDs"""

    process = GovernanceProcess.objects.get(key=process_key) if process_key else None
    role = UserRole.objects.get(key=normalize_role_key(role_key))
    criterion = ReputationCriterion.objects.get(key=criterion_key) if criterion_key else None
    return getattr(process, 'chain_id', None), role.chain_id, getattr(criterion, 'chain_id', None)


def get_process_score(user_address: str, process_key: str, role_key: str) -> int:
    """
    Ask the contract for the computed weighted score.
    This is the canonical score — never recompute in Python.
    :param user_address:
    :param process_key:
    :param role_key:
    :return:weighted score for a user
    """

    process_id, role_id, _ = resolve(process_key, role_key)
    return _get_registrar_contract().functions.calc_score(
        Web3.to_checksum_address(user_address),
        process_id,
        role_id,
    ).call()


def get_min_max_score() -> tuple[int, int]:
    contract = _get_registrar_contract()
    min_score = contract.functions.min_score().call()
    max_score = contract.functions.max_score().call()
    return min_score, max_score


def get_raw_criterion_score(user_address: str, role_key: str, criterion_key: str) -> int:
    """read a single raw criterion score from chain"""
    _, role_id, criterion_id = resolve(None, role_key, criterion_key)
    return _get_registrar_contract().functions.get_score(
        Web3.to_checksum_address(user_address),
        role_id,
        criterion_id,
    ).call()

def update_score(user_address: str, process_key: str, role_key: str, criterion_key: str, delta: int) -> int:
    """
    Backend calls this to push a score update to chain.
    Only the registrar (backend wallet) can call update_score on the contract.
    :param user_address:
    :param process_key:
    :param role_key:
    :param criterion_key:
    :param delta:
    :return:
    """
    _, role_id, criterion_id = resolve(None, role_key, criterion_key)
    update_score_tx = _get_registrar_contract().functions.update_score(
        Web3.to_checksum_address(user_address),
        role_id,
        criterion_id,
        delta
    ).build_transaction({
        'from': settings.REGISTRAR_WALLET_ADDRESS,
        'nonce': w3.eth.get_transaction_count(settings.REGISTRAR_WALLET_ADDRESS),
        'gas': 10000,
        'gasPrice': w3.eth.gas_price
    })

    signed = w3.eth.account.sign_transaction(update_score_tx, settings.REGISTRAR_WALLET_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    return tx_hash.hex()
