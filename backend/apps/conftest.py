import pytest
from rest_framework.test import APIClient
from apps.users.models import User
@pytest.fixture
def api_client():
    return APIClient()



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
        first_name="alice",
        last_name="smith",
        email="alice@example.com",
        password="testpassword123"
    )

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        first_name="admin",
        last_name='admin',
        email='admin@example.com',
        password='testpassword123'
    )

@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        first_name="other",
        last_name="user",
        email="other@example.com",
        password="testpassword123"
    )
