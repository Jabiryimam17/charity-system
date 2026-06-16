from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.auth.models import DocumentReview
from apps.auth.services.vision import extract_insight


@login_required
@require_POST
def submit_document(request):
    if "document" not in request.FILES:
        return JsonResponse({"error": "No document uploaded"}, status=400)
    doc_type = request.POST.get('doc_type', "other")
    image = request.FILES["document"]

    try:
        ai_data = extract_insight(image.read())
        image.seek(0)
    except Exception as e:
        ai_data = {}
    doc = DocumentReview.objects.create(
        user=request.user,
        doc_type=doc_type,
        image=image,
        ai_data=ai_data,
        status=DocumentReview.Status.PENDING,
    )
    return JsonResponse({
        "id": doc.id
        , "status": doc.status,
        "message": "Document submitted successfully. Please wait for review."
    })


@login_required
def document_status(request, doc_id):
    try:
        doc = DocumentReview.objects.get(id=doc_id, user=request.user)
    except DocumentReview.DoesNotExist:
        return JsonResponse({"error": "Document not found"}, status=404)
    return JsonResponse({
        "status": doc.status,
        "doc_type": doc.doc_type,
        "submitted_at": doc.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
        "reviewed_at": doc.reviewed_at.strftime("%Y-%m-%d %H:%M:%S") if doc.reviewed_at else "",
        "notes": doc.notes

    })
