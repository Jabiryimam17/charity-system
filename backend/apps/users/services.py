from apps.users.tasks import update_user_score_task



class UserService:
    @staticmethod
    def on_score_updated(
        user_address,
        role_id,
        criterion_id,
        delta,
        tx_hash,
        log_index,
        block_number,
        block_timestamp,
        role_key=None,
    ):
        if user_address is None:
            return
        update_user_score_task.delay(
            user_address,
            role_id,
            criterion_id,
            delta,
            tx_hash,
            log_index,
            block_number,
            block_timestamp,
            role_key=role_key,
        )




