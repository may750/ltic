
# Create your views here.
from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.permissions import IsEncadrant, IsEncadrantOrAdmin, IsStagiaire

from .models import Document, Feedback, Stage, Tache
from .serializers import (
    DocumentSerializer,
    FeedbackSerializer,
    StageSerializer,
    TacheEtatSerializer,
    TacheSerializer,
)


def stagiaires_visibles(user):
    """Les stagiaires que cette personne a le droit de voir."""
    if user.role == User.Role.ADMIN:
        return User.objects.filter(role=User.Role.STAGIAIRE)
    if user.role == User.Role.ENCADRANT:
        return User.objects.filter(role=User.Role.STAGIAIRE, encadrant=user)
    return User.objects.filter(pk=user.pk)


def verifier_acces(user, stagiaire):
    """Refuse si la personne n'a pas le droit de toucher à ce stagiaire."""
    if not stagiaires_visibles(user).filter(pk=stagiaire.pk).exists():
        raise PermissionDenied("Ce stagiaire n'est pas dans votre groupe.")


class StageViewSet(viewsets.ModelViewSet):
    serializer_class = StageSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsEncadrantOrAdmin()]

    def get_queryset(self):
        return Stage.objects.filter(stagiaire__in=stagiaires_visibles(self.request.user))

    def perform_create(self, serializer):
        verifier_acces(self.request.user, serializer.validated_data["stagiaire"])
        serializer.save()

    def perform_update(self, serializer):
        verifier_acces(self.request.user, serializer.validated_data.get("stagiaire", serializer.instance.stagiaire))
        serializer.save()


class TacheViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsEncadrantOrAdmin()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.user.role == User.Role.STAGIAIRE and self.action in ("update", "partial_update"):
            return TacheEtatSerializer
        return TacheSerializer

    def get_queryset(self):
        return Tache.objects.filter(stage__stagiaire__in=stagiaires_visibles(self.request.user))

    def perform_create(self, serializer):
        verifier_acces(self.request.user, serializer.validated_data["stage"].stagiaire)
        serializer.save()


class DocumentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            return [IsStagiaire()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Document.objects.filter(stagiaire__in=stagiaires_visibles(self.request.user))

    def perform_create(self, serializer):
        serializer.save(stagiaire=self.request.user)


class FeedbackViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FeedbackSerializer

    def get_permissions(self):
        if self.action == "create":
            return [IsEncadrant()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Feedback.objects.filter(document__stagiaire__in=stagiaires_visibles(self.request.user))

    def perform_create(self, serializer):
        verifier_acces(self.request.user, serializer.validated_data["document"].stagiaire)
        serializer.save(encadrant=self.request.user)