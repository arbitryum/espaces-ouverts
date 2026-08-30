from django.db import models

from spaces.models import CareHome


class CoworkingProject(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("seeking", "Recherche d'un établissement"),
        ("matched", "Projet mis en relation"),
        ("active", "Accueil en cours"),
        ("closed", "Terminé"),
    ]

    name = models.CharField(max_length=200)
    organization_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    care_home = models.ForeignKey(
        CareHome,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="coworking_projects",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
