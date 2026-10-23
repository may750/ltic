from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import AllUsersView, MeView, StagiaireListView

urlpatterns = [
    path("auth/login/", obtain_auth_token, name="login"),
    path("auth/me/", MeView.as_view(), name="me"),
    path("stagiaires/", StagiaireListView.as_view(), name="stagiaires"),
    path("utilisateurs/", AllUsersView.as_view(), name="utilisateurs"),
]