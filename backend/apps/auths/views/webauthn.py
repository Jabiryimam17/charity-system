import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..enums import AuthSteps
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django_otp_webauthn.helpers import WebAuthnHelper



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webauthn_register_begin(request):
    helper = WebAuthnHelper(request)
    options, state = helper.register_begin(request.user)
    request.session['webauthn_state'] = state
    return Response(options)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_register_complete(request):
    state = request.session.pop('webauthn_state', None)
    if not state: return Response({"error": "No pending state"}, status=400)
    try:
        data = request.data
        helper = WebAuthnHelper(request)
        helper.register_complete(user=request.user, state=state, data=data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    return Response({"success": True})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def webauthn_auth_begin(request):
    helper = WebAuthnHelper(request)
    options, state = helper.authenticate_begin(request.user)
    request.session['webauthn_state'] = state
    return Response(options)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webauthn_auth_complete(request):
    state = request.session.pop('webauthn_state', None)
    if not state: return Response({"error": "No pending state"}, status=400)
    try:
        data = request.data
        helper = WebAuthnHelper(request)
        helper.authenticate_complete(user=request.user, state=state, data=data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    request.user.auth_steps |= AuthSteps.WEBAUTHN
    request.user.save()
    return Response({"success": True})
