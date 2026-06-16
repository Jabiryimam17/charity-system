import pytest
from apps.users.models import User


@pytest.mark.django_db
def test_user_creation():
    user = User.objects.create(first_name="Alice", last_name="Smith", email="bob@example.com")
    assert user.id is not None
    assert user.get_full_name() == "Alice Smith"


@pytest.mark.django_db
def test_email_must_be_unique():
    User.objects.create(first_name="Alice", last_name="Smith", email="bob@gmail.com")
    with pytest.raises(Exception, match="already exists."):
        User.objects.create(first_name="Jabir", last_name="Yimam", email="bob@gmail.com")


@pytest.mark.django_db
def test_address_hash_must_be_unique():
    User.objects.create(first_name='Alice', address_hash='0x1234567890123456789012345678901234567890')
    with pytest.raises(Exception, match="already exists."):
        User.objects.create(first_name='Bob', address_hash='0x1234567890123456789012345678901234567890')


@pytest.mark.django_db
def test_phone_number_must_be_unique():
    User.objects.create(first_name='Alice', phone_number='1234567890')
    with pytest.raises(Exception, match="already exists."):
        User.objects.create(first_name='Bob', phone_number='1234567890')

@pytest.mark.django_db
def test_default_values():
    user =User.objects.create(first_name="alice")
    assert user.identity_steps == 0
    assert user.auth_steps == 0
    assert user.email_code is None
    assert user.email_code_expiry is None
    assert user.totp_secret is None


@pytest.mark.django_db
def test_get_full_name():
    user = User.objects.create(first_name="Alice", last_name="Smith")
    assert user.get_full_name() == "Alice Smith"

@pytest.mark.django_db
def test_get_user_name():
    user = User.objects.create(first_name="Alice", last_name="Smith", email='bob@gmail.com')
    assert user.get_username() == "bob@gmail.com"