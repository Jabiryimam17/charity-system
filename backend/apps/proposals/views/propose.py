from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from django.db import transaction

from apps.proposals.models import Proposal
from apps.proposals.serializers import ProposalSerializer
from apps.proposals.services.level_service import get_initial_level_and_score
from apps.proposals.services.question_generator import build_questions
from apps.reputation.services.chain_service import get_min_max_score

class ProposalSubmitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProposalSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = serializer.validated_data

        min_score, max_score = get_min_max_score()
        initial_level, initial_score = get_initial_level_and_score(
            request.user,
            min_score=min_score,
            max_score=max_score,
        )

        payload = dict(data)
        category = payload.pop('category', None)
        if 'budget_estimation' in payload:
            payload['budget_estimate'] = payload.pop('budget_estimation')

        questions = build_questions(
            title=payload['title'],
            description=payload['description'],
            category=category or payload.get('region_level', ''),
        )

        with transaction.atomic():
            proposal = Proposal.objects.create(
                **payload,
                proposer=request.user,
                proposal_level=initial_level,
                proposal_score=initial_score,
                proposal_status='pending',
                questions_criteria=questions
            )
        return Response({
            'id': proposal.id,
            'title':proposal.title,
            'proposal_level':proposal.proposal_level,
            'proposal_score': proposal.proposal_score,
            'questions_criteria':proposal.questions_criteria,
            'proposed_at':proposal.proposed_at,
            'proposal_status':proposal.proposal_status
        }, status=status.HTTP_201_CREATED)
