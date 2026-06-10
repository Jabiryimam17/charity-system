from django.utils import timezone
from utils.email import send_email
from tasks import update_user_score_task
from argon2 import PasswordHasher
from apps.users.models import User
from core.enums import AuthSteps, IdentityStep, Roles
class UserService:
    @staticmethod
    def on_score_updated(user_address, score_id, delta, tx_hash, log_index, block_number, block_timestamp):
        if user_address is None:
            return
        update_user_score_task.delay(user_address, score_id, delta, tx_hash, log_index, block_number, block_timestamp)


    def register_user(self, user_address: str, message: str, signature: str, email: str, first_name: str, last_name: str, password: str, phone_number: str):
        from apps.users.models import User
        from web3 import Web3
        from eth_account.messages import encode_defunct
        address_hash = Web3.keccak(text=user_address).hex()
        if not Web3.isAddress(user_address):
            raise ValueError("Invalid Ethereum address")

        signed_message = encode_defunct(text=message)
        recover_address = Web3.eth.account.recover_message(signed_message, signature)
        recover_address_hash = Web3.keccak(text=recover_address).hex()
        if recover_address_hash != address_hash:
            raise ValueError("Invalid signature")

        ph = PasswordHasher()
        hashed_password = ph.hash(password)

        User.objects.create(
            first_name=first_name,
            last_name=last_name,
            address_hash=address_hash,
            password=hashed_password,
            email=email,
            auth_steps=AuthSteps.WALLET,
            phone_number=phone_number
        )
    @staticmethod
    def login(self, email: str, password: str):
        ph = PasswordHasher()
        user = User.objects.get(email=email)
        if not ph.verify(password, user.password):
            raise ValueError("Invalid password")
        return user

    def verify_email(self, email: str, code: str) -> None:
        user = User.objects.get(email=email)
        if user.email_code != code or user.email_code_expiry  < timezone.now():
            raise ValueError("Invalid or expired verification code")
        user.auth_steps |= AuthSteps.EMAIL
        user.save()
        
    def send_email_code(self, email):
        import random
        from django.utils import timezone
        from datetime import timedelta
        user = User.objects.get(email=email)
        code = f"{random.randint(0, 999999):06d}"
        user.email_code = code
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

