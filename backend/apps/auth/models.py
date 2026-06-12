from django.db import models
from apps.users.models import User
class WebAuthnCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='webauthn_credentials')
    credential_id = models.BinaryField(unique=True)
    public_key = models.TextField()
    sign_count = models.IntegerField()
    device_name = models.CharField(max_length=255, default="My Device")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.email} - {self.device_name}"
