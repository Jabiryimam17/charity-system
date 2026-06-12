from django.urls import path
import views

urlpatterns = [
    path('mfs/setup/', views.totp_setup, name='totp-setup'),
    path('mfs/verify/', views.totp_verify, name='totp-verify'),
    path('mfs/confirm/', views.totp_confirm, name='totp-confirm'),
    path('webauthn/register/begin', views.webauthn_register_begin, name='webauthn-register-begin'),
    path('webauthn/register/complete/', views.webauthn_register_complete, name='webauthn-register-complete'),
    path('webauthn/auth/begin/', views.webauthn_auth_begin, name='webauthn-auth-begin'),
    path('webauthn/auth/complete/', views.webauthn_auth_complete, name='webauthn-auth-complete')
]