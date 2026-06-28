from rest_framework import serializers
from apps.proposals.models import Proposal, ProposalComment
from apps.reputation.services.chain_service import get_process_score


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = [
            'title', 'description', 'category', 'region_level', 'region_name',
            'budget_estimation', 'beneficiaries_estimate','proposal_file'
        ]


class ProposalReviewSerializer(serializers.Serializer):
    role = serializers.CharField()
    question_scores = serializers.ListField(
        child=serializers.IntegerField(min_value=1, max_value=10),
        allow_empty=False,
    )
    outcome = serializers.ChoiceField(choices=['support', 'concern', 'reject', 'escalate'])
    justification = serializers.CharField()


class ProposalCommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_score = serializers.SerializerMethodField()

    class Meta:
        model = ProposalComment
        fields = ['id', 'proposal', 'user_id', 'comment', 'likes', 'dislikes', 'user_score', 'created_at']
        read_only_fields = ['id', 'proposal', 'user_id', 'likes', 'dislikes', 'user_score', 'created_at']

    def get_user_score(self, obj):
        role_key = getattr(obj.user, 'primary_role_key', None)
        wallet_address = getattr(obj.user, 'wallet_address', None)
        if not role_key or not wallet_address:
            return 0
        try:
            return get_process_score(wallet_address, 'proposal_review', role_key)
        except Exception:
            return 0


class ProposalCommentCreateSerializer(serializers.Serializer):
    comment = serializers.CharField(allow_blank=False)
