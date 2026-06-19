import pytest
from rest_framework.test import APIClient
from apps.users.models import User
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def wallet():
    """
    Generates a random Ethereum keypair + a signed message.
    Use this anywhere you need a valid wallet + signature combo.
    """
    account = Account.create()
    message = "Register my wallet"
    signed = account.sign_message(encode_defunct(text=message))
    return {
        "account": account,
        "address": account.address,
        "message": message,
        "signature": signed.signature.hex()
    }

@pytest.fixture
def wallet_user_payload(wallet):
    """
    :return: returns a sample user input for registration
    """
    return {
        'user_address': wallet['address'],
        'message': wallet['message'],
        'signature': wallet['signature'],
        'email':'alice@example.com',
        'first_name':'Alice',
        'last_name':'Smith',
        'password':'test123example',
        'phone_number': '+251923456789'
    }

@pytest.fixture
def second_wallet():
    """ A second independent wallet — useful for ownership/conflict tests """
    account = Account.create()
    message = "Register my wallet"
    signed = account.sign_message(encode_defunct(text=message))
    return {
        "account": account,
        "address": account.address,
        "message": message,
        "signature": signed.signature.hex(),
    }

@pytest.fixture
def wallet_user(db, wallet):
    """
    A fully registered user with a real Ethereum wallet attached.
    Equivalent to admin_user but for blockchain-authenticated users.
    :return:
    """
    from apps.auths.enums import  AuthSteps
    from argon2 import PasswordHasher
    address_hash = Web3.keccak(text=wallet["address"]).hex()
    user = User.objects.create(
        username="alice@example.com",
        first_name="alice",
        last_name="smith",
        email='alice@example.com',
        phone_number='+251923456789',
        address_hash=address_hash,
        auth_steps=AuthSteps.WALLET,
        password=PasswordHasher().hash("test123example")
    )
    user.save()
    user.wallet = wallet
    return user

@pytest.fixture
def second_wallet_user(db, second_wallet):
    """ A second wallet user — for duplicate/ownership/conflict tests """
    from argon2 import PasswordHasher
    from apps.auths.enums import  AuthSteps
    address_hash = Web3.keccak(text=second_wallet["address"]).hex()

    user = User.objects.create(
        first_name   = "Bob",
        last_name    = "Smith",
        email        = "bob@example.com",
        phone_number = "+251911000001",
        address_hash = address_hash,
        auth_steps   = AuthSteps.WALLET,
        password=PasswordHasher.hash("strong123!")
    )
    user.save()
    user.wallet = second_wallet
    return user

@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="alice@example.com",
        first_name="alice",
        last_name="smith",
        email="alice@example.com",
        password="testpassword123"
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin@example.com",
        first_name="admin",
        last_name='admin',
        email='admin@example.com',
        password='testpassword123'
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username="other@example.com",
        first_name="other",
        last_name="user",
        email="other@example.com",
        password="testpassword123"
    )
