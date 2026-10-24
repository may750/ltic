from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class Stage(models.Model):
    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        EN_COURS = "EN_COURS", "En cours"
        TERMINE = "TERMINE", "Terminé"

    stagiaire = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="stages",
        limit_choices_to={"role": "STAGIAIRE"},
    )
    sujet = models.CharField(max_length=200)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.EN_ATTENTE)

    def __str__(self):
        return f"{self.sujet} ({self.stagiaire})"


class Tache(models.Model):
    class Etat(models.TextChoices):
        A_FAIRE = "A_FAIRE", "À faire"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="taches")
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    echeance = models.DateField(null=True, blank=True)
    etat = models.CharField(max_length=10, choices=Etat.choices, default=Etat.A_FAIRE)

    def __str__(self):
        return self.titre


class Document(models.Model):
    stagiaire = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="documents",
        limit_choices_to={"role": "STAGIAIRE"},
    )
    nom = models.CharField(max_length=200)
    fichier = models.FileField(upload_to="documents/")
    date_depot = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_depot"]

    def __str__(self):
        return self.nom


class Feedback(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="feedbacks")
    encadrant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="feedbacks_donnes",
        limit_choices_to={"role": "ENCADRANT"},
    )
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback sur {self.document}"


class Message(models.Model):
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_envoyes")
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages_recus")
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_envoi"]

    def __str__(self):
        return f"{self.expediteur} → {self.destinataire}"


class Notification(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    contenu = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    lue = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.contenu


class SuggestionProjet(models.Model):
    stagiaire = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="suggestions",
        limit_choices_to={"role": "STAGIAIRE"},
    )
    titre = models.CharField(max_length=200)
    description = models.TextField()
    score = models.FloatField(default=0)
    explication = models.TextField(blank=True, default="")
    competences_cibles = models.CharField(max_length=300, blank=True, default="")
    date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.titre
# Create your models here.
