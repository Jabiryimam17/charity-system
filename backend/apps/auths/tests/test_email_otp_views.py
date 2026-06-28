import pytest
from django.urls import reverse
from apps.auths.enums import AuthSteps
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from web3 import Web3

@pytest.mark.django_db
class TestEmailOtpViews:
    def test_register_user_view(self, api_client, wallet_user_payload):
        url = reverse('register-user')
        data = {'user': wallet_user_payload}
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True

    def test_login_view(self, api_client, user):
        user.auth_steps |= AuthSteps.EMAIL
        user.set_password('testpassword123')
        user.address_hash = Web3.keccak(text='0x1111111111111111111111111111111111111111').hex()
        user.save()

        url = reverse('login')
        data = {
            'email': user.email,
            'password': 'testpassword123',
            'user_address': '0x1111111111111111111111111111111111111111',
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True

    def test_send_email_code_view(self, api_client, user):
        url = reverse('send-email-code')
        data = {'email': user.email}
        with patch('apps.auths.services.email_otp.send_email', return_value=True):
            response = api_client.post(url, data, format='json')
            assert response.status_code == 200
            assert response.data['success'] is True

    def test_verify_email_view(self, api_client, user):
        user.email_code = '123456'
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        url = reverse('verify-email')
        data = {'email': user.email, 'code': '123456'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True

    def test_forget_password_view(self, api_client, user):
        url = reverse('forget-password')
        data = {'email': user.email}
        with patch('apps.auths.services.email_otp.send_email', return_value=True):
            response = api_client.post(url, data, format='json')
            assert response.status_code == 200
            assert response.data['success'] is True

    def test_reset_password_view(self, api_client, user):
        user.email_code = '123456'
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        url = reverse('reset-password')
        data = {'email': user.email, 'password': 'newpassword123', 'code': '123456'}
        response = api_client.post(url, data, format='json')
        assert response.status_code == 200
        assert response.data['success'] is True
