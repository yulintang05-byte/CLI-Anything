"""TikTok video upload — 3-step flow: init → chunk upload → publish."""

import math
import os
import requests

from cli_anything.tiktok.utils.tiktok_backend import api_post, _get_valid_token

CHUNK_SIZE = 10 * 1024 * 1024  # 10 MB


def init_upload(source_type: str = "FILE_UPLOAD",
                video_size: int = 0,
                chunk_size: int = CHUNK_SIZE,
                total_chunk_count: int = 1) -> dict:
    return api_post("/post/video/init/", {
        "post_info": {
            "title": "",
            "privacy_level": "SELF_ONLY",
        },
        "source_info": {
            "source": source_type,
            "video_size": video_size,
            "chunk_size": chunk_size,
            "total_chunk_count": total_chunk_count,
        },
    })


def upload_chunk(upload_url: str, chunk_data: bytes,
                 chunk_index: int, total_chunks: int) -> requests.Response:
    token = _get_valid_token()
    start = chunk_index * CHUNK_SIZE
    end = start + len(chunk_data) - 1
    total_size = total_chunks * CHUNK_SIZE

    resp = requests.put(
        upload_url,
        data=chunk_data,
        headers={
            "Content-Range": f"bytes {start}-{end}/*",
            "Content-Length": str(len(chunk_data)),
            "Content-Type": "video/mp4",
            "Authorization": f"Bearer {token}",
        },
        timeout=300,
    )
    resp.raise_for_status()
    return resp


def publish_video(publish_id: str, title: str = "",
                  privacy_level: str = "SELF_ONLY",
                  disable_duet: bool = False,
                  disable_stitch: bool = False,
                  disable_comment: bool = False) -> dict:
    return api_post("/post/video/publish/", {
        "publish_id": publish_id,
        "post_info": {
            "title": title,
            "privacy_level": privacy_level,
            "disable_duet": disable_duet,
            "disable_stitch": disable_stitch,
            "disable_comment": disable_comment,
        },
    })


def upload_video(file_path: str, title: str = "",
                 privacy_level: str = "SELF_ONLY") -> dict:
    file_size = os.path.getsize(file_path)
    total_chunks = math.ceil(file_size / CHUNK_SIZE)

    init_resp = init_upload(
        source_type="FILE_UPLOAD",
        video_size=file_size,
        chunk_size=CHUNK_SIZE,
        total_chunk_count=total_chunks,
    )

    data = init_resp.get("data", {})
    publish_id = data.get("publish_id", "")
    upload_url = data.get("upload_url", "")

    with open(file_path, "rb") as f:
        for i in range(total_chunks):
            chunk = f.read(CHUNK_SIZE)
            upload_chunk(upload_url, chunk, i, total_chunks)

    return publish_video(publish_id, title=title, privacy_level=privacy_level)
