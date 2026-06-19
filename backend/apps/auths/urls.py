from django.urls import path
import apps.auths.views as views
urlpatterns = [
    path('mfs/setup/', views.totp_setup, name='totp-setup'),
    path('mfs/verify/', views.totp_verify, name='totp-verify'),
    path('mfs/confirm/', views.totp_confirm, name='totp-confirm'),
    path('webauthn/register/begin', views.webauthn_register_begin, name='webauthn-register-begin'),
    path('webauthn/register/complete/',views.webauthn_register_complete, name='webauthn-register-complete'),
    path('webauthn/auth/begin/', views.webauthn_auth_begin, name='webauthn-auth-begin'),
    path('webauthn/auth/complete/', views.webauthn_auth_complete, name='webauthn-auth-complete'),
    path("identity/verify-id/", views.verify_id, name="verify-id"),
    path("documents/submit/", views.submit_document, name="submit-document"),
    path("documents/status/<int:doc_id>/", views.document_status, name="document-status"),
    path("email-otp/register/", views.register_user, name="register-user"),
    path("email-otp/login/", views.login, name="login"),
    path("email-otp/verify-email/", views.verify_email, name="verify-email"),
    path("email-otp/send-email-code/", views.send_email_code, name="send-email-code"),
    path("email-otp/forget-password/", views.forget_password, name="forget-password"),
    path("email-otp/reset-password/", views.reset_password, name="reset-password")
]