import subprocess
from pathlib import Path

from django.conf import settings

from video_app.models import Video

VIDEO_RESOLUTIONS = {
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
}


def get_video_output_path(video_id):
    """Create and return the HLS output directory."""
    output_path = Path(settings.MEDIA_ROOT) / "videos" / str(video_id)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def get_resolution_output_path(video_id, resolution):
    """Create and return the output directory for a resolution."""
    output_path = get_video_output_path(video_id) / resolution
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def build_hls_command(input_path, output_path, height):
    """Build the FFmpeg command for one HLS resolution."""
    return [
        "ffmpeg",
        "-i", str(input_path),
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-f", "hls",
        str(output_path / "index.m3u8"),
    ]


def run_ffmpeg(command):
    """Run an FFmpeg command."""
    subprocess.run(command, check=True)


def create_hls_version(video, resolution, height):
    """Create one HLS version of a video."""
    output_path = get_resolution_output_path(video.id, resolution)
    command = build_hls_command(video.video_file.path, output_path, height)
    run_ffmpeg(command)


def create_hls_files(video):
    """Create all required HLS versions of a video."""
    for resolution, height in VIDEO_RESOLUTIONS.items():
        create_hls_version(video, resolution, height)


def get_thumbnail_output_path(video_id):
    """Return the output path for a video thumbnail."""
    thumbnail_path = Path(settings.MEDIA_ROOT) / "thumbnails"
    thumbnail_path.mkdir(parents=True, exist_ok=True)
    return thumbnail_path / f"{video_id}.jpg"


def build_thumbnail_command(input_path, output_path):
    """Build the FFmpeg command for a video thumbnail."""
    return [
        "ffmpeg",
        "-i", str(input_path),
        "-ss", "00:00:01",
        "-frames:v", "1",
        str(output_path),
    ]


def create_thumbnail(video):
    """Create a thumbnail for a video."""
    output_path = get_thumbnail_output_path(video.id)
    command = build_thumbnail_command(video.video_file.path, output_path)
    run_ffmpeg(command)
    video.thumbnail.name = f"thumbnails/{video.id}.jpg"
    video.save(update_fields=["thumbnail"])


def get_manifest_path(movie_id, resolution):
    """Return the path to an HLS manifest."""
    return (
        Path(settings.MEDIA_ROOT)
        / "videos"
        / str(movie_id)
        / resolution
        / "index.m3u8"
    )


def get_segment_path(movie_id, resolution, segment):
    """Return the path to an HLS video segment."""
    return (
        Path(settings.MEDIA_ROOT)
        / "videos"
        / str(movie_id)
        / resolution
        / segment
    )


def is_valid_resolution(resolution):
    """Check whether an HLS resolution is supported."""
    return resolution in VIDEO_RESOLUTIONS


def is_valid_segment(segment):
    """Check whether a segment is a valid TS file."""
    return Path(segment).name == segment and segment.endswith(".ts")


def validate_hls_request(movie_id, resolution):
    """Validate the video and requested HLS resolution."""
    if not Video.objects.filter(pk=movie_id).exists():
        return False
    return is_valid_resolution(resolution)
