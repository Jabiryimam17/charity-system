import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..enums import AuthSteps
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_otp_webauthn.helpers import WebAuthnHelper



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
