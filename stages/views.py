from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.permissions import IsEncadrant, IsEncadrantOrAdmin, IsStagiaire
from users.serializers import UserSerializer

from .models import Document, Feedback, Message, Notification, Stage, Tache
from .serializers import (
    DocumentSerializer,
    FeedbackSerializer,
    MessageSerializer,
    NotificationSerializer,
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
    

def contacts_autorises(user):
    """Les personnes à qui cet utilisateur a le droit d'écrire."""
    if user.role == User.Role.ADMIN:
        return User.objects.exclude(pk=user.pk)
    admins = Q(role=User.Role.ADMIN)
    if user.role == User.Role.ENCADRANT:
        return User.objects.filter(admins | Q(role=User.Role.STAGIAIRE, encadrant=user))
    return User.objects.filter(admins | Q(pk=user.encadrant_id))


class ContactsView(APIView):
    """La liste des contacts de la personne connectée."""

    def get(self, request):
        contacts = contacts_autorises(request.user)
        return Response(UserSerializer(contacts, many=True).data)


class MessageViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MessageSerializer

    def get_queryset(self):
        moi = self.request.user
        return Message.objects.filter(Q(expediteur=moi) | Q(destinataire=moi))

    def perform_create(self, serializer):
        destinataire = serializer.validated_data["destinataire"]
        if not contacts_autorises(self.request.user).filter(pk=destinataire.pk).exists():
            raise PermissionDenied("Vous ne pouvez pas écrire à cette personne.")
        serializer.save(expediteur=self.request.user)    


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Chacun voit seulement ses propres notifications."""

    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(utilisateur=self.request.user)

    @action(detail=False, methods=["post"])
    def tout_lire(self, request):
        self.get_queryset().update(lue=True)
        return Response({"ok": True})        