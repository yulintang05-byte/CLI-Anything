"""Unit tests for CLI-Anything Trend Radar core modules.

All tests use synthetic data — no API keys, no network access required.
Run with: pytest -v
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Ensure package is importable from source ──────────────────────────
sys.path.insert(0, str(Path(__file__).parents[4]))


# ════════════════════════════════════════════════════════════════════
# TrendBackend
# ════════════════════════════════════════════════════════════════════

class TestTrendBackend:
    def test_cache_key_deterministic(self):
        from cli_anything.trend_radar.utils.trend_backend import TrendBackend
        b = TrendBackend()
        k1 = b._cache_key("https://example.com", {"a": 1, "b": 2})
        k2 = b._cache_key("https://example.com", {"b": 2, "a": 1})
        assert k1 == k2, "Cache key should be order-independent"

    def test_cache_key_different_for_different_urls(self):
        from cli_anything.trend_radar.utils.trend_backend import TrendBackend
        b = TrendBackend()
        k1 = b._cache_key("https://example.com/a", {})
        k2 = b._cache_key("https://example.com/b", {})
        assert k1 != k2

    def test_cache_roundtrip(self, tmp_path):
        from cli_anything.trend_radar.utils.trend_backend import TrendBackend, CACHE_DIR
        b = TrendBackend(cache_ttl=300)
        key = "test_roundtrip_key_abc123"
        test_data = {"items": [1, 2, 3], "status": "ok"}
        with patch.object(b, "_cache_path", return_value=tmp_path / f"{key}.json"):
            b._save_cache(key, test_data)
            loaded = b._load_cache(key)
        assert loaded == test_data

    def test_expired_cache_returns_none(self, tmp_path):
        from cli_anything.trend_radar.utils.trend_backend import TrendBackend
        import time
        b = TrendBackend(cache_ttl=1)  # 1-second TTL
        key = "test_expired"
        cache_file = tmp_path / f"{key}.json"
        # Write cache with old timestamp
        cache_file.write_text(json.dumps({"_ts": time.time() - 10, "_data": {"x": 1}}))
        with patch.object(b, "_cache_path", return_value=cache_file):
            result = b._load_cache(key)
        assert result is None

    def test_corrupt_cache_returns_none(self, tmp_path):
        from cli_anything.trend_radar.utils.trend_backend import TrendBackend
        b = TrendBackend()
        key = "test_corrupt"
        cache_file = tmp_path / f"{key}.json"
        cache_file.write_text("not valid json {{{{")
        with patch.object(b, "_cache_path", return_value=cache_file):
            result = b._load_cache(key)
        assert result is None


# ════════════════════════════════════════════════════════════════════
# TikTokTrends
# ════════════════════════════════════════════════════════════════════

class TestTikTokTrends:
    def setup_method(self):
        from cli_anything.trend_radar.core.tiktok_trends import TikTokTrends
        self.tt = TikTokTrends()

    def test_get_trending_hashtags_fallback(self):
        # Should return demo data when API fails
        with patch.object(self.tt._backend, "get", side_effect=Exception("network error")):
            results = self.tt.get_trending_hashtags(region="US", limit=10)
        assert isinstance(results, list)
        assert len(results) == 10
        for r in results:
            assert "hashtag_name" in r
            assert "publish_cnt" in r
            assert "video_views" in r
            assert "trend" in r

    def test_get_trending_sounds_fallback(self):
        with patch.object(self.tt._backend, "get", side_effect=Exception("network error")):
            results = self.tt.get_trending_sounds(limit=5)
        assert isinstance(results, list)
        assert len(results) == 5
        for r in results:
            assert "title" in r
            assert "author" in r
            assert "video_count" in r

    def test_get_trending_videos_fallback(self):
        with patch.object(self.tt._backend, "get", side_effect=Exception("network error")):
            results = self.tt.get_trending_videos(limit=5)
        assert isinstance(results, list)
        assert len(results) == 5
        for r in results:
            assert "title" in r
            assert "play_count" in r
            assert "like_count" in r

    def test_hashtags_live_api_response_parsed(self):
        mock_response = {
            "data": {
                "list": [
                    {"hashtag_name": "fitness", "publish_cnt": 1000000, "video_views": 5000000, "rank_diff": 2, "rank": 1},
                    {"hashtag_name": "workout", "publish_cnt": 800000,  "video_views": 4000000, "rank_diff": -1, "rank": 2},
                ]
            }
        }
        with patch.object(self.tt._backend, "get", return_value=mock_response):
            results = self.tt.get_trending_hashtags(limit=5)
        assert len(results) == 2
        assert results[0]["hashtag_name"] == "fitness"
        assert results[0]["trend"] == "↑"
        assert results[1]["trend"] == "↓"

    def test_limit_respected(self):
        with patch.object(self.tt._backend, "get", side_effect=Exception("fail")):
            results = self.tt.get_trending_hashtags(limit=3)
        assert len(results) == 3

    def test_trend_arrow_positive(self):
        from cli_anything.trend_radar.core.tiktok_trends import _trend_arrow
        assert _trend_arrow(5)  == "↑"
        assert _trend_arrow(-3) == "↓"
        assert _trend_arrow(0)  == "→"


# ════════════════════════════════════════════════════════════════════
# YouTubeTrends
# ════════════════════════════════════════════════════════════════════

class TestYouTubeTrends:
    def setup_method(self):
        from cli_anything.trend_radar.core.youtube_trends import YouTubeTrends
        self.yt = YouTubeTrends()

    def test_require_key_raises_without_key(self):
        from cli_anything.trend_radar.core.youtube_trends import YouTubeTrends
        with pytest.raises(RuntimeError, match="API key"):
            with patch.dict(os.environ, {}, clear=True):
                # Remove any existing key
                env = {k: v for k, v in os.environ.items() if k != "YOUTUBE_API_KEY"}
                with patch.dict(os.environ, env, clear=True):
                    YouTubeTrends._require_key(None)

    def test_require_key_returns_env_key(self):
        from cli_anything.trend_radar.core.youtube_trends import YouTubeTrends
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "AIzaTestKey123"}):
            key = YouTubeTrends._require_key(None)
        assert key == "AIzaTestKey123"

    def test_require_key_prefers_explicit(self):
        from cli_anything.trend_radar.core.youtube_trends import YouTubeTrends
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "env_key"}):
            key = YouTubeTrends._require_key("explicit_key")
        assert key == "explicit_key"

    def test_parse_video(self):
        from cli_anything.trend_radar.core.youtube_trends import YouTubeTrends
        item = {
            "id": "abc123",
            "snippet": {
                "title": "Test Video",
                "channelTitle": "Test Channel",
                "description": "A description",
                "publishedAt": "2025-01-01T00:00:00Z",
                "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
                "tags": ["tag1", "tag2"],
                "categoryId": "10",
            },
            "statistics": {
                "viewCount": "1000000",
                "likeCount": "50000",
                "commentCount": "3000",
            },
        }
        parsed = YouTubeTrends._parse_video(item)
        assert parsed["video_id"] == "abc123"
        assert parsed["title"] == "Test Video"
        assert parsed["channel"] == "Test Channel"
        assert parsed["views"] == 1_000_000
        assert parsed["likes"] == 50_000
        assert parsed["comments"] == 3_000

    def test_days_ago_format(self):
        from cli_anything.trend_radar.core.youtube_trends import _days_ago
        result = _days_ago(7)
        assert result.endswith("Z")
        assert "T" in result
        assert len(result) == 20  # YYYY-MM-DDTHH:MM:SSZ

    def test_get_trending_calls_api(self):
        mock_response = {
            "items": [
                {
                    "id": "vid1",
                    "snippet": {
                        "title": "Trending Video",
                        "channelTitle": "Channel",
                        "description": "",
                        "publishedAt": "2025-01-01T00:00:00Z",
                        "thumbnails": {},
                        "tags": [],
                        "categoryId": "0",
                    },
                    "statistics": {"viewCount": "5000000", "likeCount": "200000", "commentCount": "10000"},
                }
            ]
        }
        with patch.object(self.yt._backend, "get", return_value=mock_response):
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_key"}):
                results = self.yt.get_trending(region="US", category="all", limit=5)
        assert len(results) == 1
        assert results[0]["title"] == "Trending Video"
        assert results[0]["views"] == 5_000_000


# ════════════════════════════════════════════════════════════════════
# HashtagOptimizer
# ════════════════════════════════════════════════════════════════════

class TestHashtagOptimizer:
    def setup_method(self):
        from cli_anything.trend_radar.core.hashtag_optimizer import HashtagOptimizer
        self.ho = HashtagOptimizer()

    def test_generate_set_returns_correct_structure(self):
        result = self.ho.generate_set(niche="fitness", platform="instagram", count=20)
        assert "niche" in result
        assert "platform" in result
        assert "tiers" in result
        assert "all_tags" in result
        assert "copy_ready" in result
        assert "strategy" in result

    def test_generate_set_respects_platform_limit(self):
        result = self.ho.generate_set(niche="fitness", platform="tiktok", count=50)
        # TikTok limit is 10
        assert result["total"] <= 10

    def test_generate_set_instagram_limit(self):
        result = self.ho.generate_set(niche="food", platform="instagram", count=30)
        assert result["total"] <= 30

    def test_generate_set_twitter_limit(self):
        result = self.ho.generate_set(niche="tech", platform="twitter", count=10)
        assert result["total"] <= 3  # Twitter limit is 3

    def test_generate_set_fallback_to_general(self):
        result = self.ho.generate_set(niche="unicorn_niche_xyz", platform="instagram", count=10)
        assert result["total"] > 0

    def test_copy_ready_has_hashtag_prefix(self):
        result = self.ho.generate_set(niche="fashion", platform="instagram", count=5)
        parts = result["copy_ready"].split()
        for p in parts:
            assert p.startswith("#"), f"Expected #{p} to start with #"

    def test_all_tiers_present(self):
        result = self.ho.generate_set(niche="travel", platform="instagram", count=20)
        tiers = result["tiers"]
        assert any("mega" in k for k in tiers)
        assert any("large" in k for k in tiers)
        assert any("medium" in k for k in tiers)

    def test_analyze_hashtags_returns_structure(self):
        tags = ["#fitness", "#gym", "#workout", "#homeworkout", "#calisthenics"]
        result = self.ho.analyze_hashtags(tags)
        assert "total" in result
        assert result["total"] == 5
        assert "tier_counts" in result
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_analyze_hashtags_recommendations_not_empty(self):
        tags = ["#viral", "#fyp", "#trending", "#foryou", "#explore"]  # all mega
        result = self.ho.analyze_hashtags(tags)
        assert len(result["recommendations"]) > 0


# ════════════════════════════════════════════════════════════════════
# ContentCalendar
# ════════════════════════════════════════════════════════════════════

class TestContentCalendar:
    def setup_method(self):
        from cli_anything.trend_radar.core.content_calendar import ContentCalendar
        self.cc = ContentCalendar()

    def test_generate_returns_correct_structure(self):
        cal = self.cc.generate(niche="fitness", platform="instagram", weeks=2, posts_per_week=3)
        assert "niche" in cal
        assert "platform" in cal
        assert "total_posts" in cal
        assert "weeks" in cal
        assert len(cal["weeks"]) == 2

    def test_generate_correct_week_count(self):
        cal = self.cc.generate(niche="food", platform="tiktok", weeks=4, posts_per_week=5)
        assert len(cal["weeks"]) == 4

    def test_each_post_has_required_fields(self):
        cal = self.cc.generate(niche="travel", platform="instagram", weeks=1, posts_per_week=3)
        for week in cal["weeks"]:
            for post in week["posts"]:
                assert "day" in post
                assert "date" in post
                assert "format" in post
                assert "topic" in post
                assert "hashtags" in post
                assert "best_time" in post

    def test_total_posts_matches_actual_posts(self):
        cal = self.cc.generate(niche="finance", platform="instagram", weeks=2, posts_per_week=5)
        actual = sum(len(w["posts"]) for w in cal["weeks"])
        assert cal["total_posts"] == actual

    def test_export_json(self, tmp_path):
        cal = self.cc.generate(niche="fitness", platform="instagram", weeks=1, posts_per_week=3)
        out = str(tmp_path / "calendar.json")
        self.cc.export_json(cal, out)
        assert Path(out).exists()
        with open(out) as f:
            loaded = json.load(f)
        assert loaded["niche"] == "fitness"
        assert "weeks" in loaded

    def test_export_csv(self, tmp_path):
        cal = self.cc.generate(niche="food", platform="instagram", weeks=1, posts_per_week=3)
        out = str(tmp_path / "calendar.csv")
        self.cc.export_csv(cal, out)
        assert Path(out).exists()
        content = Path(out).read_text()
        assert "week" in content
        assert "topic" in content
        assert "hashtags" in content


# ════════════════════════════════════════════════════════════════════
# AccountOptimizer
# ════════════════════════════════════════════════════════════════════

class TestAccountOptimizer:
    def setup_method(self):
        from cli_anything.trend_radar.core.account_optimizer import AccountOptimizer
        self.ao = AccountOptimizer()

    def test_audit_returns_categories(self):
        result = self.ao.audit(platform="instagram", niche="fitness")
        assert isinstance(result, dict)
        assert len(result) > 0
        for key, tips in result.items():
            assert isinstance(tips, list)
            assert len(tips) > 0

    def test_audit_includes_niche_tips_for_known_niches(self):
        result = self.ao.audit(platform="instagram", niche="fitness")
        assert "niche_specific" in result

    def test_audit_no_crash_unknown_niche(self):
        result = self.ao.audit(platform="tiktok", niche="underwater_basket_weaving")
        assert isinstance(result, dict)

    def test_get_best_times_returns_schedule(self):
        result = self.ao.get_best_times(platform="instagram")
        assert "schedule" in result
        assert len(result["schedule"]) == 7  # all 7 days
        assert "frequency" in result

    def test_get_best_times_all_platforms(self):
        result = self.ao.get_best_times(platform="all")
        assert isinstance(result, dict)
        assert "instagram" in result
        assert "tiktok" in result
        assert "youtube" in result

    def test_get_best_times_tiktok(self):
        result = self.ao.get_best_times(platform="tiktok")
        assert "schedule" in result
        for day in result["schedule"]:
            assert "day" in day
            assert "peak1" in day
            assert "score" in day

    def test_audit_all_platforms(self):
        for platform in ["instagram", "tiktok", "youtube"]:
            result = self.ao.audit(platform=platform, niche="travel")
            assert isinstance(result, dict)
            assert len(result) > 0


# ════════════════════════════════════════════════════════════════════
# ThemePageGuide
# ════════════════════════════════════════════════════════════════════

class TestThemePageGuide:
    def setup_method(self):
        from cli_anything.trend_radar.core.theme_page_guide import ThemePageGuide
        self.tg = ThemePageGuide()

    def test_get_guide_overview(self):
        result = self.tg.get_guide("overview")
        assert isinstance(result, dict)
        assert len(result) > 0
        for key, val in result.items():
            assert isinstance(val, list)

    def test_get_guide_all(self):
        result = self.tg.get_guide("all")
        assert isinstance(result, dict)
        assert len(result) > 5

    def test_get_guide_unknown_falls_back(self):
        result = self.tg.get_guide("nonexistent_topic_xyz")
        # Falls back to overview
        assert isinstance(result, dict)

    def test_find_niches_all(self):
        results = self.tg.find_niches(category="all")
        assert isinstance(results, list)
        assert len(results) > 10
        for r in results:
            assert "niche" in r
            assert "competition" in r
            assert "growth_potential" in r
            assert "monetization" in r

    def test_find_niches_sorted_by_growth(self):
        results = self.tg.find_niches(category="all")
        order = {"very high": 0, "high": 1, "medium": 2, "low": 3}
        potentials = [order.get(r.get("growth_potential", "medium"), 2) for r in results]
        assert potentials == sorted(potentials), "Niches should be sorted by growth potential"

    def test_find_niches_by_category(self):
        results = self.tg.find_niches(category="fitness")
        assert isinstance(results, list)
        for r in results:
            assert r["category"] == "fitness"

    def test_get_conversion_tips_known(self):
        result = self.tg.get_conversion_tips(from_type="personal", to_type="theme")
        assert isinstance(result, dict)
        assert len(result) > 0
        for phase, steps in result.items():
            assert isinstance(steps, list)
            assert len(steps) > 0

    def test_get_conversion_tips_unknown_has_fallback(self):
        result = self.tg.get_conversion_tips(from_type="unknown", to_type="unknown")
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_setup_checklist(self):
        result = self.tg.get_setup_checklist(niche="fitness", platform="instagram")
        assert isinstance(result, dict)
        assert len(result) > 0
        for phase, items in result.items():
            assert isinstance(items, list)
            assert len(items) > 0

    def test_setup_checklist_mentions_niche(self):
        result = self.tg.get_setup_checklist(niche="cooking", platform="tiktok")
        all_text = " ".join(
            item for items in result.values() for item in items
        ).lower()
        assert "cooking" in all_text
