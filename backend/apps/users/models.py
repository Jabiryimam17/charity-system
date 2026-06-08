from django.db import models

class ScoreEvents(models.Model):
    tx_hash = models.CharField(max_length=42)
    log_index = models.IntegerField()
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    user_address = models.CharField(max_length=42)
    score_id = models.IntegerField()
    delta = models.IntegerField()

class Score(models.Model):
    address = models.CharField(max_length=42)
    score_id = models.IntegerField()
    score_val = models.IntegerField()
    last_update = models.BigIntegerField()

class Config(models.Model):
    last_block = models.BigIntegerField()
