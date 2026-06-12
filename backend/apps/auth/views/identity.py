from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..models import VerifiedIdentity
from ..services.vision import extract_id_fields
from ..enums import IdentityStep

@login_required
@require_POST
def verify_id(request):
    if "id_image" not in request.FILES:
        return JsonResponse({"error": "No image uploaded"}, status=400)
    if VerifiedIdentity.objects.filter(user=request.user, status="verified").exists():
        return JsonResponse({"error": "Identity already verified"}, status=400)
    image_file = request.FILES["id_image"]
    image_bytes = image_file.read()
    try:
        fields = extract_id_fields(image_bytes)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    identity, _ = VerifiedIdentity.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": fields["full_name"],
            "date_of_birth": fields["date_of_birth"],
            "id_number": fields["id_number"],
            "nationality": fields["nationality"],
            "issuing_country": fields["issuing_country"],
            "region_country": fields["region_country"],
            "region_state": fields["region_state"],
            "region_city": fields["region_city"],
            "expiry_date": fields["expiry_date"],
            "confidence": fields.get("confidence", 0.0),
            "status": fields.get("status", "review"),
            "id_image": image_file,
        }

    )
    if identity.status == "verified":
        request.user.identity |= IdentityStep.GOVERNMENT_ID
        request.user.save()
    return JsonResponse({
        "status": identity.status,
        "confidence": identity.confidence,
        "fields": {
            "full_name": identity.full_name,
            "date_of_birth": identity.date_of_birth,
            "id_number": identity.id_number,
            "nationality": identity.nationality,
            "region_country": identity.region_country,
            "region_state": identity.region_state,
            "region_city": identity.region_city
        }
    })
