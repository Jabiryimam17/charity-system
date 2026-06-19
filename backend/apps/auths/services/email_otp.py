from apps.auths.enums import AuthSteps
from apps.users.models import User
from django.utils import timezone
from apps.utils.email_manage import send_email


class EmailOtpService:
    @staticmethod
    def register_user(user_address: str, message: str, timestamp: str, signature: str, email: str, first_name: str,
                      last_name: str, password: str, phone_number: str):
        from apps.users.models import User
        from web3 import Web3
        from eth_account import Account
        from eth_account.messages import encode_defunct
        import time
        
        if not all([user_address, message, timestamp, signature, email, password]):
            return {"success": False, "message": "Missing required fields", "data": "", "status_code": 400}

        # Verify timestamp (within 1 minute)
        try:
            ts = int(timestamp)
            current_ts = int(time.time())
            if abs(current_ts - ts) > 60:
                return {"success": False, "message": "Timestamp out of range", "data": "", "status_code": 400}
        except (ValueError, TypeError):
            return {"success": False, "message": "Invalid timestamp", "data": "", "status_code": 400}

        if not Web3.is_address(user_address):
            return {"success": False, "message": "Invalid Ethereum address", "data": "", "status_code": 400}
        
        address_hash = Web3.keccak(text=user_address).hex()
        
        # Check for duplicate email
        if User.objects.filter(email=email).exists():
            return {"success": False, "message": "User with this email already exists", "data": "", "status_code": 400}
        
        # Check for duplicate wallet
        if User.objects.filter(address_hash=address_hash).exists():
            return {"success": False, "message": "User with this wallet already exists", "data": "", "status_code": 400}

        # Concatenate message and timestamp as done in frontend
        full_message = f"{message}{timestamp}"
        signed_message = encode_defunct(text=full_message)
        try:
            recover_address = Account.recover_message(signed_message, signature=signature)
            recover_address_hash = Web3.keccak(text=recover_address).hex()
        except Exception:
            return {"success": False, "message": "Invalid signature format", "data": "", "status_code": 400}
            
        if recover_address_hash != address_hash:
            return {"success": False, "message": "Invalid signature", "data": "", "status_code": 400}

        user = User.objects.create(
            username=email,
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
    def login(email: str, password: str):
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
    def verify_email(email: str, code: str) -> dict:
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {"success": False, "message": "User not found", "data": "", "status_code": 400}
            
        if not user.email_code or user.email_code != code:
            return {"success": False, "message": "Invalid verification code", "data": "", "status_code": 400}
            
        if user.email_code_expiry < timezone.now():
            return {"success": False, "message": "Expired verification code", "data": "", "status_code": 400}
            
        user.auth_steps |= AuthSteps.EMAIL
        # Clear code after success
        user.email_code = None
        user.save()
        return {"success": True, "message": "Email verified successfully", "data": "", "status_code": 200}

    @staticmethod
    def send_email_code(email: str):
        import random
        from datetime import timedelta
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {"success": False, "message": "User not found", "data": "", "status_code": 400}
            
        code = f"{random.randint(0, 999999):06d}"
        user.email_code = code
        user.email_code_expiry = timezone.now() + timedelta(minutes=10)
        
        if send_email(code, email):
            user.save()
        else:
            return {"success": False, "message": "Failed to send email", "data": "", "status_code": 500}
        return {"success": True, "message": "Verification code sent", "data": "", "status_code": 200}

    @staticmethod
    def forget_password(email: str):
        return EmailOtpService.send_email_code(email)

    @staticmethod
    def reset_password(email: str, password: str, code: str):
        res = EmailOtpService.verify_email(email, code)
        if res["success"]:
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                return {"success": True, "message": "Password reset successfully", "data": "", "status_code": 200}
            except User.DoesNotExist:
                return {"success": False, "message": "User not found", "data": "", "status_code": 400}
        return res
