from django.urls import path

from apps.proposals.views.comments import ProposalCommentsView
from apps.proposals.views.propose import ProposalSubmitView
from apps.proposals.views.submit_review import ProposalReviewView


urlpatterns = [
    path('proposals/submit/', ProposalSubmitView.as_view(), name='proposal-submit'),
    path('proposals/<int:proposal_id>/reviews/', ProposalReviewView.as_view(), name='proposal-review'),
    path('proposals/<int:proposal_id>/comments/', ProposalCommentsView.as_view(), name='proposal-comments'),
]