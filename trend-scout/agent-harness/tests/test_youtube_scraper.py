"""Tests for YouTube scraper."""

import pytest
from unittest.mock import patch, MagicMock
from cli_anything.trend_scout.core.youtube_scraper import YouTubeScraper


@pytest.fixture
def scraper():
    return YouTubeScraper(api_key=None)


class TestHashtagExtraction:
    def test_extracts_hashtags_from_text(self, scraper):
        text = "Check out #fitness #gym tips #workout today"
        result = scraper._extract_hashtags_from_text(text)
        assert "#fitness" not in result  # returns without #
        assert "fitness" in result
        assert "gym" in result
        assert "workout" in result

    def test_empty_text_returns_empty(self, scraper):
        assert scraper._extract_hashtags_from_text("") == []
        assert scraper._extract_hashtags_from_text(None) == []

    def test_deduplicates_hashtags(self, scraper):
        text = "#fyp #fyp #viral #fyp"
        result = scraper._extract_hashtags_from_text(text)
        assert result.count("fyp") == 1

    def test_extracts_from_mixed_text(self, scraper):
        text = "Watch this #trending video about #fashion today!"
        result = scraper._extract_hashtags_from_text(text)
        assert "trending" in result
        assert "fashion" in result


class TestHashtagAggregation:
    def test_ranks_by_frequency(self, scraper):
        videos = [
            {"hashtags": ["fyp", "viral"], "tags": []},
            {"hashtags": ["fyp", "fitness"], "tags": []},
            {"hashtags": ["fyp"], "tags": []},
        ]
        result = scraper._extract_hashtags(videos, limit=5)
        assert result[0]["hashtag"] == "#fyp"
        assert result[0]["frequency"] == 3

    def test_returns_empty_for_no_videos(self, scraper):
        result = scraper._extract_hashtags([], limit=5)
        assert result == []

    def test_respects_limit(self, scraper):
        videos = [{"hashtags": [f"tag{i}" for i in range(20)], "tags": []} for _ in range(3)]
        result = scraper._extract_hashtags(videos, limit=5)
        assert len(result) <= 5


class TestTopicClustering:
    def test_extracts_topic_words(self, scraper):
        videos = [
            {"title": "Amazing fitness workout tips for beginners"},
            {"title": "Best fitness routines that work for everyone"},
        ]
        result = scraper._cluster_topics(videos)
        topics = [t["topic"] for t in result]
        assert "fitness" in topics

    def test_returns_at_most_20(self, scraper):
        videos = [{"title": f"word{i} content creator amazing tips"} for i in range(100)]
        result = scraper._cluster_topics(videos)
        assert len(result) <= 20


class TestPostingFrequency:
    def test_daily_frequency(self, scraper):
        entries = [{"upload_date": f"2025050{i}"} for i in range(1, 8)]
        result = scraper._estimate_posting_freq(entries)
        assert result == "daily"

    def test_unknown_with_no_dates(self, scraper):
        result = scraper._estimate_posting_freq([{}])
        assert result == "unknown"

    def test_weekly_frequency(self, scraper):
        # 7-day gaps
        entries = [{"upload_date": "20250501"}, {"upload_date": "20250508"}, {"upload_date": "20250515"}]
        result = scraper._estimate_posting_freq(entries)
        assert result in ("weekly", "every 2-4 days")


class TestCaching:
    def test_caches_results(self, scraper):
        call_count = [0]

        def expensive_fn():
            call_count[0] += 1
            return [{"data": "result"}]

        scraper._cached("test_key", expensive_fn)
        scraper._cached("test_key", expensive_fn)
        assert call_count[0] == 1

    def test_different_keys_not_shared(self, scraper):
        scraper._cached("key1", lambda: [{"a": 1}])
        scraper._cached("key2", lambda: [{"b": 2}])
        assert scraper._cache["key1"]["data"] != scraper._cache["key2"]["data"]


class TestFallbackBehavior:
    def test_returns_error_dict_without_any_method(self, scraper):
        result = scraper._fetch_trending_scrape("US", 10)
        assert len(result) > 0
        assert "error" in result[0]
        assert "fix" in result[0]


class TestTopWords:
    def test_filters_stop_words(self, scraper):
        titles = ["the best fitness tips for you", "a great workout in the gym"]
        result = scraper._top_words(titles, 10)
        assert "the" not in result
        assert "for" not in result
        assert "fitness" in result or "workout" in result

    def test_respects_limit(self, scraper):
        titles = [f"word{i} content" for i in range(50)]
        result = scraper._top_words(titles, 5)
        assert len(result) <= 5
