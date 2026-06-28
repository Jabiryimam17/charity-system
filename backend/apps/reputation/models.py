from django.db import models

class ReputationCriterion(models.Model):
    """
    Master list — max 255, each maps to a smart contract bit position.
    """
    chain_id = models.PositiveSmallIntegerField(unique=True)
    key = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return f"[{self.chain_id}] {self.label}"

class UserRole(models.Model):
    """
    Maps human-readable role keys to uint8 used on-chain.
    """
    chain_id = models.PositiveSmallIntegerField(unique=True)
    key = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True)


    def __str__(self):
        return f"[{self.chain_id}] {self.label}"



class GovernanceProcess(models.Model):
    """
    Fixed core set of processes, extensible later.
    e.g. proposal_submission, plan_execution_election, procurement, etc.
    Maps human-readable process keys to uint16 used on-chain
    """
    chain_id = models.PositiveSmallIntegerField(unique=True)
    key = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=255)
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.chain_id}] {self.label}"

class ScoreEvents(models.Model):
    tx_hash = models.CharField(max_length=42)
    log_index = models.IntegerField()
    block_number = models.BigIntegerField()
    block_timestamp = models.BigIntegerField()
    user_address = models.CharField(max_length=42)
    criterion = models.ForeignKey(ReputationCriterion, on_delete=models.CASCADE, related_name='score_events')
    role = models.ForeignKey(UserRole, on_delete=models.CASCADE, related_name='score_events')
    delta = models.IntegerField()

    class Meta:
        indexes = [
            models.Index(fields=['user_address', 'role', 'score_id']),
            models.Index(fields=['block_number'])
        ]

class Score(models.Model):
    address = models.CharField(max_length=42)
    criterion = models.ForeignKey(ReputationCriterion, on_delete=models.CASCADE, related_name='scores')
    score = models.IntegerField()
    last_update = models.BigIntegerField()
    