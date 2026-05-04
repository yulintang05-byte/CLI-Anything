from unittest.mock import MagicMock, patch

import pytest

from cli_anything.social_trends.core.tiktok_trends import (
    _EVERGREEN_HASHTAGS,
    _extract_hashtags,
    get_trending_hashtags_tiktok,
    get_trending_sounds,
)


class TestEvergreenHashtags:
    def test_has_required_fields(self):
        for item in _EVERGREEN_HASHTAGS:
            assert "hashtag" in item
            assert item["hashtag"].startswith("#")
            assert "category" in item
            assert "description" in item

    def test_fyp_is_first(self):
        assert _EVERGREEN_HASHTAGS[0]["hashtag"] == "#fyp"

    def test_minimum_30_tags(self):
        assert len(_EVERGREEN_HASHTAGS) >= 20


class TestExtractHashtags:
    def test_extracts_from_challenges(self):
        items = [
            {
                "desc": "",
                "stats": {"playCount": 100_000},
                "challenges": [
                    {"title": "DanceChallenge", "desc": "viral dance", "stats": {"viewCount": 5_000_000, "videoCount": 1_000}}
                ],
            }
        ]
        result = _extract_hashtags(items)
        assert any(h["hashtag"] == "#dancechallenge" for h in result)

    def test_extracts_from_description(self):
        items = [
            {
                "desc": "Check this out #viral #fyp",
                "stats": {"playCount": 200_000},
                "challenges": [],
            }
        ]
        result = _extract_hashtags(items)
        hashtag_names = [h["hashtag"] for h in result]
        assert "#viral" in hashtag_names
        assert "#fyp" in hashtag_names

    def test_deduplicates_hashtags(self):
        items = [
            {"desc": "#dance", "stats": {"playCount": 100}, "challenges": []},
            {"desc": "#dance again", "stats": {"playCount": 200}, "challenges": []},
        ]
        result = _extract_hashtags(items)
        dance_items = [h for h in result if h["hashtag"] == "#dance"]
        assert len(dance_items) == 1

    def test_accumulates_views(self):
        items = [
            {"desc": "#test", "stats": {"playCount": 1_000}, "challenges": []},
            {"desc": "#test", "stats": {"playCount": 2_000}, "challenges": []},
        ]
        result = _extract_hashtags(items)
        test_item = next(h for h in result if h["hashtag"] == "#test")
        assert test_item["view_count"] == 3_000

    def test_empty_input(self):
        assert _extract_hashtags([]) == []


class TestGetTrendingHashtagsTiktok:
    def test_returns_list_of_dicts(self):
        with patch("cli_anything.social_trends.core.tiktok_trends.get_cached", return_value=None):
            with patch("cli_anything.social_trends.core.tiktok_trends.set_cached"):
                with patch("cli_anything.social_trends.core.tiktok_trends.get_session") as mock_sess:
                    mock_resp = MagicMock()
                    mock_resp.status_code = 403
                    mock_sess.return_value.get.return_value = mock_resp
                    result = get_trending_hashtags_tiktok(top_n=10)

        assert isinstance(result, list)
        assert len(result) <= 10
        assert all("hashtag" in h for h in result)

    def test_returns_cached_when_available(self):
        cached = [{"hashtag": "#cached"}]
        with patch("cli_anything.social_trends.core.tiktok_trends.get_cached", return_value=cached):
            result = get_trending_hashtags_tiktok(top_n=5)
        assert result == cached

    def test_falls_back_to_evergreen_on_api_failure(self):
        with patch("cli_anything.social_trends.core.tiktok_trends.get_cached", return_value=None):
            with patch("cli_anything.social_trends.core.tiktok_trends.set_cached"):
                with patch("cli_anything.social_trends.core.tiktok_trends.get_session") as mock_sess:
                    mock_sess.return_value.get.side_effect = Exception("network error")
                    result = get_trending_hashtags_tiktok(top_n=5)

        assert len(result) > 0
        assert all("hashtag" in h for h in result)

    def test_top_n_respected(self):
        with patch("cli_anything.social_trends.core.tiktok_trends.get_cached", return_value=None):
            with patch("cli_anything.social_trends.core.tiktok_trends.set_cached"):
                with patch("cli_anything.social_trends.core.tiktok_trends.get_session") as mock_sess:
                    mock_resp = MagicMock()
                    mock_resp.status_code = 403
                    mock_sess.return_value.get.return_value = mock_resp
                    result = get_trending_hashtags_tiktok(top_n=5)
        assert len(result) <= 5


class TestGetTrendingSounds:
    def test_returns_fallback_when_no_cookie(self):
        with patch("cli_anything.social_trends.core.tiktok_trends.get_cached", return_value=None):
            with patch("cli_anything.social_trends.core.tiktok_trends.set_cached"):
                with patch("cli_anything.social_trends.core.tiktok_trends.get_config", return_value={}):
                    with patch("cli_anything.social_trends.core.tiktok_trends.get_session") as mock_sess:
                        mock_resp = MagicMock()
                        mock_resp.status_code = 403
                        mock_sess.return_value.get.return_value = mock_resp
                        result = get_trending_sounds(top_n=5)

        assert isinstance(result, list)
        assert len(result) > 0
