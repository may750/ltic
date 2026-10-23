from rest_framework.routers import DefaultRouter

from .views import DocumentViewSet, FeedbackViewSet, StageViewSet, TacheViewSet

router = DefaultRouter()
router.register("stages", StageViewSet, basename="stage")
router.register("taches", TacheViewSet, basename="tache")
router.register("documents", DocumentViewSet, basename="document")
router.register("feedbacks", FeedbackViewSet, basename="feedback")

urlpatterns = router.urls