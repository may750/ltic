from django.apps import AppConfig


class StagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "stages"

    def ready(self):
        # Active les signaux quand Django démarre
        from . import signals  # noqa: F401