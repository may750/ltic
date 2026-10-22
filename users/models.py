from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STAGIAIRE = "STAGIAIRE", "Stagiaire"
        ENCADRANT = "ENCADRANT", "Encadrant"
        ADMIN = "ADMIN", "Administrateur"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAGIAIRE)

    # Attributs du stagiaire
    specialite = models.CharField(max_length=100, blank=True)
    competences = models.TextField(blank=True)
    cv = models.FileField(upload_to="cv/", blank=True)
    encadrant = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="stagiaires", limit_choices_to={"role": "ENCADRANT"},
    )

    # Attribut de l'encadrant
    service = models.CharField(max_length=100, blank=True)

    # Attribut de l'administrateur
    matricule = models.CharField(max_length=30, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

# Create your models here.
