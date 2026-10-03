from video_app.functions import create_hls_files, create_thumbnail
from video_app.models import Video


def process_video(video_id):
    """Process a video in the background."""
    video = Video.objects.get(id=video_id)
    create_thumbnail(video)
    create_hls_files(video)
