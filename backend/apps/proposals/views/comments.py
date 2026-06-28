from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.proposals.models import Proposal, ProposalComment
from apps.proposals.serializers import ProposalCommentCreateSerializer, ProposalCommentSerializer


class ProposalCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, proposal_id):
        proposal = get_object_or_404(Proposal, id=proposal_id)
        comments = ProposalComment.objects.filter(proposal=proposal).select_related('user').order_by('-created_at')
        serializer = ProposalCommentSerializer(comments, many=True)
        return Response({'results': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, proposal_id):
        proposal = get_object_or_404(Proposal, id=proposal_id)
        serializer = ProposalCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = ProposalComment.objects.create(
            proposal=proposal,
            user=request.user,
            comment=serializer.validated_data['comment'],
        )

        response_serializer = ProposalCommentSerializer(comment)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
