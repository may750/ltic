from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsAdminRole, IsEncadrantOrAdmin
from .serializers import UserSerializer


class MeView(APIView):
    """Renvoie les informations de la personne connectée."""

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class StagiaireListView(ListAPIView):
    """Encadrant : ses stagiaires. Administrateur : tous les stagiaires."""

    serializer_class = UserSerializer
    permission_classes = [IsEncadrantOrAdmin]

    def get_queryset(self):
        stagiaires = User.objects.filter(role=User.Role.STAGIAIRE)
        if self.request.user.role == User.Role.ENCADRANT:
            stagiaires = stagiaires.filter(encadrant=self.request.user)
        return stagiaires


class AllUsersView(ListAPIView):
    """Réservé à l'administrateur : tous les utilisateurs."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
# Create your views here.
