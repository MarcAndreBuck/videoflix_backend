import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from video_app.models import Video
from video_app.tasks import process_video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """Queue processing when a new video is created."""
    if created:
        queue = django_rq.get_queue("default")
        queue.enqueue(process_video, instance.id)
