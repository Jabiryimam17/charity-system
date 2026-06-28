from celery import shared_task
from .momentum_promotion import run_momentum_promotion
from .random_promotion import run_random_promotion
@shared_task
def momentum_promotion_task():
    run_momentum_promotion()


@shared_task
def random_promotion_task():
    run_random_promotion()