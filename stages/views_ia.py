from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsStagiaire

from .ia import IAError, ProfilIncomplet, generer_suggestions
from .models import SuggestionProjet
from .serializers import SuggestionSerializer


class SuggestionsView(APIView):
    """GET : voir mes suggestions. POST : en générer de nouvelles avec l'IA."""

    permission_classes = [IsStagiaire]

    def get(self, request):
        suggestions = SuggestionProjet.objects.filter(stagiaire=request.user).order_by("-score")
        return Response(SuggestionSerializer(suggestions, many=True).data)

    def post(self, request):
        try:
            suggestions = generer_suggestions(request.user)
        except ProfilIncomplet as erreur:
            return Response({"detail": str(erreur)}, status=status.HTTP_400_BAD_REQUEST)
        except IAError as erreur:
            return Response({"detail": str(erreur)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        suggestions.sort(key=lambda s: -s.score)
        return Response(SuggestionSerializer(suggestions, many=True).data, status=status.HTTP_201_CREATED)