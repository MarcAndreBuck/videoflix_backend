from django.db import models


class Video(models.Model):
    """Represent a video available on Videoflix."""

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
