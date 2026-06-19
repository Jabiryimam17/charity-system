from apps.auths.services.email_otp import EmailOtpService
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
@require_POST
@api_view(['POST'])
def register_user(request):
    user = request.data.get('user')
    if user['email'] is None or user['password'] is None or user['phone_number'] is None:
        return Response({"error": "User profile not set correctly"}, status=400)
    res = EmailOtpService.register_user(None, user['user_address'], user['message'], user['signature'], user['email'],
                                        user['first_name'], user['last_name'], user['password'], user['phone_number'])
    return Response(res, status=res["status_code"], content_type='application/json; charset=utf-8', )

@require_POST
def login(request):
    res = EmailOtpService.login(request.POST.get('email'), request.POST.get('password'))
    return JsonResponse(res, status=res["status_code"], content_type='application/json; charset=utf-8', )

@require_POST
def verify_email(request):
    res = EmailOtpService.verify_email(request.POST.get('email'), request.POST.get('code'))
    return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8', )

@require_POST
def send_email_code(request):
    res = EmailOtpService.send_email_code(request.POST.get('email'))
    return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8')

@require_POST
def forget_password(request):
    res = EmailOtpService.forget_password(request.POST.get('email'))
    return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8')

@require_POST
def reset_password(request):
    res = EmailOtpService.reset_password(request.POST.get('email'), request.POST.get('password'),
                                         request.POST.get('code'))
    return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8')
