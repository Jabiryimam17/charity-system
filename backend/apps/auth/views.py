import json

from attrs import exceptions
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .totp import generate_totp_secret, get_totp_uri, generate_qr_base64, verify_totp_code
from .enums import AuthSteps
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_otp_webauthn.models import WebAuthnCredential
from django.conf import settings
from django_otp_webauthn.helpers import WebAuthnHelper


@login_required
def totp_setup(request):
    """Step 1: generate_totp_secret + return QR code"""
    secret = generate_totp_secret()
    uri = get_totp_uri(secret, request.user.email)
    qr = generate_qr_base64(uri)
    request.session['pending_totp_secret'] = secret
    return JsonResponse({"secret": secret, "qr": f"data:image/png;base64,{qr}"})


@login_required
@require_POST
def totp_confirm(request):
    """Step 2: user scans QR, enters first code to confirm setup"""
    secret = request.session.pop('pending_totp_secret')
    code = request.POST.get('code').strip()
    if not secret: return JsonResponse({"error": "No pending secret"}, status=400)
    if not verify_totp_code(secret, code): return JsonResponse({"error": "Invalid code"}, status=400)
    request.user.totp_secret = secret
    if request.user.auth_steps | AuthSteps.TOTP == request.user.auth_steps: request.user.auth_steps ^= AuthSteps.TOTP
    request.user.save()
    return JsonResponse({"success": True})


@login_required
@require_POST
def totp_verify(request):
    """Step 3: called during login to verify TOTP code+flip bit"""
    code = request.POST.get('code').strip()
    if not request.user.totp_secret: return JsonResponse({"error": "TOTP not set up"}, status=400)
    if not verify_totp_code(request.user.totp_secret, code): return JsonResponse({"error": "Invalid code"}, status=400)
    request.user.auth_steps |= AuthSteps.TOTP
    request.user.save()
    return JsonResponse({"success": True})


@login_required
def webauthn_register_begin(request):
    helper = WebAuthnHelper(request)
    options, state = helper.register_begin(request.user)
    request.session['webauthn_state'] = state
    return JsonResponse(options)


@login_required
@csrf_exempt
@require_POST
def webauthn_register_complete(request):
    state = request.session.pop('webauthn_state')
    if not state: return JsonResponse({"error": "No pending state"}, status=400)
    try:
        data = json.loads(request.body)
        helper = WebAuthnHelper(request)
        helper.register_complete(user=request.user, state=state, data=data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"success": True})


@login_required
def webauthn_auth_begin(request):
    helper = WebAuthnHelper(request)
    options, state = helper.authenticate_begin(request.user)
    request.session['webauthn_state'] = state
    return JsonResponse(options)


@login_required
@csrf_exempt
@require_POST
def webauthn_auth_complete(request):
    state = request.session.pop('webauthn_state')
    if not state: return JsonResponse({"error": "No pending state"}, status=400)
    try:
        data = json.loads(request.body)
        helper = WebAuthnHelper(request)
        helper.authenticate_complete(user=request.user, state=state, data=data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    request.user.auth_steps |= AuthSteps.WEBAUTHN
    request.user.save()
    return JsonResponse({"success": True})
