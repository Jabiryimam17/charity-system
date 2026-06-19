import pytest
import json
from django.urls import reverse
from unittest.mock import patch, MagicMock
from apps.auths.enums import AuthSteps

@pytest.mark.django_db
class TestWebAuthnViews:
    @patch('apps.auths.views.webauthn.WebAuthnHelper')
    def test_webauthn_register_begin(self, mock_helper_class, authenticated_client):
        mock_helper = mock_helper_class.return_value
        mock_helper.register_begin.return_value = ({'challenge': 'abc'}, {'state': 'xyz'})
        
        url = reverse('webauthn-register-begin')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.json() == {'challenge': 'abc'}
        assert authenticated_client.session['webauthn_state'] == {'state': 'xyz'}

    @patch('apps.auths.views.webauthn.WebAuthnHelper')
    def test_webauthn_register_complete_success(self, mock_helper_class, authenticated_client):
        mock_helper = mock_helper_class.return_value
        
        # Setup session state
        session = authenticated_client.session
        session['webauthn_state'] = {'state': 'xyz'}
        session.save()
        
        url = reverse('webauthn-register-complete')
        data = {'id': 'cred_id', 'rawId': 'cred_id'}
        response = authenticated_client.post(url, data=json.dumps(data), content_type='application/json')
        
        assert response.status_code == 200
        assert response.json() == {'success': True}
        mock_helper.register_complete.assert_called_once()
        assert 'webauthn_state' not in authenticated_client.session

    def test_webauthn_register_complete_no_state(self, authenticated_client):
        url = reverse('webauthn-register-complete')
        response = authenticated_client.post(url, data=json.dumps({}), content_type='application/json')
        assert response.status_code == 400
        assert response.json()['error'] == "No pending state"

    @patch('apps.auths.views.webauthn.WebAuthnHelper')
    def test_webauthn_register_complete_failure(self, mock_helper_class, authenticated_client):
        mock_helper = mock_helper_class.return_value
        mock_helper.register_complete.side_effect = Exception("Invalid credential")
        
        session = authenticated_client.session
        session['webauthn_state'] = {'state': 'xyz'}
        session.save()
        
        url = reverse('webauthn-register-complete')
        response = authenticated_client.post(url, data=json.dumps({}), content_type='application/json')
        
        assert response.status_code == 400
        assert "Invalid credential" in response.json()['error']

    @patch('apps.auths.views.webauthn.WebAuthnHelper')
    def test_webauthn_auth_begin(self, mock_helper_class, authenticated_client):
        mock_helper = mock_helper_class.return_value
        mock_helper.authenticate_begin.return_value = ({'challenge': 'auth_abc'}, {'state': 'auth_xyz'})
        
        url = reverse('webauthn-auth-begin')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.json() == {'challenge': 'auth_abc'}
        assert authenticated_client.session['webauthn_state'] == {'state': 'auth_xyz'}

    @patch('apps.auths.views.webauthn.WebAuthnHelper')
    def test_webauthn_auth_complete_success(self, mock_helper_class, authenticated_client, user):
        mock_helper = mock_helper_class.return_value
        
        session = authenticated_client.session
        session['webauthn_state'] = {'state': 'auth_xyz'}
        session.save()
        
        url = reverse('webauthn-auth-complete')
        response = authenticated_client.post(url, data=json.dumps({}), content_type='application/json')
        
        assert response.status_code == 200
        assert response.json() == {'success': True}
        
        user.refresh_from_db()
        assert user.auth_steps & AuthSteps.WEBAUTHN

    def test_webauthn_auth_complete_no_state(self, authenticated_client):
        url = reverse('webauthn-auth-complete')
        response = authenticated_client.post(url, data=json.dumps({}), content_type='application/json')
        assert response.status_code == 400
        assert response.json()['error'] == "No pending state"
