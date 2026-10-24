from rest_framework.generics import RetrieveUpdateAPIView

from .permissions import IsStagiaire
from .serializers import ProfilSerializer


class ProfilView(RetrieveUpdateAPIView):
    """Le stagiaire lit et modifie son propre profil."""

    serializer_class = ProfilSerializer
    permission_classes = [IsStagiaire]

    def get_object(self):
        return self.request.user