from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "email",
            "role", "specialite", "competences", "service", "matricule", "encadrant",
        ]
        read_only_fields = fields


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "role", "specialite", "competences", "centres_interet", "cv"]
        read_only_fields = ["id", "username", "role"]

    def validate_cv(self, fichier):
        if fichier and not fichier.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("Le CV doit être un fichier PDF.")
        if fichier and fichier.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Le CV ne doit pas dépasser 5 Mo.")
        return fichier        