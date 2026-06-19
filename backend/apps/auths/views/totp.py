
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..services.totp import generate_totp_secret, get_totp_uri, generate_qr_base64, verify_totp_code
from ..enums import AuthSteps
from django.contrib.auth.decorators import login_required



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def totp_setup(request):
    """Step 1: generate_totp_secret + return QR code"""
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, request.user.email)
    qr = generate_qr_base64(uri)
    request.session['pending_totp_secret'] = secret
    return Response({"secret": secret, "qr": f"data:image/png;base64,{qr}"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def totp_confirm(request):
    """Step 2: user scans QR, enters first code to confirm setup"""
    secret = request.session.get('pending_totp_secret')
    if not secret: return Response({"error": "No pending secret"}, status=400)
    
    code = request.data.get('code', '').strip()
    if not code: return Response({"error": "Code is required"}, status=400)
    
    if not verify_totp_code(secret, code): return Response({"error": "Invalid code"}, status=400)
    
    request.session.pop('pending_totp_secret')
    request.user.totp_secret = secret
    request.user.auth_steps |= AuthSteps.TOTP
    request.user.save()
    return Response({"success": True})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def totp_verify(request):
    """Step 3: called during login to verify TOTP code+flip bit"""
    code = request.data.get('code', '').strip()
    if not request.user.totp_secret: return Response({"error": "TOTP not set up"}, status=400)
    if not verify_totp_code(request.user.totp_secret, code): return Response({"error": "Invalid code"}, status=400)
    request.user.auth_steps |= AuthSteps.TOTP
    request.user.save()
    return Response({"success": True})