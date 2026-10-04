from django.contrib import admin

from video_app.models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configure videos in the Django admin."""

    fields = (
        "title",
        "description",
        "category",
        "video_file",
        "thumbnail",
    )
    list_display = ("title", "category", "video_file", "thumbnail")
    search_fields = ("title", "description", "category")
    list_filter = ("category",)

    def get_form(self, request, obj=None, **kwargs):
        """Mark required video fields in the admin form."""
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if field.required:
                field.label = f"{field.label} (required)"
        return form
