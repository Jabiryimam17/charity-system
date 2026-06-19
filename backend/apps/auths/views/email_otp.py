from apps.auths.services.email_otp import EmailOtpService
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
@require_POST
@api_view(['POST'])
def register_user(request):
    user_data = request.data.get('user')
    if user_data.get('email') is None or user_data.get('password') is None or user_data.get('phone_number') is None:
        return Response({"error": "User profile not set correctly"}, status=400)
    res = EmailOtpService.register_user(user_data.get('user_address'), user_data.get('message'),
                                        user_data.get('timestamp'),
                                        user_data.get('signature'), user_data.get('email'),
                                        user_data.get('first_name'), user_data.get('last_name'),
                                        user_data.get('password'), user_data.get('phone_number'))
    return Response(res, status=res["status_code"], content_type='application/json; charset=utf-8', )

@require_POST
@api_view(['POST'])
def login(request):
    res = EmailOtpService.login(request.data.get('email'), request.data.get('password'))
    return Response(res, status=res["status_code"], content_type='application/json; charset=utf-8', )

@require_POST
@api_view(['POST'])
def verify_email(request):
    res = EmailOtpService.verify_email(request.data.get('email'), request.data.get('code'))
    return Response(res, status=res['status_code'], content_type='application/json; charset=utf-8', )

@require_POST
@api_view(['POST'])
def send_email_code(request):
    res = EmailOtpService.send_email_code(request.data.get('email'))
    return Response(res, status=res['status_code'], content_type='application/json; charset=utf-8')

@require_POST
@api_view(['POST'])
def forget_password(request):
    res = EmailOtpService.forget_password(request.data.get('email'))
    return Response(res, status=res['status_code'], content_type='application/json; charset=utf-8')

@require_POST
@api_view(['POST'])
def reset_password(request):
    res = EmailOtpService.reset_password(request.data.get('email'), request.data.get('password'),
                                         request.data.get('code'))
    return Response(res, status=res['status_code'], content_type='application/json; charset=utf-8')
