import json
from unittest.mock import MagicMock, patch

import pytest

from cli_anything.social_trends.core.youtube_trends import (
    VIDEO_CATEGORIES,
    _get_api_key,
    get_trending_hashtags,
    get_trending_videos,
    search_trending_topics,
)


@pytest.fixture
def mock_api_key(monkeypatch):
    monkeypatch.setenv("YOUTUBE_API_KEY", "test_key_123")


@pytest.fixture
def sample_video_item():
    return {
        "id": "abc123",
        "snippet": {
            "title": "Viral Dance Tutorial #trending #fyp",
            "channelTitle": "DanceChannel",
            "publishedAt": "2025-05-01T10:00:00Z",
            "categoryId": "10",
            "description": "Learn this dance #viral #music",
            "tags": ["dance", "tutorial", "trending"],
            "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
        },
        "statistics": {
            "viewCount": "1000000",
            "likeCount": "50000",
            "commentCount": "5000",
        },
    }


def _mock_yt_response(items):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"items": items, "nextPageToken": None}
    mock_resp.raise_for_status.return_value = None
    return mock_resp


class TestGetApiKey:
    def test_reads_env_var(self, monkeypatch):
        monkeypatch.setenv("YOUTUBE_API_KEY", "env_key")
        with patch("cli_anything.social_trends.core.youtube_trends.get_config", return_value={}):
            assert _get_api_key() == "env_key"

    def test_raises_when_missing(self, monkeypatch):
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        with patch("cli_anything.social_trends.core.youtube_trends.get_config", return_value={}):
            with pytest.raises(ValueError, match="YouTube API key"):
                _get_api_key()

    def test_prefers_config_over_env(self, monkeypatch):
        monkeypatch.setenv("YOUTUBE_API_KEY", "env_key")
        with patch(
            "cli_anything.social_trends.core.youtube_trends.get_config",
            return_value={"youtube_api_key": "config_key"},
        ):
            assert _get_api_key() == "config_key"


class TestGetTrendingVideos:
    def test_returns_mapped_list(self, mock_api_key, sample_video_item):
        with patch("cli_anything.social_trends.core.youtube_trends.get_config", return_value={"youtube_api_key": "k"}):
            with patch("cli_anything.social_trends.core.youtube_trends.get_cached", return_value=None):
                with patch("cli_anything.social_trends.core.youtube_trends.set_cached"):
                    with patch("cli_anything.social_trends.core.youtube_trends.get_session") as mock_sess:
                        mock_sess.return_value.get.return_value = _mock_yt_response([sample_video_item])
                        result = get_trending_videos(region="US", max_results=1)

        assert len(result) == 1
        assert result[0]["id"] == "abc123"
        assert result[0]["title"] == "Viral Dance Tutorial #trending #fyp"
        assert result[0]["view_count"] == 1_000_000
        assert result[0]["category_name"] == "Music"
        assert result[0]["url"] == "https://www.youtube.com/watch?v=abc123"

    def test_returns_cache_when_available(self):
        cached = [{"id": "cached_item"}]
        with patch("cli_anything.social_trends.core.youtube_trends.get_cached", return_value=cached):
            result = get_trending_videos(use_cache=True)
        assert result == cached

    def test_respects_max_results(self, mock_api_key, sample_video_item):
        items = [dict(sample_video_item, id=f"vid{i}") for i in range(10)]
        for item in items:
            item["snippet"] = sample_video_item["snippet"].copy()
            item["statistics"] = sample_video_item["statistics"].copy()

        with patch("cli_anything.social_trends.core.youtube_trends.get_config", return_value={"youtube_api_key": "k"}):
            with patch("cli_anything.social_trends.core.youtube_trends.get_cached", return_value=None):
                with patch("cli_anything.social_trends.core.youtube_trends.set_cached"):
                    with patch("cli_anything.social_trends.core.youtube_trends.get_session") as mock_sess:
                        mock_sess.return_value.get.return_value = _mock_yt_response(items)
                        result = get_trending_videos(max_results=3)
        assert len(result) == 3


class TestGetTrendingHashtags:
    def test_extracts_hashtags_from_title_description(self, mock_api_key, sample_video_item):
        with patch("cli_anything.social_trends.core.youtube_trends.get_trending_videos") as mock_tv:
            mock_tv.return_value = [
                {
                    "id": "x",
                    "title": "Best #fitness tips",
                    "description": "#workout #gym routine",
                    "tags": ["fitness", "gym"],
                    "view_count": 500_000,
                }
            ]
            result = get_trending_hashtags(top_n=10)

        assert any(h["hashtag"] in ("#fitness", "#workout", "#gym") for h in result)
        for item in result:
            assert "hashtag" in item
            assert item["hashtag"].startswith("#")

    def test_sorted_by_views_descending(self, mock_api_key):
        with patch("cli_anything.social_trends.core.youtube_trends.get_trending_videos") as mock_tv:
            mock_tv.return_value = [
                {"id": "a", "title": "#popular", "description": "", "tags": ["popular"], "view_count": 1_000_000},
                {"id": "b", "title": "#niche", "description": "", "tags": ["niche"], "view_count": 1_000},
            ]
            result = get_trending_hashtags(top_n=5)

        if len(result) >= 2:
            assert result[0]["total_views"] >= result[1]["total_views"]


class TestVideoCategories:
    def test_has_key_categories(self):
        assert VIDEO_CATEGORIES["10"] == "Music"
        assert VIDEO_CATEGORIES["20"] == "Gaming"
        assert VIDEO_CATEGORIES["24"] == "Entertainment"
        assert VIDEO_CATEGORIES["28"] == "Science & Technology"

    def test_all_values_are_strings(self):
        for k, v in VIDEO_CATEGORIES.items():
            assert isinstance(k, str)
            assert isinstance(v, str)
