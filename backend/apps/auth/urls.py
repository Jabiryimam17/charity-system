from django.urls import path
import views

urlpatterns = [
    path('mfs/setup/', views.totp_setup, name='totp-setup'),
    path('mfs/verify/', views.totp_verify, name='totp-verify'),
    path('mfs/confirm/', views.totp_confirm, name='totp-confirm'),
]