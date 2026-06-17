from apps.auths.services.email_otp import EmailOtpService
from django.http import JsonResponse
from django.views.decorators.http import require_POST


class EmailOtpView:
    @staticmethod
    @require_POST
    def register_user(self, request):
        user = request.POST.get('user')
        if user.email is None or user.password is None or user.phone_number is None:
            return JsonResponse({"error": "User profile not set correctly"}, status=400)
        res = EmailOtpService.register_user(self, user.user_address, user.message, user.signature, user.email,
                                            user.first_name, user.last_name, user.password, user.phone_number)
        return JsonResponse(res, status=res["status_code"], content_type='application/json; charset=utf-8', )

    @staticmethod
    @require_POST
    def login(self, request):
        res = EmailOtpService.login(self, request.POST.get('email'), request.POST.get('password'))
        return JsonResponse(res, status=res["status_code"], content_type='application/json; charset=utf-8', )

    @staticmethod
    @require_POST
    def verify_email(self, request):
        res = EmailOtpService.verify_email(self, request.POST.get('email'), request.POST.get('code'))
        return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8', )

    @staticmethod
    @require_POST
    def send_email_code(self, request):
        res = EmailOtpService.send_email_code(self, request.POST.get('email'))
        return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8')

    @staticmethod
    @require_POST
    def forget_password(self, request):
        res = EmailOtpService.forget_password(self, request.POST.get('email'))
        return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8')

    @staticmethod
    @require_POST
    def reset_password(self, request):
        res = EmailOtpService.reset_password(self, request.POST.get('email'), request.POST.get('password'),
                                             request.POST.get('code'))
        return JsonResponse(res, status=res['status_code'], content_type='application/json; charset=utf-8')
