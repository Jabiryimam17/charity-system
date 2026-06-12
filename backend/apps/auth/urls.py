from django.urls import path
import views.webauthn as webauthn_views
import views.totp as totp_views
import views.identity as identity_views
urlpatterns = [
    path('mfs/setup/', totp_views.totp_setup, name='totp-setup'),
    path('mfs/verify/', totp_views.totp_verify, name='totp-verify'),
    path('mfs/confirm/', totp_views.totp_confirm, name='totp-confirm'),
    path('webauthn/register/begin', webauthn_views.webauthn_register_begin, name='webauthn-register-begin'),
    path('webauthn/register/complete/',webauthn_views.webauthn_register_complete, name='webauthn-register-complete'),
    path('webauthn/auth/begin/', webauthn_views.webauthn_auth_begin, name='webauthn-auth-begin'),
    path('webauthn/auth/complete/', identity_views.verify_id, name='webauthn-auth-complete'),
    path("identity/verify-id/", identity_views.verify_id, name="verify-id")
]