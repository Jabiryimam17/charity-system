from django.db import models
from apps.auths.enums import Roles


class PromotionType(models.TextChoices):
    RANDOM = "random", "Random promotion"
    MOMENTUM = "momentum", "Momentum promotion"


class Proposal(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    region_level = models.CharField(max_length=255)
    region_name = models.CharField(max_length=255)
    budget_estimate = models.IntegerField()
    beneficiaries_estimate = models.TextField()
    questions_criteria = models.JSONField()
    proposal_file = models.FileField(upload_to='proposals/')
    proposer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    proposed_at = models.DateTimeField(auto_now_add=True)
    proposal_level = models.CharField(max_length=10, default='L1')
    proposal_score = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    proposal_status = models.CharField(max_length=50, default='pending')
    daily_score_delta = models.DecimalField(max_digits=10, decimal_places=4, default=0)

class ProposalReview(models.Model):
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reviewed_proposals'
    )
    reviewer_role = models.PositiveSmallIntegerField(choices=[(role.value, role.name) for role in Roles])
    review_justification = models.TextField()
    raw_score = models.DecimalField(max_digits=5, decimal_places=2)
    reputation_at_time = models.DecimalField(max_digits=5, decimal_places=2)
    outcome = models.CharField(max_length=20)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proposal', 'reviewer'],
                name='unique_proposal_reviewer'
            )
        ]


class ProposalRoleScoreset(models.Model):
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='role_scores'
    )
    proposal_role = models.PositiveSmallIntegerField(choices=[(role.value, role.name) for role in Roles])

    weighted_score_sum = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    reputation_sum = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    avg_weighted_score = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    review_count = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proposal', 'proposal_role'],
                name='unique_proposal_role_score'
            )
        ]


class ProposalComment(models.Model):
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='proposal_comments'
    )
    comment = models.TextField()
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class TemporaryPromotion(models.Model):
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='promotions'
    )
    promotion_type = models.CharField(max_length=20, choices=PromotionType.choices)  # 'random' or 'momentum'
    promoted_from_level = models.CharField(max_length=10)
    promoted_to_level = models.CharField(max_length=10)
    promoted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    trigger_reason = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proposal', 'promotion_type'],
                name='unique_active_promotion_type'
            )
        ]


class PromotionHistory(models.Model):
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='promotion_history'
    )
    promotion_type = models.CharField(max_length=20, choices=PromotionType.choices)
    promoted_from_level = models.CharField(max_length=10)
    promoted_to_level = models.CharField(max_length=10)
    started_at = models.DateTimeField()
    expired_at = models.DateTimeField()
    trigger_reason = models.TextField()
