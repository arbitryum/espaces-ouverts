from django.conf import settings
from django.db import models


class EhpadProfile(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_SUSPENDED = "suspended"
    STATUS_CHOICES = (
        (STATUS_PENDING, "En attente de validation"),
        (STATUS_APPROVED, "Validé"),
        (STATUS_SUSPENDED, "Suspendu"),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ehpad_profile",
    )
    establishment_name = models.CharField(max_length=200)
    establishment_address = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    participates_in_spaces = models.BooleanField(default=False)
    participates_in_coworking = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.establishment_name

    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED
