from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    address_hash = models.CharField(max_length=64, unique=True)
    email = models.CharField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=255, unique=True, null=True)
    identity_steps=models.IntegerField(default=0)
    auth_steps=models.IntegerField(default=0)
    email_code = models.CharField(max_length=6, default=None, null=True)
    email_code_expiry = models.DateTimeField(null=True)
    totp_secret = models.CharField(max_length=255, default=None, null=True)
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    def get_username(self):
        return self.email





class Config(models.Model):
    last_block = models.BigIntegerField()
