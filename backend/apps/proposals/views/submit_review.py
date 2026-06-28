from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.proposals.models import Proposal
from apps.proposals.serializers import ProposalReviewSerializer
from apps.proposals.services.submit_review import submit_review


class ProposalReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, proposal_id):
        proposal = get_object_or_404(Proposal, id=proposal_id)
        role_scores = []
        for score in proposal.role_scores.all():
            role_scores.append(
                {
                    'role': score.proposal_role,
                    'avg_weighted_score': score.avg_weighted_score,
                    'review_count': score.review_count,
                }
            )
        return Response(
            {
                'proposal_id': proposal.id,
                'proposal_level': proposal.proposal_level,
                'questions_criteria': proposal.questions_criteria,
                'role_scores': role_scores,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, proposal_id):
        serializer = ProposalReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        proposal = get_object_or_404(Proposal, id=proposal_id)
        if proposal.proposer_id == request.user.id:
            return Response(
                {'message': 'Proposers cannot review their own proposal'},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = serializer.validated_data
        try:
            review = submit_review(
                proposal_id=proposal.id,
                reviewer=request.user,
                role_key=data['role'],
                question_scores=data['question_scores'],
                outcome=data['outcome'],
                justification=data['justification'],
            )
        except ValueError as exc:
            return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        proposal.refresh_from_db(fields=['proposal_level'])
        return Response(
            {
                'proposal_id': proposal.id,
                'proposal_level': proposal.proposal_level,
                'outcome': data['outcome'],
                'reviewed_at': review.reviewed_at,
            },
            status=status.HTTP_201_CREATED,
        )

