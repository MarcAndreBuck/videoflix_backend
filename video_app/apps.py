from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "video_app"

    def ready(self):
        """Register video app signals."""
        import video_app.signals  # noqa: F401
