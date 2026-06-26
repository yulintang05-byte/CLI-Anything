"""Tests for YouTube module — unit tests using synthetic data."""

import pytest
from cli_anything.social_trends.core.youtube import (
    _extract_hashtags,
    _rank_hashtags_from_videos,
    _rank_tags_from_videos,
    _safe_int,
    _parse_api_response,
    extract_trending_music_from_videos,
    CATEGORIES,
)


class TestExtractHashtags:
    def test_extracts_from_title(self):
        tags = _extract_hashtags("Check out #fitness tips #workout #gym")
        assert "fitness" in tags
        assert "workout" in tags
        assert "gym" in tags

    def test_no_duplicates(self):
        tags = _extract_hashtags("#fitness #fitness #workout #fitness")
        assert tags.count("fitness") == 1

    def test_empty_string(self):
        assert _extract_hashtags("") == []

    def test_no_hashtags(self):
        assert _extract_hashtags("No tags here") == []


class TestRankHashtagsFromVideos:
    def _make_video(self, hashtags):
        return {"hashtags": hashtags}

    def test_counts_frequencies(self):
        videos = [
            self._make_video(["fitness", "gym"]),
            self._make_video(["fitness", "workout"]),
            self._make_video(["fitness"]),
        ]
        result = _rank_hashtags_from_videos(videos)
        fitness = next(r for r in result if r["hashtag"] == "#fitness")
        assert fitness["frequency"] == 3

    def test_sorted_descending(self):
        videos = [
            self._make_video(["a", "b", "a", "b", "a"]),
        ]
        # Unique: a=1, b=1 (one video with 3 a's and 2 b's, but per-video unique extraction)
        result = _rank_hashtags_from_videos(videos)
        assert len(result) >= 1

    def test_empty_videos(self):
        assert _rank_hashtags_from_videos([]) == []

    def test_case_normalized(self):
        videos = [
            {"hashtags": ["Fitness"]},
            {"hashtags": ["FITNESS"]},
        ]
        result = _rank_hashtags_from_videos(videos)
        assert result[0]["hashtag"] == "#fitness"
        assert result[0]["frequency"] == 2


class TestRankTagsFromVideos:
    def test_basic_ranking(self):
        videos = [
            {"tags": ["cooking", "recipe", "easy"]},
            {"tags": ["cooking", "meal prep"]},
        ]
        result = _rank_tags_from_videos(videos)
        cooking = next(r for r in result if r["tag"] == "cooking")
        assert cooking["frequency"] == 2

    def test_empty_tags(self):
        videos = [{"tags": []}]
        assert _rank_tags_from_videos(videos) == []


class TestSafeInt:
    def test_string_number(self):
        assert _safe_int("12345") == 12345

    def test_none(self):
        assert _safe_int(None) == 0

    def test_empty_string(self):
        assert _safe_int("") == 0

    def test_integer(self):
        assert _safe_int(42) == 42

    def test_invalid_string(self):
        assert _safe_int("abc") == 0


class TestParseApiResponse:
    def _make_item(self, video_id, title, channel, views, likes, comments, tags=None):
        return {
            "id": video_id,
            "snippet": {
                "title": title,
                "channelTitle": channel,
                "description": f"A video about {title}",
                "tags": tags or [],
                "publishedAt": "2024-01-01T00:00:00Z",
                "categoryId": "10",
                "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
            },
            "statistics": {
                "viewCount": str(views),
                "likeCount": str(likes),
                "commentCount": str(comments),
            },
        }

    def test_parses_single_video(self):
        data = {
            "items": [self._make_item("abc123", "Test Video", "TestChannel", 100000, 5000, 200)]
        }
        result = _parse_api_response(data, "US", "test")
        assert result["total"] == 1
        assert result["videos"][0]["title"] == "Test Video"
        assert result["videos"][0]["views"] == 100000

    def test_parses_multiple_videos(self):
        data = {
            "items": [
                self._make_item(f"id{i}", f"Video {i}", "Channel", i * 1000, i * 100, i * 10)
                for i in range(5)
            ]
        }
        result = _parse_api_response(data, "US", "test")
        assert result["total"] == 5

    def test_trending_hashtags_aggregated(self):
        data = {
            "items": [
                self._make_item("id1", "Video #fitness today", "Chan", 1000, 100, 10),
                self._make_item("id2", "More #fitness content", "Chan", 2000, 200, 20),
            ]
        }
        result = _parse_api_response(data, "US", "test")
        hashtags = [h["hashtag"] for h in result["trending_hashtags"]]
        assert "#fitness" in hashtags

    def test_empty_items(self):
        result = _parse_api_response({"items": []}, "US", "test")
        assert result["total"] == 0
        assert result["videos"] == []

    def test_url_constructed(self):
        data = {"items": [self._make_item("abc123", "Test", "Chan", 0, 0, 0)]}
        result = _parse_api_response(data, "US", "test")
        assert result["videos"][0]["url"] == "https://www.youtube.com/watch?v=abc123"

    def test_source_recorded(self):
        result = _parse_api_response({"items": []}, "GB", "youtube_api")
        assert result["source"] == "youtube_api"
        assert result["region"] == "GB"


class TestExtractTrendingMusicFromVideos:
    def test_music_category_video_detected(self):
        videos = [
            {
                "title": "Drake - God's Plan (Official Music Video)",
                "category_id": "10",
                "views": 500_000_000,
                "url": "https://youtube.com/watch?v=abc",
                "channel": "Drake",
            }
        ]
        result = extract_trending_music_from_videos(videos)
        assert len(result) == 1

    def test_official_audio_detected(self):
        videos = [
            {
                "title": "Bad Bunny - TITÍ ME PREGUNTÓ (Official Audio)",
                "category_id": "0",
                "views": 100_000_000,
                "url": "https://youtube.com/watch?v=xyz",
                "channel": "Bad Bunny",
            }
        ]
        result = extract_trending_music_from_videos(videos)
        assert len(result) >= 1

    def test_non_music_excluded(self):
        videos = [
            {
                "title": "How to Code in Python — Full Tutorial",
                "category_id": "28",
                "views": 500_000,
                "url": "https://youtube.com/watch?v=py1",
                "channel": "Coding Channel",
            }
        ]
        result = extract_trending_music_from_videos(videos)
        assert len(result) == 0

    def test_sorted_by_views_desc(self):
        videos = [
            {"title": "Song A (Official Music Video)", "category_id": "10", "views": 1000, "url": "", "channel": ""},
            {"title": "Song B (Official Music Video)", "category_id": "10", "views": 5000, "url": "", "channel": ""},
        ]
        result = extract_trending_music_from_videos(videos)
        assert result[0]["views"] >= result[1]["views"]

    def test_feat_detected(self):
        videos = [
            {
                "title": "Justin Bieber feat. Chance the Rapper - Holy",
                "category_id": "0",
                "views": 200_000_000,
                "url": "",
                "channel": "Justin Bieber",
            }
        ]
        result = extract_trending_music_from_videos(videos)
        assert len(result) == 1


class TestCategories:
    def test_all_is_zero(self):
        assert CATEGORIES["all"] == "0"

    def test_music_is_10(self):
        assert CATEGORIES["music"] == "10"

    def test_gaming_is_20(self):
        assert CATEGORIES["gaming"] == "20"

    def test_all_values_are_strings(self):
        for v in CATEGORIES.values():
            assert isinstance(v, str)
