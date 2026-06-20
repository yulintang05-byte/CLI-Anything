"""Unit tests for social-trends CLI harness core modules."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from cli_anything.social_trends.core import scraper, account_optimizer, theme_pages
from cli_anything.social_trends.utils import config as cfg


# ── scraper tests ─────────────────────────────────────────────────

class TestTikTokCurated:
    def test_returns_dict(self):
        data = scraper._tt_curated_trending(20)
        assert isinstance(data, dict)

    def test_platform_field(self):
        data = scraper._tt_curated_trending(20)
        assert data["platform"] == "tiktok"

    def test_hashtags_list(self):
        data = scraper._tt_curated_trending(10)
        assert isinstance(data["hashtags"], list)
        assert len(data["hashtags"]) == 10

    def test_hashtag_format(self):
        data = scraper._tt_curated_trending(5)
        for h in data["hashtags"]:
            assert h["hashtag"].startswith("#")

    def test_warning_passthrough(self):
        data = scraper._tt_curated_trending(5, warning="test warning")
        assert data["warning"] == "test warning"

    def test_no_warning_by_default(self):
        data = scraper._tt_curated_trending(5)
        assert "warning" not in data

    def test_fetched_at_present(self):
        data = scraper._tt_curated_trending(5)
        assert "fetched_at" in data
        assert data["fetched_at"].endswith("Z")

    def test_max_results_respected(self):
        for n in [1, 5, 15, 20]:
            data = scraper._tt_curated_trending(n)
            assert len(data["hashtags"]) == n

    def test_source_is_curated(self):
        data = scraper._tt_curated_trending(5)
        assert data["source"] == "curated"

    def test_video_count_positive(self):
        data = scraper._tt_curated_trending(20)
        for h in data["hashtags"]:
            assert h["video_count"] > 0


class TestTikTokMusic:
    def test_returns_dict(self):
        data = scraper.fetch_tiktok_music()
        assert isinstance(data, dict)

    def test_tracks_list(self):
        data = scraper.fetch_tiktok_music()
        assert isinstance(data["tracks"], list)

    def test_max_results(self):
        data = scraper.fetch_tiktok_music(max_results=3)
        assert len(data["tracks"]) <= 3

    def test_track_has_required_fields(self):
        data = scraper.fetch_tiktok_music()
        for t in data["tracks"]:
            assert "title" in t
            assert "artist" in t
            assert "trend" in t

    def test_how_to_use_present(self):
        data = scraper.fetch_tiktok_music()
        assert "how_to_use" in data
        assert len(data["how_to_use"]) > 20

    def test_platform_field(self):
        data = scraper.fetch_tiktok_music()
        assert data["platform"] == "tiktok"


class TestTikTokHashtags:
    def test_returns_dict(self):
        data = scraper.fetch_tiktok_hashtags()
        assert isinstance(data, dict)

    def test_recommended_list(self):
        data = scraper.fetch_tiktok_hashtags()
        assert isinstance(data["recommended"], list)

    def test_niche_tags_included(self):
        data = scraper.fetch_tiktok_hashtags(niche="fitness")
        assert any("fitness" in tag.lower() for tag in data["recommended"])

    def test_fyp_always_present(self):
        data = scraper.fetch_tiktok_hashtags()
        assert "#fyp" in data["recommended"]

    def test_strategy_field(self):
        data = scraper.fetch_tiktok_hashtags()
        assert "strategy" in data

    def test_max_results(self):
        data = scraper.fetch_tiktok_hashtags(max_results=5)
        assert len(data["recommended"]) <= 5

    def test_unknown_niche_fallback(self):
        data = scraper.fetch_tiktok_hashtags(niche="unicorn_racing")
        assert isinstance(data["recommended"], list)
        assert len(data["recommended"]) > 0

    def test_multiple_niches(self):
        for niche in ["food", "travel", "gaming", "fashion", "finance", "beauty"]:
            data = scraper.fetch_tiktok_hashtags(niche=niche)
            assert len(data["recommended"]) > 0


class TestYouTubeHashtags:
    def test_returns_dict(self):
        data = scraper.fetch_youtube_hashtags()
        assert isinstance(data, dict)

    def test_recommended_list(self):
        data = scraper.fetch_youtube_hashtags()
        assert isinstance(data["recommended"], list)

    def test_shorts_always_present(self):
        data = scraper.fetch_youtube_hashtags()
        assert "#shorts" in data["recommended"]

    def test_niche_tags(self):
        data = scraper.fetch_youtube_hashtags(niche="fitness")
        assert any("fitness" in tag.lower() for tag in data["recommended"])

    def test_strategy_field(self):
        data = scraper.fetch_youtube_hashtags()
        assert "strategy" in data


# ── account_optimizer tests ───────────────────────────────────────

class TestAccountOptimizer:
    def test_tiktok_report(self):
        data = account_optimizer.get_optimization_report("tiktok")
        assert data["platform"] == "tiktok"

    def test_youtube_report(self):
        data = account_optimizer.get_optimization_report("youtube")
        assert data["platform"] == "youtube"

    def test_instagram_report(self):
        data = account_optimizer.get_optimization_report("instagram")
        assert data["platform"] == "instagram"

    def test_profile_checklist_nonempty(self):
        for p in ["tiktok", "youtube", "instagram"]:
            data = account_optimizer.get_optimization_report(p)
            assert len(data["profile_checklist"]) > 0

    def test_seo_tips_nonempty(self):
        for p in ["tiktok", "youtube", "instagram"]:
            data = account_optimizer.get_optimization_report(p)
            assert len(data["seo_tips"]) > 0

    def test_posting_schedule_has_frequency(self):
        data = account_optimizer.get_optimization_report("tiktok")
        assert "frequency" in data["posting_schedule"]

    def test_score_estimate(self):
        data = account_optimizer.get_optimization_report("tiktok")
        assert "score_estimate" in data

    def test_invalid_platform_raises(self):
        with pytest.raises(ValueError):
            account_optimizer.get_optimization_report("myspace")

    def test_all_report(self):
        data = account_optimizer.get_all_optimization_report()
        assert "platforms" in data
        assert "cross_platform_tips" in data
        assert len(data["cross_platform_tips"]) > 0

    def test_all_report_has_all_platforms(self):
        data = account_optimizer.get_all_optimization_report()
        for p in ["tiktok", "youtube", "instagram"]:
            assert p in data["platforms"]


# ── theme_pages tests ─────────────────────────────────────────────

class TestThemePages:
    def test_niche_guide_all(self):
        data = theme_pages.get_niche_guide()
        assert "niches" in data
        assert len(data["niches"]) >= 5

    def test_specific_niche(self):
        data = theme_pages.get_niche_guide("finance_money")
        assert data["niche"] == "finance_money"
        assert "cpm_estimate" in data

    def test_unknown_niche_error(self):
        data = theme_pages.get_niche_guide("zzz_does_not_exist_zzz")
        assert "error" in data
        assert "available_niches" in data

    def test_niche_has_monetisation(self):
        data = theme_pages.get_niche_guide("pets_animals")
        assert "best_monetisation" in data
        assert len(data["best_monetisation"]) > 0

    def test_conversion_playbook_phases(self):
        data = theme_pages.get_conversion_playbook()
        assert len(data["phases"]) == 3

    def test_conversion_playbook_golden_rule(self):
        data = theme_pages.get_conversion_playbook()
        assert "golden_rule" in data

    def test_monetisation_roadmap_tiers(self):
        data = theme_pages.get_monetisation_roadmap()
        assert len(data["roadmap"]) == 4

    def test_monetisation_roadmap_fastest_path(self):
        data = theme_pages.get_monetisation_roadmap()
        assert "fastest_path_to_revenue" in data

    def test_content_calendar_7_days(self):
        data = theme_pages.get_content_calendar()
        assert len(data["weekly_framework"]) == 7

    def test_content_calendar_repurposing_tip(self):
        data = theme_pages.get_content_calendar()
        assert "repurposing_tip" in data

    def test_all_niches_have_cpm(self):
        data = theme_pages.get_niche_guide()
        for name, info in data["niches"].items():
            assert "cpm_estimate" in info, f"Missing cpm_estimate in {name}"

    def test_all_niches_have_platforms(self):
        data = theme_pages.get_niche_guide()
        for name, info in data["niches"].items():
            assert isinstance(info["platforms"], list)
            assert len(info["platforms"]) > 0


# ── config tests ──────────────────────────────────────────────────

class TestConfig:
    def test_set_and_get(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_DIR", tmp_path
        )
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_FILE",
            tmp_path / "config.json",
        )
        cfg.set_key("test_key", "hello")
        assert cfg.get("test_key") == "hello"

    def test_add_and_list_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_DIR", tmp_path
        )
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_FILE",
            tmp_path / "config.json",
        )
        cfg.add_account("TestPage", "tiktok", "fitness", "@testpage")
        accounts = cfg.get_accounts()
        assert any(a["name"] == "TestPage" for a in accounts)

    def test_remove_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_DIR", tmp_path
        )
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_FILE",
            tmp_path / "config.json",
        )
        cfg.add_account("TestPage2", "youtube", "tech")
        removed = cfg.remove_account("TestPage2", "youtube")
        assert removed
        accounts = cfg.get_accounts()
        assert not any(a["name"] == "TestPage2" for a in accounts)

    def test_remove_nonexistent_returns_false(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_DIR", tmp_path
        )
        monkeypatch.setattr(
            "cli_anything.social_trends.utils.config._CONFIG_FILE",
            tmp_path / "config.json",
        )
        result = cfg.remove_account("ghost", "instagram")
        assert result is False
