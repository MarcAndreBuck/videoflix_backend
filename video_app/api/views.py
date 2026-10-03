from django.http import FileResponse, Http404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from video_app.api.serializers import VideoSerializer
from video_app.functions import (
    get_manifest_path,
    get_segment_path,
    is_valid_segment,
    validate_hls_request,
)
from video_app.models import Video


class VideoListView(generics.ListAPIView):
    """Return all available videos."""

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]


class HLSManifestView(generics.GenericAPIView):
    """Return the HLS manifest for a video resolution."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        if not validate_hls_request(movie_id, resolution):
            raise Http404

        manifest_path = get_manifest_path(movie_id, resolution)

        if not manifest_path.exists():
            raise Http404

        return FileResponse(
            open(manifest_path, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class HLSSegmentView(generics.GenericAPIView):
    """Return a single HLS video segment."""

    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        if not validate_hls_request(movie_id, resolution):
            raise Http404

        if not is_valid_segment(segment):
            raise Http404

        segment_path = get_segment_path(movie_id, resolution, segment)

        if not segment_path.is_file():
            raise Http404

        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/MP2T",
        )
