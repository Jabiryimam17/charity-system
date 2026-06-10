from tasks import update_user_score_task
from argon2 import PasswordHasher
from apps.users.models import User
class UserService:
    @staticmethod
    def on_score_updated(user_address, score_id, delta, tx_hash, log_index, block_number, block_timestamp):
        if user_address is None:
            return
        update_user_score_task.delay(user_address, score_id, delta, tx_hash, log_index, block_number, block_timestamp)


    def register_user(self, user_address, message, signature, email, first_name, last_name, password):
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
            email=email
        )
    @staticmethod
    def login(self, email, password):
        ph = PasswordHasher()
        user = User.objects.get(email=email)
        if not ph.verify(password, user.password):
            raise ValueError("Invalid password")
        return user


