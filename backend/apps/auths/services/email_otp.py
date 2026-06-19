from apps.auths.enums import AuthSteps
from apps.users.models import User
from django.utils import timezone
from apps.utils.email_manage import send_email


class EmailOtpService:
    @staticmethod
    def register_user(self, user_address: str, message: str, signature: str, email: str, first_name: str,
                      last_name: str, password: str, phone_number: str):
        from apps.users.models import User
        from web3 import Web3
        from eth_account import Account
        from eth_account.messages import encode_defunct
        if not Web3.is_address(user_address):
            return {"success": False, "message": "Invalid Ethereum address", "data": "", "status_code": 400}
        address_hash = Web3.keccak(text=user_address).hex()
        signed_message = encode_defunct(text=message)
        try:
            recover_address = Account.recover_message(signed_message, signature=signature)
            recover_address_hash = Web3.keccak(text=recover_address).hex()
        except Exception as e:
            return {"success": False, "message": "Invalid signature", "data": "", "status_code": 400}
        if recover_address_hash != address_hash:
            return {"success": False, "message": "Invalid signature", "data": "", "status_code": 400}

        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            address_hash=address_hash,
            email=email,
            auth_steps=AuthSteps.WALLET,
            phone_number=phone_number
        )
        user.set_password(password)
        user.save()
        return {"success": True, "message": "User registered successfully", "data": "", "status_code": 200}

    @staticmethod
    def login(self, email: str, password: str):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {"success": False, "message": "User not found", "data": "", "status_code": 400}
        if not user.check_password(password):
            return {"success": False, "message": "Invalid password", "data": "", "status_code": 400}
        if not user.auth_steps & AuthSteps.EMAIL:
            return {"success": False, "message": "Email not verified", "data": "", "status_code": 400}
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return {"success": True, "message": "successfully logged in", "data": {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, "status_code": 200}

    @staticmethod
    def verify_email(self, email: str, code: str) -> dict:
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
