from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ContactsView,
    DocumentViewSet,
    FeedbackViewSet,
    MessageViewSet,
    NotificationViewSet,
    StageViewSet,
    TacheViewSet,
)
from .views_ia import SuggestionsView

router = DefaultRouter()
router.register("stages", StageViewSet, basename="stage")
router.register("taches", TacheViewSet, basename="tache")
router.register("documents", DocumentViewSet, basename="document")
router.register("feedbacks", FeedbackViewSet, basename="feedback")
router.register("messages", MessageViewSet, basename="message")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("contacts/", ContactsView.as_view(), name="contacts"),
    path("suggestions/", SuggestionsView.as_view(), name="suggestions"),
] + router.urls