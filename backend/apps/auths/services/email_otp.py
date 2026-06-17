from apps.auths.models import User
from apps.auths.enums import AuthSteps
from argon2 import PasswordHasher
from django.utils import timezone
from apps.utils.email_manage import send_email
from requests import status_codes


class EmailOtpService:
    @staticmethod
    def register_user(self, user_address: str, message: str, signature: str, email: str, first_name: str,
                      last_name: str, password: str, phone_number: str):
        from apps.users.models import User
        from web3 import Web3
        from eth_account.messages import encode_defunct
        address_hash = Web3.keccak(text=user_address).hex()
        if not Web3.isAddress(user_address):
            return {"success": False, "message": "Invalid Ethereum address", "data": "", "status_code": 400}

        signed_message = encode_defunct(text=message)
        recover_address = Web3.eth.account.recover_message(signed_message, signature)
        recover_address_hash = Web3.keccak(text=recover_address).hex()
        if recover_address_hash != address_hash:
            return {"success": False, "message": "Invalid signature", "data": "", "status_code": 400}

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
        return {"success": True, "message": "User registered successfully", "data": "", "status_code": 200}

    @staticmethod
    def login(self, email: str, password: str):
        ph = PasswordHasher()
        user = User.objects.get(email=email)
        if not ph.verify(password, user.password):
            return {"success": False, "message": "Invalid password", "data": "", "status_code": 400}
        return {"success": True, "message": "successfully logged in", "data": user, "status_code": 200}

    @staticmethod
    def verify_email(self, email: str, code: str) -> None:
        user = User.objects.get(email=email)
        if user.email_code != code or user.email_code_expiry < timezone.now():
            return {"success": False, "message": "Invalid or expired verification code", "data": "",
                    "status_code": 400}
        user.auth_steps |= AuthSteps.EMAIL
        user.save()
        return {"success": True, "message": "Email verified successfully", "data": "", "status_code": 200}

    @staticmethod
    def send_email_code(self, email: str):
        import random
        from django.utils import timezone
        from datetime import timedelta
        user = User.objects.get(email=email)
        if user is None:
            return {"success": False, "message": "User not found", "data": "",
                    "status_code": 400}
        code = f"{random.randint(0, 999999):06d}"
        user.email_code = code
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        if send_email(code, email):
            user.save()
        else:
            return {"success": False, "message": "Failed to send email", "data": "", "status_code": 500}
        return {"success": True, "message": "Verification code sent", "data": "", "status_code": 200}

    @staticmethod
    def forget_password(self, email: str):
        return self.send_email_code(email)

    @staticmethod
    def reset_password(self, email: str, password: str, code: str):
        res = self.verify_email(email, code)
        if res.success:
            ph = PasswordHasher()
            hashed_password = ph.hash(password)
            User.objects.update_or_create(
                email=email,
                defaults={"password": hashed_password}
            )
            return {"success": True, "message": "Password reset successfully", "data": "", "status_code": 200}
        return {"success": False, "message": "Invalid code or email", "data": "", "status_code": 400}
