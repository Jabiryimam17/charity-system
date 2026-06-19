import pytest
from apps.conftest import api_client
from apps.users.models import User
from django.contrib.auth.base_user import AbstractBaseUser

REGISTER_URL = '/api/auths/email-otp/register/'

@pytest.mark.django_db
def test_register_user(api_client, wallet):
    response = api_client.post(REGISTER_URL,{
        'user':{
            'user_address':wallet['address'],
            'message':wallet['message'],
            'signature':wallet['signature'],
            'email':"alice@example.com",
            'first_name': 'Alice',
            'last_name': 'Smith',
            'password': 'testpassword123',
            'phone_number': '+251923456789'
        }

    }, format='json')
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_exists(api_client, wallet):
    api_client.post(REGISTER_URL,{
        'user':{
            'user_address':wallet['address'],
            'message':wallet['message'],
            'signature':wallet['signature'],
            'email':'alice@example.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'password': 'testpassword123',
            'phone_number': '+251923456789'
        }
    }, format='json')
    assert User.objects.filter(email='alice@example.com').exists()

@pytest.mark.django_db
def test_address_hash_stored_not_raw_address(api_client, wallet_user_payload, wallet):
    from web3 import Web3
    api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    user = User.objects.get(email='alice@example.com')
    assert user.address_hash != wallet['address']
    assert Web3.keccak(text=wallet['address']).hex() == user.address_hash

@pytest.mark.django_db
def test_password_hashed(api_client, wallet_user_payload):
    api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    user = User.objects.get(email="alice@example.com")
    assert user.check_password('test123example')
@pytest.mark.django_db
def test_invalid_email(api_client, wallet_user_payload):
    wallet_user_payload['email']=None
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_invalid_password(api_client, wallet_user_payload):
    wallet_user_payload['password']=None
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_invalid_phone_number(api_client, wallet_user_payload):
    wallet_user_payload['phone_number']=None
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400
    
@pytest.mark.django_db
def test_register_response_shape(api_client, wallet_user_payload):
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.data['success'] == True
    assert 'password' not in response.data['data']
    assert 'address' not in response.data['data']

@pytest.mark.django_db
def test_invalid_ethereum_address(api_client, wallet_user_payload):
    wallet_user_payload['user_address'] = '0x1234'
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400
    assert response.data['success'] == False
    assert "Invalid Ethereum address" in response.data['message']


@pytest.mark.django_db
def test_invalid_signature(api_client, wallet_user_payload):
    wallet_user_payload['signature'] = "0x" + "ab" * 65
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400
    assert response.data['success'] == False
    assert "Invalid signature" in response.data['message']
@pytest.mark.django_db
def test_duplicate_email_returns_400(api_client, wallet_user_payload, second_wallet):
    api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    
    # New wallet, but same email
    wallet_user_payload['user_address'] = second_wallet['address']
    wallet_user_payload['message'] = second_wallet['message']
    wallet_user_payload['signature'] = second_wallet['signature']
    
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400
    assert "email already exists" in response.data['message']

@pytest.mark.django_db
def test_duplicate_wallet_returns_400(api_client, wallet_user_payload):
    api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    
    # Different email, but same wallet
    wallet_user_payload['email'] = 'bob@example.com'
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400
    assert "wallet already exists" in response.data['message']
@pytest.mark.django_db
def test_signature_from_different_wallet_returns_400(api_client, wallet_user_payload, second_wallet):
    wallet_user_payload['signature'] = second_wallet['signature']
    response = api_client.post(REGISTER_URL,{
        'user':wallet_user_payload
    }, format='json')
    assert response.status_code == 400
    assert response.data['success'] == False
    assert "Invalid signature" in response.data['message']

@pytest.mark.django_db
def test_user_auth_step_set_to_wallet(api_client, wallet_user_payload):
    from apps.auths.enums import AuthSteps
    api_client.post(REGISTER_URL,{'user':wallet_user_payload}, format='json')
    user = User.objects.get(email=wallet_user_payload['email'])
    assert user.auth_steps == AuthSteps.WALLET.value

