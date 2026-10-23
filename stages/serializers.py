from rest_framework import serializers

from .models import Document, Feedback, Message, Notification, Stage, Tache


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ["id", "stagiaire", "sujet", "date_debut", "date_fin", "statut"]


class TacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tache
        fields = ["id", "stage", "titre", "description", "echeance", "etat"]


class TacheEtatSerializer(serializers.ModelSerializer):
    """Le stagiaire peut changer seulement l'état de sa tâche."""

    class Meta:
        model = Tache
        fields = ["id", "etat"]


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "stagiaire", "nom", "fichier", "date_depot"]
        read_only_fields = ["stagiaire", "date_depot"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "document", "encadrant", "commentaire", "date"]
        read_only_fields = ["encadrant", "date"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "expediteur", "destinataire", "contenu", "date_envoi"]
        read_only_fields = ["expediteur", "date_envoi"]        


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "contenu", "date", "lue"]
        read_only_fields = ["contenu", "date"]        