"""Unit tests for trends-scout core modules."""
import json
import pytest
from unittest.mock import patch, MagicMock

from cli_anything.trends_scout.core import account as acc_mod
from cli_anything.trends_scout.core import theme_page as tp_mod
from cli_anything.trends_scout.core import youtube as yt_mod
from cli_anything.trends_scout.core import tiktok as tt_mod
from cli_anything.trends_scout.core import music as music_mod
from cli_anything.trends_scout.utils import config as cfg_mod


# ── Config tests ──────────────────────────────────────────────────────────────

class TestConfig:
    def test_set_and_get_key(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        cfg_mod.set_key("youtube_api_key", "test_key_123")
        assert cfg_mod.get("youtube_api_key") == "test_key_123"

    def test_env_var_takes_precedence(self, monkeypatch):
        monkeypatch.setenv("YOUTUBE_API_KEY", "env_key")
        assert cfg_mod.get("youtube_api_key") == "env_key"

    def test_get_all_masks_secrets(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        cfg_mod.set_key("youtube_api_key", "supersecretkey123")
        cfg_mod.set_key("niche", "fitness")
        masked = cfg_mod.get_all()
        assert "supers..." in masked["youtube_api_key"]
        assert masked["niche"] == "fitness"

    def test_add_and_remove_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        result = cfg_mod.add_account("tiktok", "@testpage", "fitness")
        assert result["added"] is True
        accounts = cfg_mod.get_accounts()
        assert len(accounts) == 1
        assert accounts[0]["handle"] == "@testpage"
        removed = cfg_mod.remove_account("tiktok", "@testpage")
        assert removed["removed"] == 1
        assert cfg_mod.get_accounts() == []

    def test_no_duplicate_accounts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        cfg_mod.add_account("tiktok", "@page", "fitness")
        cfg_mod.add_account("tiktok", "@page", "fitness")
        assert len(cfg_mod.get_accounts()) == 1


# ── Account module tests ──────────────────────────────────────────────────────

class TestAccount:
    def test_audit_account_returns_checklist(self):
        result = acc_mod.audit_account("tiktok", "@testaccount", "fitness")
        assert "optimization_checklist" in result
        assert len(result["optimization_checklist"]) > 0
        assert "quick_wins" in result
        assert len(result["quick_wins"]) == 5

    def test_audit_has_posting_schedule(self):
        result = acc_mod.audit_account("tiktok", "@test", "general")
        schedule = result["posting_schedule"]
        assert "best_days" in schedule
        assert "best_times_utc" in schedule
        assert "frequency" in schedule

    def test_audit_unknown_platform_defaults(self):
        result = acc_mod.audit_account("snapchat", "@test", "general")
        assert "optimization_checklist" in result

    def test_optimize_hashtags_returns_list(self):
        result = acc_mod.optimize_hashtags(niche="fitness", platform="tiktok", count=10)
        assert "hashtags" in result
        assert len(result["hashtags"]) <= 10
        assert "caption_ready" in result

    def test_optimize_hashtags_injects_trend_tags(self):
        trend = ["#trendingnow", "#viraltoday"]
        result = acc_mod.optimize_hashtags(
            niche="fitness", trend_hashtags=trend, count=10,
        )
        tags = result["hashtags"]
        assert any(t in tags for t in trend)

    def test_get_posting_schedule_all_platforms(self):
        for platform in ("tiktok", "youtube", "instagram", "twitter"):
            result = acc_mod.get_posting_schedule(platform)
            assert "schedule" in result
            assert "platform" in result

    def test_optimize_all_no_accounts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        result = acc_mod.optimize_all_accounts()
        assert "error" in result

    def test_optimize_all_with_accounts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        cfg_mod.add_account("tiktok", "@fitnesspage", "fitness")
        cfg_mod.add_account("youtube", "@financechannel", "finance")
        result = acc_mod.optimize_all_accounts()
        assert result["accounts_audited"] == 2
        assert len(result["results"]) == 2

    def test_score_format(self):
        audit = acc_mod.audit_account("tiktok", "@test", "general")
        score = acc_mod._calculate_score(audit)
        assert "/" in score
        assert any(label in score for label in ("STRONG", "NEEDS WORK", "CRITICAL GAPS"))

    def test_niche_hashtags_coverage(self):
        for niche in ("fitness", "food", "fashion", "finance", "beauty", "gaming", "general"):
            result = acc_mod.optimize_hashtags(niche=niche, count=10)
            assert result["hashtags"]


# ── Theme page module tests ───────────────────────────────────────────────────

class TestThemePage:
    def test_get_niches_returns_all(self):
        result = tp_mod.get_niches()
        assert result["total"] >= 6
        for n in result["niches"]:
            assert "name" in n
            assert "conversion_rate" in n
            assert "time_to_monetize" in n

    def test_get_niche_strategy_valid(self):
        result = tp_mod.get_niche_strategy("motivation")
        assert "content_types" in result
        assert "monetization" in result
        assert "90_day_action_plan" in result
        assert len(result["90_day_action_plan"]) == 4

    def test_get_niche_strategy_invalid(self):
        result = tp_mod.get_niche_strategy("nonexistent_niche")
        assert "error" in result
        assert "available" in result

    def test_get_repurpose_guide_all_platforms(self):
        for platform in ("tiktok_video", "youtube_shorts", "instagram_reels", "twitter_thread"):
            result = tp_mod.get_repurpose_guide(platform)
            assert "tip" in result
            assert "tools" in result
            assert "sources" in result

    def test_get_repurpose_guide_invalid(self):
        result = tp_mod.get_repurpose_guide("snapchat")
        assert "error" in result

    def test_get_monetization_roadmap_all_platforms(self):
        for platform in ("tiktok", "youtube", "instagram"):
            result = tp_mod.get_monetization_roadmap(platform)
            assert "monetization_tiers" in result
            assert len(result["monetization_tiers"]) >= 2

    def test_get_monetization_roadmap_invalid(self):
        result = tp_mod.get_monetization_roadmap("myspace")
        assert "error" in result

    def test_growth_roadmap_has_4_phases(self):
        result = tp_mod.get_growth_roadmap()
        assert len(result["phases"]) == 4
        assert "key_metrics" in result
        assert "tools" in result

    def test_niche_strategy_includes_growth_phases(self):
        result = tp_mod.get_niche_strategy("finance_money")
        assert "growth_phases" in result
        phases = result["growth_phases"]
        assert len(phases) == 4


# ── YouTube module tests (mocked HTTP) ───────────────────────────────────────

class TestYouTube:
    def test_extract_hashtags(self):
        from cli_anything.trends_scout.core.youtube import _extract_hashtags
        result = _extract_hashtags("Great video #fitness #gym Check it out #motivation")
        assert "#fitness" in result
        assert "#gym" in result
        assert "#motivation" in result

    def test_parse_views(self):
        from cli_anything.trends_scout.core.youtube import _parse_views
        assert _parse_views("1.5M views") == 1_500_000
        assert _parse_views("500K views") == 500_000
        assert _parse_views("2.1B views") == 2_100_000_000
        assert _parse_views("12,345") == 12_345

    def test_deep_text_simple(self):
        from cli_anything.trends_scout.core.youtube import _deep_text
        assert _deep_text("hello") == "hello"
        assert _deep_text({"simpleText": "world"}) == "world"
        assert _deep_text({"runs": [{"text": "foo"}, {"text": " bar"}]}) == "foo bar"

    def test_get_trending_no_api_key_falls_back(self, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.trends_scout.utils.config.get",
            lambda key, fallback=None: None,
        )
        with patch("cli_anything.trends_scout.core.youtube._scrape_trending") as mock_scrape:
            mock_scrape.return_value = [
                {"id": "abc", "title": "Test Video #trending", "channel": "TestCh",
                 "views": 1000000, "hashtags": ["#trending"], "url": "https://yt.be/abc"},
            ]
            result = yt_mod.get_trending(region="US", limit=5)
            assert result["source"] == "scrape"
            assert result["total"] >= 1
            assert "#trending" in result["top_hashtags"]


# ── TikTok module tests (mocked HTTP) ────────────────────────────────────────

class TestTikTok:
    def test_extract_hashtags(self):
        from cli_anything.trends_scout.core.tiktok import _extract_hashtags
        result = _extract_hashtags("New video #fyp #fitness #viral2024")
        assert "#fyp" in result
        assert "#fitness" in result

    def test_normalize_public_item(self):
        from cli_anything.trends_scout.core.tiktok import _normalize_public
        item = {
            "id": "12345",
            "desc": "Test video #fyp #fitness",
            "author": {"uniqueId": "testuser"},
            "music": {"title": "Trending Song", "authorName": "Artist", "id": "music123"},
            "stats": {"playCount": 500000, "diggCount": 10000, "shareCount": 5000, "commentCount": 200},
        }
        result = _normalize_public(item)
        assert result["id"] == "12345"
        assert result["author"] == "testuser"
        assert result["views"] == 500000
        assert result["music_title"] == "Trending Song"
        assert "#fyp" in result["hashtags"]
        assert "#fitness" in result["hashtags"]

    def test_get_trending_sounds_aggregates(self, monkeypatch):
        mock_videos = [
            {"music_title": "Hot Song", "music_author": "DJ Cool", "music_id": "m1",
             "hashtags": ["#fyp"], "views": 100000},
            {"music_title": "Hot Song", "music_author": "DJ Cool", "music_id": "m1",
             "hashtags": ["#trending"], "views": 200000},
            {"music_title": "Other Track", "music_author": "Singer X", "music_id": "m2",
             "hashtags": ["#music"], "views": 50000},
        ]
        with patch("cli_anything.trends_scout.core.tiktok._public_trending") as mock_pub, \
             patch("cli_anything.trends_scout.core.tiktok._get_research_token", return_value=None):
            mock_pub.return_value = mock_videos
            result = tt_mod.get_trending_sounds(region="US", limit=5)
            sounds = result["trending_sounds"]
            assert len(sounds) >= 1
            # Hot Song should be rank 1 (appears twice)
            assert sounds[0]["title"] == "Hot Song"
            assert sounds[0]["video_count"] == 2


# ── Music module tests ────────────────────────────────────────────────────────

class TestMusic:
    def test_get_viral_music_no_apis(self, monkeypatch):
        with patch("cli_anything.trends_scout.core.tiktok.get_trending_sounds") as mock_tt, \
             patch("cli_anything.trends_scout.core.youtube.get_trending_music") as mock_yt:
            mock_tt.return_value = {
                "trending_sounds": [
                    {"title": "Viral Hit", "artist": "Big Artist", "video_count": 50, "url": ""},
                ]
            }
            mock_yt.return_value = {
                "trending_music": [
                    {"song": "YouTube Hit", "artist": "YT Artist", "views": 1000000, "url": ""},
                ]
            }
            result = music_mod.get_viral_music(limit=10)
            assert result["total"] >= 2
            titles = [t["title"] for t in result["tracks"]]
            assert "Viral Hit" in titles
            assert "YouTube Hit" in titles

    def test_deduplication(self, monkeypatch):
        with patch("cli_anything.trends_scout.core.tiktok.get_trending_sounds") as mock_tt, \
             patch("cli_anything.trends_scout.core.youtube.get_trending_music") as mock_yt:
            mock_tt.return_value = {
                "trending_sounds": [
                    {"title": "Same Song", "artist": "Artist", "video_count": 10, "url": ""},
                    {"title": "Same Song", "artist": "Artist", "video_count": 10, "url": ""},
                ]
            }
            mock_yt.return_value = {"trending_music": []}
            result = music_mod.get_viral_music(limit=10)
            titles = [t["title"] for t in result["tracks"]]
            assert titles.count("Same Song") == 1
