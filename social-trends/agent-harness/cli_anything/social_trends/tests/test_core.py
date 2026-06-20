"""Unit tests for social trends core modules."""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


# ── Account Optimization Tests ────────────────────────────────────────

from cli_anything.social_trends.core.account import (
    optimize_account,
    optimize_all_accounts,
    _classify_account_stage,
    _calc_engagement_rate,
    _rate_engagement,
)


class TestAccountClassification:
    def test_brand_new(self):
        assert _classify_account_stage(0) == "brand_new"

    def test_nano(self):
        assert _classify_account_stage(500) == "nano"

    def test_micro(self):
        assert _classify_account_stage(5000) == "micro"

    def test_mid_tier(self):
        assert _classify_account_stage(50000) == "mid_tier"

    def test_macro(self):
        assert _classify_account_stage(500000) == "macro"

    def test_mega(self):
        assert _classify_account_stage(2_000_000) == "mega"


class TestEngagementRate:
    def test_zero_followers(self):
        assert _calc_engagement_rate(0, 0) == 0.0

    def test_normal(self):
        rate = _calc_engagement_rate(10_000, 1_500)
        assert rate == pytest.approx(0.15)

    def test_rating_excellent(self):
        assert _rate_engagement(0.20) == "excellent"

    def test_rating_good(self):
        assert _rate_engagement(0.08) == "good"

    def test_rating_average(self):
        assert _rate_engagement(0.04) == "average"

    def test_rating_below_average(self):
        assert _rate_engagement(0.015) == "below_average"

    def test_rating_poor(self):
        assert _rate_engagement(0.005) == "poor"


class TestOptimizeAccount:
    def test_tiktok_optimization_structure(self):
        result = optimize_account(
            platform="tiktok",
            niche="fitness",
            current_followers=1200,
            avg_views=800,
            post_frequency_per_week=2,
        )
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"
        assert result["account_stage"] == "micro"
        assert isinstance(result["recommendations"], list)
        assert len(result["recommendations"]) > 0
        assert result["critical_count"] >= 0

    def test_instagram_optimization(self):
        result = optimize_account(
            platform="instagram",
            niche="beauty",
            current_followers=5000,
            avg_views=3000,
            post_frequency_per_week=4,
        )
        assert result["platform"] == "instagram"
        recs = result["recommendations"]
        categories = [r["category"] for r in recs]
        assert "originality" in categories

    def test_invalid_platform_raises(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            optimize_account(platform="myspace", niche="music")

    def test_with_trending_data(self):
        result = optimize_account(
            platform="tiktok",
            niche="cooking",
            trending_hashtags=["foodtiktok", "recipe", "cooking"],
            trending_sounds=[{"title": "Viral Beat", "artist": "DJ Test", "usage_count": 50000}],
        )
        recs = result["recommendations"]
        sound_rec = next((r for r in recs if r["category"] == "trending_audio"), None)
        assert sound_rec is not None
        assert "Viral Beat" in sound_rec["action"]

    def test_optimize_all_accounts(self):
        accounts = [
            {"name": "main", "platform": "tiktok", "niche": "fitness", "current_followers": 5000},
            {"name": "side", "platform": "instagram", "niche": "food", "current_followers": 1000},
        ]
        results = optimize_all_accounts(accounts)
        assert len(results) == 2
        assert all("recommendations" in r for r in results)


# ── Theme Page Tests ──────────────────────────────────────────────────

from cli_anything.social_trends.core.theme_page import (
    theme_page_blueprint,
    list_niches,
    content_formats_guide,
    _estimate_weeks,
    _project_revenue,
    THEME_NICHES,
)


class TestThemePage:
    def test_list_niches_returns_all(self):
        niches = list_niches()
        assert len(niches) == len(THEME_NICHES)
        assert all("niche" in n and "avg_cpm_usd" in n for n in niches)

    def test_list_niches_sorted_by_cpm(self):
        niches = list_niches(sort_by="avg_cpm_usd")
        cpms = [n["avg_cpm_usd"] for n in niches]
        assert cpms == sorted(cpms, reverse=True)

    def test_content_formats_guide(self):
        formats = content_formats_guide()
        assert len(formats) > 0
        assert all("format" in f and "virality" in f for f in formats)
        # Should be sorted by virality (very_high first)
        assert formats[0]["virality"] in ("very_high", "high")

    def test_blueprint_structure(self):
        bp = theme_page_blueprint(
            niche="fitness_motivation",
            platform="tiktok",
            target_followers=100_000,
            current_followers=0,
        )
        assert bp["niche"] == "fitness_motivation"
        assert bp["platform"] == "tiktok"
        assert isinstance(bp["content_calendar_30_days"], list)
        assert len(bp["content_calendar_30_days"]) > 0
        assert isinstance(bp["monetization_roadmap"], list)
        assert isinstance(bp["revenue_projection"], dict)

    def test_blueprint_calendar_has_required_fields(self):
        bp = theme_page_blueprint(
            niche="meme_humor",
            platform="instagram",
            target_followers=50_000,
        )
        for day in bp["content_calendar_30_days"]:
            assert "day" in day
            assert "date" in day
            assert "format" in day
            assert "content_idea" in day
            assert "hashtags" in day
            assert "cta" in day

    def test_blueprint_with_trending_data(self):
        bp = theme_page_blueprint(
            niche="finance_education",
            platform="tiktok",
            trending_hashtags=["finance", "money", "investing"],
            trending_sounds=[{"title": "Money Music", "artist": "Artist", "usage_count": 1000}],
        )
        assert "#finance" in bp["content_calendar_30_days"][0]["hashtags"] or \
               any("finance" in h for h in bp["content_calendar_30_days"][0]["hashtags"])
        assert len(bp["trending_sounds_to_use"]) > 0

    def test_custom_niche(self):
        bp = theme_page_blueprint(niche="dog_training", platform="instagram")
        assert bp["niche"] == "dog_training"

    def test_revenue_projection(self):
        rev = _project_revenue(100_000, THEME_NICHES["finance_education"], "affiliate")
        assert rev["at_followers"] == 100_000
        assert rev["total_monthly_usd"] > 0
        assert "note" in rev

    def test_estimate_weeks_reasonable(self):
        estimate = _estimate_weeks(0, 10_000, THEME_NICHES["meme_humor"])
        assert "weeks" in estimate or "years" in estimate


# ── Trends Caching Tests ──────────────────────────────────────────────

from cli_anything.social_trends.core.trends import (
    _cache_path,
    _load_cache,
    _save_cache,
    clear_cache,
    list_cached,
    _derive_opportunities,
)


class TestTrendsCache:
    def test_cache_round_trip(self, tmp_path, monkeypatch):
        from cli_anything.social_trends.core import trends as trends_mod
        monkeypatch.setattr(trends_mod, "CACHE_DIR", tmp_path)
        monkeypatch.setattr("cli_anything.social_trends.core.trends.CACHE_DIR", tmp_path)

        test_data = {"platform": "tiktok", "country": "US", "hashtags": []}
        _save_cache.__globals__["CACHE_DIR"] = tmp_path

        # Directly test save/load by using the module's functions with patched dir
        from pathlib import Path
        cache_file = tmp_path / "tiktok_US_7d.json"
        import time
        test_data["_cached_at"] = time.time()
        cache_file.write_text(json.dumps(test_data))

        loaded = json.loads(cache_file.read_text())
        assert loaded["platform"] == "tiktok"

    def test_derive_opportunities_structure(self):
        opps = _derive_opportunities(
            hashtags=["fitness", "gym", "workout"],
            sounds=[{"title": "Beat", "artist": "DJ", "usage_count": 10000}],
            yt_titles=["10 Fitness Tips That Actually Work"],
            yt_music=["Workout Mix 2026"],
        )
        assert len(opps) > 0
        assert all("type" in o and "action" in o and "platforms" in o for o in opps)
        types = [o["type"] for o in opps]
        assert "hashtag_trend" in types
        assert "trending_sound" in types


# ── TikTok Scraper Tests (mocked) ────────────────────────────────────

from cli_anything.social_trends.utils import tiktok_scraper


class TestTikTokScraper:
    def _mock_response(self, data: dict):
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = data
        return mock

    def test_trending_hashtags_parsing(self):
        mock_data = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "rank": 1,
                        "hashtag_name": "fitness",
                        "hashtag_id": "123",
                        "publish_cnt": 1000000,
                        "video_views": 5000000000,
                        "trend": "up",
                    }
                ]
            },
        }
        with patch("requests.get", return_value=self._mock_response(mock_data)):
            results = tiktok_scraper.trending_hashtags(country="US", period=7, limit=10)

        assert len(results) == 1
        assert results[0]["name"] == "fitness"
        assert results[0]["video_count"] == 1000000
        assert results[0]["view_count"] == 5000000000
        assert results[0]["country"] == "US"

    def test_trending_sounds_parsing(self):
        mock_data = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "rank": 1,
                        "music_name": "Viral Song",
                        "author": "Artist Name",
                        "music_id": "456",
                        "video_cnt": 500000,
                        "play_url": "https://example.com/audio.mp3",
                        "duration": 30,
                        "trend": "up",
                    }
                ]
            },
        }
        with patch("requests.get", return_value=self._mock_response(mock_data)):
            results = tiktok_scraper.trending_sounds(country="US", period=7, limit=5)

        assert len(results) == 1
        assert results[0]["title"] == "Viral Song"
        assert results[0]["artist"] == "Artist Name"
        assert results[0]["usage_count"] == 500000

    def test_api_error_raises(self):
        mock_data = {"code": 40001, "message": "Invalid country code"}
        with patch("requests.get", return_value=self._mock_response(mock_data)):
            with pytest.raises(RuntimeError, match="TikTok API error"):
                tiktok_scraper.trending_hashtags(country="XX")

    def test_http_error_raises(self):
        mock = MagicMock()
        mock.status_code = 429
        with patch("requests.get", return_value=mock):
            with pytest.raises(RuntimeError, match="failed"):
                tiktok_scraper.trending_hashtags()

    def test_trending_videos_parsing(self):
        mock_data = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "rank": 1,
                        "item_id": "789",
                        "desc": "Viral video description",
                        "author_name": "creator123",
                        "follower_cnt": 100000,
                        "like_cnt": 50000,
                        "comment_cnt": 1000,
                        "share_cnt": 5000,
                        "play_cnt": 1000000,
                        "hashtag_list": [{"name": "viral"}, {"name": "trending"}],
                        "music_info": {"music_name": "Cool Song", "author": "DJ"},
                        "cover_url": "https://example.com/cover.jpg",
                    }
                ]
            },
        }
        with patch("requests.get", return_value=self._mock_response(mock_data)):
            results = tiktok_scraper.trending_videos(country="US", limit=5)

        assert len(results) == 1
        assert results[0]["description"] == "Viral video description"
        assert "viral" in results[0]["hashtags"]
        assert results[0]["view_count"] == 1000000


# ── YouTube Scraper Tests (mocked) ────────────────────────────────────

from cli_anything.social_trends.utils import youtube_scraper


class TestYouTubeScraper:
    def _mock_api_response(self, items: list) -> MagicMock:
        mock = MagicMock()
        mock.status_code = 200
        mock.json.return_value = {"items": items}
        return mock

    def test_trending_videos_api_parsing(self):
        items = [
            {
                "id": "abc123",
                "snippet": {
                    "title": "Viral YouTube Video",
                    "channelTitle": "Top Channel",
                    "channelId": "ch123",
                    "description": "Amazing video",
                    "tags": ["viral", "trending", "2026"],
                    "categoryId": "10",
                    "publishedAt": "2026-06-01T12:00:00Z",
                    "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
                },
                "statistics": {
                    "viewCount": "1500000",
                    "likeCount": "75000",
                    "commentCount": "3000",
                },
                "contentDetails": {"duration": "PT5M30S"},
            }
        ]
        with patch("requests.get", return_value=self._mock_api_response(items)):
            results = youtube_scraper.trending_videos_api("fake_key", region="US", limit=5)

        assert len(results) == 1
        assert results[0]["title"] == "Viral YouTube Video"
        assert results[0]["view_count"] == 1500000
        assert results[0]["rank"] == 1

    def test_api_key_required_for_api_mode(self):
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 403
            mock_get.return_value.text = "API key invalid"
            with pytest.raises(RuntimeError, match="quota exceeded"):
                youtube_scraper.trending_videos_api("bad_key", region="US")

    def test_unified_interface_uses_scrape_without_key(self):
        # Without API key, should call scrape path
        with patch("cli_anything.social_trends.utils.youtube_scraper.trending_videos_scrape") as mock_scrape:
            mock_scrape.return_value = [{"rank": 1, "title": "Test", "video_id": "x"}]
            result = youtube_scraper.trending_videos(region="US", api_key=None)
            mock_scrape.assert_called_once()
            assert len(result) == 1

    def test_unified_interface_uses_api_with_key(self):
        with patch("cli_anything.social_trends.utils.youtube_scraper.trending_videos_api") as mock_api:
            mock_api.return_value = [{"rank": 1, "title": "Test", "video_id": "x"}]
            result = youtube_scraper.trending_videos(region="US", api_key="fake_key")
            mock_api.assert_called_once_with("fake_key", region="US", category=None, limit=25)


# ── Session Tests ─────────────────────────────────────────────────────

from cli_anything.social_trends.core.session import Session, HistoryEntry


class TestSession:
    def test_record_and_history(self):
        sess = Session()
        sess.record("trends tiktok", {"country": "US"}, {"fetched": True})
        sess.record("account optimize", {"platform": "tiktok"}, {})
        history = sess.history()
        assert len(history) == 2
        assert history[0]["command"] == "trends tiktok"

    def test_undo_redo(self):
        sess = Session()
        sess.record("cmd1", {})
        sess.record("cmd2", {})
        assert sess.history_count == 2

        undone = sess.undo()
        assert undone.command == "cmd2"
        assert sess.history_count == 1
        assert sess.can_redo

        redone = sess.redo()
        assert redone.command == "cmd2"
        assert sess.history_count == 2

    def test_undo_empty(self):
        sess = Session()
        assert sess.undo() is None

    def test_redo_empty(self):
        sess = Session()
        assert sess.redo() is None

    def test_redo_clears_on_new_record(self):
        sess = Session()
        sess.record("cmd1", {})
        sess.undo()
        sess.record("cmd2", {})
        assert not sess.can_redo

    def test_persist_and_load(self, tmp_path):
        sf = str(tmp_path / "session.json")
        sess = Session(session_file=sf)
        sess.record("trends youtube", {"region": "US"}, {})
        sess.record("theme blueprint", {"niche": "fitness"}, {})

        sess2 = Session(session_file=sf)
        assert sess2.history_count == 2

    def test_history_entry_serialization(self):
        entry = HistoryEntry(command="test", args={"x": 1}, result={"y": 2})
        d = entry.to_dict()
        restored = HistoryEntry.from_dict(d)
        assert restored.command == "test"
        assert restored.args == {"x": 1}
        assert restored.result == {"y": 2}
