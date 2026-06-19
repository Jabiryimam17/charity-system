import pytest
from apps.auths.services.email_otp import EmailOtpService
from apps.users.models import User
from apps.auths.enums import AuthSteps
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

@pytest.mark.django_db
class TestEmailOtpService:
    def test_register_user(self, wallet_user_payload):
        res = EmailOtpService.register_user(
            wallet_user_payload['user_address'],
            wallet_user_payload['message'],
            wallet_user_payload['timestamp'],
            wallet_user_payload['signature'],
            wallet_user_payload['email'],
            wallet_user_payload['first_name'],
            wallet_user_payload['last_name'],
            wallet_user_payload['password'],
            wallet_user_payload['phone_number']
        )
        assert res['success'] is True
        assert User.objects.filter(email=wallet_user_payload['email']).exists()
        user = User.objects.get(email=wallet_user_payload['email'])
        assert user.auth_steps == AuthSteps.WALLET

    def test_send_email_code(self, user):
        with patch('apps.auths.services.email_otp.send_email', return_value=True):
            res = EmailOtpService.send_email_code(user.email)
            assert res['success'] is True
            user.refresh_from_db()
            assert user.email_code is not None
            assert user.email_code_expiry > timezone.now()

    def test_verify_email_success(self, user):
        user.email_code = '123456'
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        res = EmailOtpService.verify_email(user.email, '123456')
        assert res['success'] is True
        user.refresh_from_db()
        assert user.auth_steps & AuthSteps.EMAIL

    def test_verify_email_invalid_code(self, user):
        user.email_code = '123456'
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        res = EmailOtpService.verify_email(user.email, 'wrong')
        assert res['success'] is False
        assert res['status_code'] == 400

    def test_login_success(self, user):
        user.auth_steps |= AuthSteps.EMAIL
        user.set_password('testpassword123')
        user.save()

        res = EmailOtpService.login(user.email, 'testpassword123')
        assert res['success'] is True
        assert 'access' in res['data']
        assert 'refresh' in res['data']

    def test_login_email_not_verified(self, user):
        user.auth_steps = AuthSteps.NONE
        user.set_password('testpassword123')
        user.save()

        res = EmailOtpService.login(user.email, 'testpassword123')
        assert res['success'] is False
        assert "Email not verified" in res['message']

    def test_forget_password(self, user):
        with patch('apps.auths.services.email_otp.send_email', return_value=True):
            res = EmailOtpService.forget_password(user.email)
            assert res['success'] is True
            user.refresh_from_db()
            assert user.email_code is not None

    def test_verify_email_expired_code(self, user):
        user.email_code = '123456'
        user.email_code_expiry = timezone.now() - timedelta(minutes=1)
        user.save()

        res = EmailOtpService.verify_email(user.email, '123456')
        assert res['success'] is False
        assert "Expired" in res['message']

    def test_verify_email_user_not_found(self):
        res = EmailOtpService.verify_email("nonexistent@example.com", '123456')
        assert res['success'] is False
        assert "User not found" in res['message']

    def test_send_email_code_user_not_found(self):
        res = EmailOtpService.send_email_code("nonexistent@example.com")
        assert res['success'] is False
        assert "User not found" in res['message']

    def test_register_user_duplicate_email(self, wallet_user_payload, second_wallet):
        # First registration
        EmailOtpService.register_user(**wallet_user_payload)
        
        # Second registration with same email but different wallet
        wallet_user_payload['user_address'] = second_wallet['address']
        wallet_user_payload['message'] = second_wallet['message']
        wallet_user_payload['timestamp'] = second_wallet['timestamp']
        wallet_user_payload['signature'] = second_wallet['signature']
        
        res = EmailOtpService.register_user(**wallet_user_payload)
        assert res['success'] is False
        assert "email already exists" in res['message']

    def test_register_user_duplicate_wallet(self, wallet_user_payload):
        # First registration
        EmailOtpService.register_user(**wallet_user_payload)
        
        # Second registration with same wallet but different email
        wallet_user_payload['email'] = 'other@example.com'
        
        res = EmailOtpService.register_user(**wallet_user_payload)
        assert res['success'] is False
        assert "wallet already exists" in res['message']

    def test_reset_password_success(self, user):
        user.email_code = '123456'
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        res = EmailOtpService.reset_password(user.email, 'newpassword123', '123456')
        assert res['success'] is True
        user.refresh_from_db()
        assert user.check_password('newpassword123')
