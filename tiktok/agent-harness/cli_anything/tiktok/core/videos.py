"""TikTok video management commands."""

from cli_anything.tiktok.utils.tiktok_backend import api_post

DEFAULT_VIDEO_FIELDS = [
    "id", "title", "create_time", "cover_image_url",
    "share_url", "duration", "height", "width",
    "like_count", "comment_count", "share_count", "view_count",
]


def list_videos(fields: list[str] | None = None,
                max_count: int = 20,
                cursor: int = 0) -> dict:
    return api_post("/video/list/", {
        "fields": fields or DEFAULT_VIDEO_FIELDS,
        "max_count": max_count,
        "cursor": cursor,
    })


def get_video(video_id: str, fields: list[str] | None = None) -> dict:
    return api_post("/video/query/", {
        "filters": {"video_ids": [video_id]},
        "fields": fields or DEFAULT_VIDEO_FIELDS,
    })


def delete_video(video_id: str) -> dict:
    return api_post("/video/delete/", {"video_id": video_id})
