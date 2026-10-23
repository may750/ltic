from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ContactsView,
    DocumentViewSet,
    FeedbackViewSet,
    MessageViewSet,
    StageViewSet,
    TacheViewSet,
)

router = DefaultRouter()
router.register("stages", StageViewSet, basename="stage")
router.register("taches", TacheViewSet, basename="tache")
router.register("documents", DocumentViewSet, basename="document")
router.register("feedbacks", FeedbackViewSet, basename="feedback")
router.register("messages", MessageViewSet, basename="message")

urlpatterns = [path("contacts/", ContactsView.as_view(), name="contacts")] + router.urls