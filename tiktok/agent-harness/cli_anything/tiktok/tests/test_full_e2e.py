"""Full end-to-end integration tests (requires real TikTok credentials).

Set environment variables to run:
    TIKTOK_CLIENT_KEY=...
    TIKTOK_CLIENT_SECRET=...
    TIKTOK_ACCESS_TOKEN=...   # pre-authorized token for sandbox

These tests are skipped automatically if credentials are not set.
"""

import os
import pytest


REQUIRES_CREDENTIALS = pytest.mark.skipif(
    not os.environ.get("TIKTOK_ACCESS_TOKEN"),
    reason="TIKTOK_ACCESS_TOKEN not set — skipping live API tests",
)


@REQUIRES_CREDENTIALS
def test_get_user_info_live():
    from cli_anything.tiktok.core.user import get_user_info
    info = get_user_info()
    assert "display_name" in info
    assert "open_id" in info


@REQUIRES_CREDENTIALS
def test_list_videos_live():
    from cli_anything.tiktok.core.videos import list_videos
    result = list_videos(max_count=5)
    assert "data" in result
