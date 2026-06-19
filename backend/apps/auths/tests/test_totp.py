import pytest
import pyotp
from django.urls import reverse
from apps.auths.services.totp import generate_totp_secret, verify_totp_code
from apps.auths.enums import AuthSteps

@pytest.mark.django_db
class TestTOTPService:
    def test_generate_totp_secret(self):
        secret = generate_totp_secret()
        assert len(secret) == 32
        # Check if it's base32
        import base64
        try:
            base64.b32decode(secret)
        except Exception:
            pytest.fail("Generated secret is not valid base32")

    def test_verify_totp_code_success(self):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        assert verify_totp_code(secret, code) is True

    def test_verify_totp_code_failure(self):
        secret = pyotp.random_base32()
        assert verify_totp_code(secret, "000000") is False

@pytest.mark.django_db
class TestTOTPViews:
    def test_totp_setup(self, authenticated_client):
        url = reverse('totp-setup')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert 'secret' in response.json()
        assert 'qr' in response.json()
        
        # Check session
        session = authenticated_client.session
        assert 'pending_totp_secret' in session
        assert session['pending_totp_secret'] == response.json()['secret']

    def test_totp_confirm_success(self, authenticated_client, user):
        # Setup first
        authenticated_client.get(reverse('totp-setup'))
        secret = authenticated_client.session['pending_totp_secret']
        totp = pyotp.TOTP(secret)
        code = totp.now()

        url = reverse('totp-confirm')
        response = authenticated_client.post(url, {'code': code})
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        user.refresh_from_db()
        assert user.totp_secret == secret
        assert user.auth_steps & AuthSteps.TOTP

    def test_totp_confirm_invalid_code(self, authenticated_client):
        authenticated_client.get(reverse('totp-setup'))
        
        url = reverse('totp-confirm')
        response = authenticated_client.post(url, {'code': '000000'})
        assert response.status_code == 400
        assert response.json()['error'] == "Invalid code"

    def test_totp_confirm_no_pending_secret(self, authenticated_client):
        url = reverse('totp-confirm')
        response = authenticated_client.post(url, {'code': '123456'})
        assert response.status_code == 400
        assert response.json()['error'] == "No pending secret"

    def test_totp_verify_success(self, authenticated_client, user):
        secret = pyotp.random_base32()
        user.totp_secret = secret
        user.save()
        
        totp = pyotp.TOTP(secret)
        code = totp.now()

        url = reverse('totp-verify')
        response = authenticated_client.post(url, {'code': code})
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        user.refresh_from_db()
        assert user.auth_steps & AuthSteps.TOTP

    def test_totp_verify_failure(self, authenticated_client, user):
        secret = pyotp.random_base32()
        user.totp_secret = secret
        user.save()

        url = reverse('totp-verify')
        response = authenticated_client.post(url, {'code': '000000'})
        assert response.status_code == 400
        assert response.json()['error'] == "Invalid code"

    def test_totp_verify_not_setup(self, authenticated_client, user):
        user.totp_secret = None
        user.save()

        url = reverse('totp-verify')
        response = authenticated_client.post(url, {'code': '123456'})
        assert response.status_code == 400
        assert response.json()['error'] == "TOTP not set up"

    def test_totp_re_setup(self, authenticated_client, user):
        """Test that setting up TOTP again works (duplicate case/override)"""
        # First setup
        user.totp_secret = "OLDSECRET"
        user.auth_steps |= AuthSteps.TOTP
        user.save()

        # Second setup
        authenticated_client.get(reverse('totp-setup'))
        new_secret = authenticated_client.session['pending_totp_secret']
        assert new_secret != "OLDSECRET"
        
        totp = pyotp.TOTP(new_secret)
        code = totp.now()
        
        authenticated_client.post(reverse('totp-confirm'), {'code': code})
        
        user.refresh_from_db()
        assert user.totp_secret == new_secret
        assert user.auth_steps & AuthSteps.TOTP
