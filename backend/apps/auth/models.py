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

class VerifiedIdentity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='identity')
    full_name = models.CharField(max_length=255, null=True, blank=True)
    data_of_birth = models.DateField(null=True, blank=True)
    id_number = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.CharField(max_length=255, null=True, blank=True)
    issuing_country = models.CharField(max_length=255, null=True, blank=True)
    region_country = models.CharField(max_length=255, null=True, blank=True)
    region_state = models.CharField(max_length=255, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    confidence = models.FloatField(default=0.0)
    status = models.CharField(max_length=255, default="pending")
    id_image = models.ImageField(upload_to='kyc/', null=True, blank=True)
    verified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.status}"

class DocumentReview(models.Model):
    class DocType(models.TextChoices):
        RELIGIOUS = "religious", "Religious certificate"
        TAX = "tax", "Tax document"
        OTHER = "other", "Other document"
    class Status(models.TextChoices):
        PENDING = "pending", "Pending review"
        REJECTED = "rejected", "Rejected"
        APPROVED = "approved", "Approved"
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    doc_type = models.CharField(max_length=255, choices=DocType.choices)
    image = models.ImageField(upload_to='doc_reviews/')
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    ai_extracted = models.JSONField(default=dict, blank=True)

    full_name = models.CharField(max_length=255, blank=True)
    issuing_body = models.CharField(max_length=255, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    region = models.CharField(max_length=255, blank=True)
    reference_no = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviewed_docs')
    reviewed_at = models.DateTimeField(null=True)
    class Meta:
        ordering = ['submitted_at']

    def __str__(self):
        return f"{self.user.username} - {self.doc_type} - {self.status}"
