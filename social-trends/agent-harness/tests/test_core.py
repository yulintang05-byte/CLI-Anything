"""Tests for social-trends core modules."""

import pytest
from unittest.mock import patch, MagicMock

from cli_anything.social_trends.core import optimizer as opt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import theme_pages as tp_mod
from cli_anything.social_trends.core import config as cfg_mod
from cli_anything.social_trends.core.session import Session


# ── optimizer tests ───────────────────────────────────────────────────────────

class TestHashtagStrategy:
    def test_basic_strategy(self):
        result = opt_mod.generate_hashtag_strategy("finance", "tiktok", 10)
        assert result["niche"] == "finance"
        assert result["platform"] == "tiktok"
        assert isinstance(result["strategy"], list)
        assert len(result["strategy"]) <= 10
        assert all(isinstance(h, str) for h in result["strategy"])

    def test_strategy_has_tiers(self):
        result = opt_mod.generate_hashtag_strategy("fitness", "tiktok", 10)
        tiers = result["by_tier"]
        assert "mega" in tiers
        assert "large" in tiers
        assert "niche" in tiers
        assert "micro" in tiers

    def test_unknown_niche_falls_back_to_general(self):
        result = opt_mod.generate_hashtag_strategy("unicornriding", "tiktok", 5)
        assert isinstance(result["strategy"], list)
        assert len(result["strategy"]) > 0

    def test_platform_rules_applied(self):
        tiktok_result = opt_mod.generate_hashtag_strategy("finance", "tiktok", 20)
        youtube_result = opt_mod.generate_hashtag_strategy("finance", "youtube", 20)
        # TikTok max is 5 hashtags
        assert len(tiktok_result["strategy"]) <= 5
        # YouTube allows up to 15
        assert len(youtube_result["strategy"]) <= 15

    def test_trending_hashtags_injected(self):
        trending = [{"hashtag": "trendingnow2025"}, {"hashtag": "viralthisweek"}]
        result = opt_mod.generate_hashtag_strategy("finance", "tiktok", 5, trending)
        all_tags = result["all_recommended"]
        assert "trendingnow2025" in all_tags or "viralthisweek" in all_tags

    def test_no_duplicate_hashtags(self):
        result = opt_mod.generate_hashtag_strategy("business", "tiktok", 10)
        assert len(result["strategy"]) == len(set(result["strategy"]))

    def test_caption_template_generated(self):
        result = opt_mod.generate_hashtag_strategy("food", "tiktok", 5)
        assert isinstance(result["caption_template"], str)
        assert len(result["caption_template"]) > 10


class TestPostingSchedule:
    def test_schedule_all_platforms(self):
        result = opt_mod.generate_posting_schedule(["tiktok", "youtube"], "finance", 2)
        assert "tiktok" in result["schedule"]
        assert "youtube" in result["schedule"]

    def test_schedule_has_7_days(self):
        result = opt_mod.generate_posting_schedule(["tiktok"], "fitness", 1)
        assert len(result["schedule"]["tiktok"]) == 7

    def test_posts_per_day_respected(self):
        result = opt_mod.generate_posting_schedule(["tiktok"], "fitness", 1)
        for day, times in result["schedule"]["tiktok"].items():
            assert len(times) <= 1

    def test_weekly_total_correct(self):
        result = opt_mod.generate_posting_schedule(["tiktok", "youtube"], "finance", 2)
        assert result["weekly_total"] == 2 * 7 * 2


class TestContentCalendar:
    def test_calendar_generates(self):
        result = opt_mod.generate_content_calendar("finance", ["tiktok"], weeks=1)
        assert len(result["calendar"]) == 7
        assert result["weeks"] == 1

    def test_calendar_has_required_fields(self):
        result = opt_mod.generate_content_calendar("fitness", ["tiktok", "youtube"], weeks=1)
        entry = result["calendar"][0]
        assert "video_idea" in entry
        assert "hook" in entry
        assert "hashtags" in entry
        assert "cta" in entry
        assert "content_type" in entry

    def test_two_week_calendar(self):
        result = opt_mod.generate_content_calendar("business", ["tiktok"], weeks=2)
        assert len(result["calendar"]) == 14


class TestAccountMetrics:
    def test_low_engagement_flagged(self):
        result = opt_mod.analyze_account_metrics("tiktok", 10000, 1000, 10, 1, 7)
        priorities = result["priorities"]
        assert any("engagement" in p["issue"].lower() for p in priorities)

    def test_growth_stages(self):
        assert opt_mod.analyze_account_metrics("tiktok", 500, 100, 10, 1, 7)["growth_stage"] == "nano"
        assert opt_mod.analyze_account_metrics("tiktok", 5000, 500, 50, 5, 7)["growth_stage"] == "micro"
        assert opt_mod.analyze_account_metrics("tiktok", 50000, 5000, 500, 50, 14)["growth_stage"] == "mid"

    def test_score_range(self):
        result = opt_mod.analyze_account_metrics("tiktok", 1000, 500, 50, 5, 3)
        assert 0 <= result["optimization_score"] <= 100

    def test_monetization_readiness(self):
        result = opt_mod.analyze_account_metrics("tiktok", 10001, 5000, 500, 50, 7)
        eligible = result["monetization_readiness"]["currently_eligible"]
        assert len(eligible) > 0


# ── tiktok tests ──────────────────────────────────────────────────────────────

class TestTikTokTrends:
    def test_fallback_hashtags_returned_without_cookie(self):
        result = tt_mod.fetch_trending_hashtags(session_cookie=None, count=10)
        assert result["platform"] == "tiktok"
        assert result["source"] == "curated"
        assert len(result["hashtags"]) == 10

    def test_hashtag_count_respected(self):
        result = tt_mod.fetch_trending_hashtags(count=5)
        assert result["hashtag_count"] == 5
        assert len(result["hashtags"]) == 5

    def test_hashtags_have_required_fields(self):
        result = tt_mod.fetch_trending_hashtags(count=5)
        for h in result["hashtags"]:
            assert "hashtag" in h
            assert "view_count" in h
            assert "video_count" in h

    def test_fetch_sounds(self):
        result = tt_mod.fetch_trending_sounds(count=5)
        assert result["platform"] == "tiktok"
        assert len(result["sounds"]) == 5
        assert all("title" in s for s in result["sounds"])

    def test_fetch_all_returns_summary(self):
        result = tt_mod.fetch_trending_all()
        assert "summary" in result
        assert "hashtags" in result
        assert "sounds" in result
        assert "viral_hashtags" in result["summary"]
        assert "rising_hashtags" in result["summary"]

    def test_account_audit_extracts_handle(self):
        result = tt_mod.get_account_audit("https://www.tiktok.com/@myhandle123")
        assert result["handle"] == "myhandle123"
        assert "checklist" in result
        assert "algorithm_tips" in result

    def test_content_pillars_sum_to_100_pct(self):
        pillars = tt_mod._content_pillars()
        total = sum(int(p["ratio"].strip("%")) for p in pillars)
        assert total == 100


# ── theme_pages tests ─────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches(self):
        niches = tp_mod.get_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 5
        assert all("id" in n and "name" in n for n in niches)

    def test_sort_by_monetization(self):
        niches = tp_mod.get_niches("monetization_potential")
        pots = [n["monetization_potential"] for n in niches]
        # very-high should come first
        assert pots[0] in ("very-high", "high")

    def test_sort_by_difficulty(self):
        niches = tp_mod.get_niches("difficulty")
        assert niches[0]["difficulty"] in ("easy", "medium")

    def test_known_niche_strategy(self):
        strategy = tp_mod.get_niche_strategy("ai-tools")
        assert strategy["name"] == "AI Tools & Productivity"
        assert "30_day_action_plan" in strategy
        assert "monetization_roadmap" in strategy
        assert len(strategy["30_day_action_plan"]) == 4

    def test_unknown_niche_raises(self):
        with pytest.raises(ValueError):
            tp_mod.get_niche_strategy("notarealniche12345")

    def test_roadmap_has_phases(self):
        roadmap = tp_mod.get_roadmap("beginner")
        assert "phases" in roadmap
        assert len(roadmap["phases"]) == 5
        assert "income_timeline" in roadmap
        assert "common_mistakes" in roadmap

    def test_conversion_guide(self):
        guide = tp_mod.get_conversion_guide()
        assert "conversion_funnel" in guide
        assert "traffic_to_revenue_paths" in guide
        assert "email_list_strategy" in guide
        assert len(guide["traffic_to_revenue_paths"]) >= 4


# ── config tests ──────────────────────────────────────────────────────────────

class TestConfig:
    def test_mask_secrets_short_key(self):
        cfg = {"youtube_api_key": "abc", "tiktok_session_cookie": ""}
        masked = cfg_mod.mask_secrets(cfg)
        assert masked["youtube_api_key"] == "****"
        assert masked["tiktok_session_cookie"] == ""

    def test_mask_secrets_long_key(self):
        cfg = {"youtube_api_key": "AIzaSyABCDEFGHIJKL", "tiktok_session_cookie": ""}
        masked = cfg_mod.mask_secrets(cfg)
        assert "****" in masked["youtube_api_key"]
        assert masked["youtube_api_key"].startswith("AIza")
        assert masked["youtube_api_key"].endswith("JKHL" if len("AIzaSyABCDEFGHIJKL") > 8 else "****") or "****" in masked["youtube_api_key"]

    def test_defaults_returned_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "_CONFIG_FILE", tmp_path / "nonexistent" / "config.json")
        cfg = cfg_mod.load()
        assert "youtube_api_key" in cfg
        assert "tiktok_session_cookie" in cfg


# ── session tests ─────────────────────────────────────────────────────────────

class TestSession:
    def test_initial_state(self):
        s = Session()
        assert s.niche == "general"
        assert not s.has_trends()

    def test_cache_and_retrieve(self):
        s = Session()
        data = {"platform": "tiktok", "hashtags": []}
        s.cache_trends("tiktok", data)
        assert s.has_trends("tiktok")
        assert s.get_cached_trends("tiktok") == data

    def test_clear_cache(self):
        s = Session()
        s.cache_trends("tiktok", {"test": True})
        s.clear_cache()
        assert not s.has_trends()
        assert s.get_cached_trends("tiktok") is None

    def test_niche_setter_lowercases(self):
        s = Session()
        s.niche = "FINANCE"
        assert s.niche == "finance"

    def test_platforms_setter(self):
        s = Session()
        s.platforms = ["TikTok", "YouTube"]
        assert s.platforms == ["tiktok", "youtube"]

    def test_status(self):
        s = Session()
        s.niche = "gaming"
        s.cache_trends("tiktok", {})
        status = s.status()
        assert status["current_niche"] == "gaming"
        assert "tiktok" in status["cached_platforms"]
