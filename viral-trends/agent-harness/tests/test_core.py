"""Unit tests for viral-trends core modules.

All tests use synthetic / offline data — no live network calls.
Run with: pytest tests/test_core.py -v
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_YT_VIDEOS = [
    {
        "id": "abc123", "title": "Viral Dance Trend #fyp #dance",
        "channel": "DanceCentral", "views": 5_000_000, "likes": 200_000,
        "duration": 45, "url": "https://youtu.be/abc123",
        "thumbnail": "https://i.ytimg.com/vi/abc123/hqdefault.jpg",
        "hashtags": ["fyp", "dance"], "description": "Hit dance trend",
        "platform": "youtube", "category": "all",
    },
    {
        "id": "def456", "title": "Money Tips #finance #moneytok",
        "channel": "WealthMind", "views": 2_000_000, "likes": 80_000,
        "duration": 60, "url": "https://youtu.be/def456",
        "thumbnail": "https://i.ytimg.com/vi/def456/hqdefault.jpg",
        "hashtags": ["finance", "moneytok"], "description": "Finance tips",
        "platform": "youtube", "category": "all",
    },
]

SAMPLE_TT_HASHTAGS = [
    {"hashtag": "fyp",      "views": 50_000_000_000, "category": "general"},
    {"hashtag": "finance",  "views": 3_000_000_000,  "category": "finance"},
    {"hashtag": "dance",    "views": 8_000_000_000,  "category": "entertainment"},
    {"hashtag": "moneytok", "views": 3_500_000_000,  "category": "finance"},
]


# ── youtube_scraper tests ─────────────────────────────────────────────────────

class TestYouTubeScraper:
    def setup_method(self):
        from cli_anything.viral_trends.core import youtube_scraper
        self.mod = youtube_scraper

    def test_extract_hashtags_basic(self):
        result = self.mod._extract_hashtags("Hello #world and #python are #trending")
        assert "world" in result
        assert "python" in result
        assert "trending" in result

    def test_extract_hashtags_empty(self):
        assert self.mod._extract_hashtags("") == []

    def test_extract_hashtags_deduplication(self):
        result = self.mod._extract_hashtags("#fyp #fyp #dance")
        assert result.count("fyp") == 1

    def test_parse_view_count_K(self):
        assert self.mod._parse_view_count("1.5K") == 1500

    def test_parse_view_count_M(self):
        assert self.mod._parse_view_count("2.3M") == 2_300_000

    def test_parse_view_count_B(self):
        assert self.mod._parse_view_count("1B") == 1_000_000_000

    def test_parse_view_count_plain(self):
        assert self.mod._parse_view_count("12345") == 12345

    def test_parse_view_count_invalid(self):
        assert self.mod._parse_view_count("N/A") == 0

    def test_get_all_hashtags_offline(self):
        with patch.object(self.mod, "get_trending", return_value=SAMPLE_YT_VIDEOS):
            tags = self.mod.get_all_hashtags()
        assert isinstance(tags, list)
        tag_names = [t["hashtag"] for t in tags]
        assert "fyp" in tag_names or "dance" in tag_names

    def test_get_all_hashtags_structure(self):
        with patch.object(self.mod, "get_trending", return_value=SAMPLE_YT_VIDEOS):
            tags = self.mod.get_all_hashtags()
        assert all("hashtag" in t and "frequency" in t for t in tags)

    def test_cache_miss_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "CACHE_DIR", tmp_path)
        result = self.mod._load_cache("nonexistent_key")
        assert result is None

    def test_cache_write_and_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "CACHE_DIR", tmp_path)
        self.mod._save_cache("test_key", SAMPLE_YT_VIDEOS)
        loaded = self.mod._load_cache("test_key")
        assert loaded is not None
        assert len(loaded) == 2

    def test_cache_ttl_expired(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "CACHE_DIR", tmp_path)
        monkeypatch.setattr(self.mod, "CACHE_TTL", -1)  # force expire
        self.mod._save_cache("expired_key", SAMPLE_YT_VIDEOS)
        result = self.mod._load_cache("expired_key")
        assert result is None

    def test_trending_music_structure(self):
        with patch.object(self.mod, "get_trending", return_value=SAMPLE_YT_VIDEOS):
            music = self.mod.get_trending_music_from_videos()
        assert all("title" in m and "channel" in m for m in music)


# ── tiktok_scraper tests ──────────────────────────────────────────────────────

class TestTikTokScraper:
    def setup_method(self):
        from cli_anything.viral_trends.core import tiktok_scraper
        self.mod = tiktok_scraper

    def test_seed_data_not_empty(self):
        assert len(self.mod._SEED_TRENDS) > 20

    def test_seed_sounds_not_empty(self):
        assert len(self.mod._SEED_SOUNDS) > 10

    def test_get_trending_hashtags_returns_list(self):
        with patch.object(self.mod, "_try_requests_discover", return_value=[]):
            result = self.mod.get_trending_hashtags(use_cache=False)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_trending_hashtags_niche_filter(self):
        with patch.object(self.mod, "_try_requests_discover", return_value=[]):
            result = self.mod.get_trending_hashtags(niche="finance", use_cache=False)
        assert all(
            "finance" in r.get("hashtag","").lower() or
            "finance" in r.get("category","").lower()
            for r in result
        )

    def test_get_trending_sounds_returns_list(self):
        with patch.object(self.mod, "_try_tiktokapi", return_value=None):
            result = self.mod.get_trending_sounds(use_cache=False)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_trending_sounds_structure(self):
        with patch.object(self.mod, "_try_tiktokapi", return_value=None):
            result = self.mod.get_trending_sounds(use_cache=False)
        assert all("sound" in s for s in result)

    def test_cache_write_and_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "CACHE_DIR", tmp_path)
        self.mod._save_cache("tt_test", SAMPLE_TT_HASHTAGS)
        loaded = self.mod._load_cache("tt_test")
        assert loaded is not None
        assert len(loaded) == 4

    def test_limit_respected(self):
        with patch.object(self.mod, "_try_requests_discover", return_value=[]):
            result = self.mod.get_trending_hashtags(limit=5, use_cache=False)
        assert len(result) <= 5

    def test_get_niche_hashtags(self):
        with patch.object(self.mod, "get_trending_hashtags", return_value=SAMPLE_TT_HASHTAGS):
            result = self.mod.get_niche_hashtags("finance")
        assert isinstance(result, list)


# ── hashtag_analyzer tests ────────────────────────────────────────────────────

class TestHashtagAnalyzer:
    def setup_method(self):
        from cli_anything.viral_trends.core import hashtag_analyzer
        self.mod = hashtag_analyzer

    def test_tier_mega(self):
        assert self.mod._tier(50_000_000_000) == "mega"

    def test_tier_high(self):
        assert self.mod._tier(5_000_000_000) == "high"

    def test_tier_medium(self):
        assert self.mod._tier(500_000_000) == "medium"

    def test_tier_low(self):
        assert self.mod._tier(50_000_000) == "low"

    def test_tier_niche(self):
        assert self.mod._tier(5_000_000) == "niche"

    def test_score_hashtag_returns_float(self):
        entry = {"hashtag": "fyp", "views": 50_000_000_000, "frequency": 10}
        score = self.mod.score_hashtag(entry)
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_analyze_hashtags_merges(self):
        yt = [{"hashtag": "fyp", "frequency": 3, "total_views": 1000000}]
        tt = [{"hashtag": "fyp", "views": 50_000_000_000, "category": "general"}]
        result = self.mod.analyze_hashtags(yt, tt)
        assert len(result) == 1
        assert result[0]["hashtag"] == "fyp"
        assert "youtube" in result[0]["platforms"]
        assert "tiktok" in result[0]["platforms"]

    def test_analyze_hashtags_sorted_by_score(self):
        yt = [
            {"hashtag": "fyp", "frequency": 10, "total_views": 50_000_000_000},
            {"hashtag": "niche123", "frequency": 1, "total_views": 1000},
        ]
        tt = [
            {"hashtag": "fyp", "views": 50_000_000_000, "category": "general"},
        ]
        result = self.mod.analyze_hashtags(yt, tt)
        scores = [r["combined_score"] for r in result]
        assert scores == sorted(scores, reverse=True)

    def test_build_optimal_set_structure(self):
        yt_tags = [{"hashtag": t["hashtag"], "frequency": 2, "total_views": t["views"]}
                   for t in SAMPLE_TT_HASHTAGS]
        ranked  = self.mod.analyze_hashtags(yt_tags, SAMPLE_TT_HASHTAGS)
        result  = self.mod.build_optimal_set(ranked, "", 30)
        assert "optimal_set" in result
        assert "caption_block" in result
        assert "by_tier" in result
        assert isinstance(result["optimal_set"], list)

    def test_build_optimal_set_respects_max_tags(self):
        yt_tags = [{"hashtag": f"tag{i}", "frequency": 1, "total_views": 100_000_000}
                   for i in range(100)]
        tt_tags = [{"hashtag": f"tag{i}", "views": 100_000_000, "category": "test"}
                   for i in range(100)]
        ranked  = self.mod.analyze_hashtags(yt_tags, tt_tags)
        result  = self.mod.build_optimal_set(ranked, "", 15)
        assert result["tag_count"] <= 15

    def test_caption_block_has_hashes(self):
        yt_tags = [{"hashtag": "fyp", "frequency": 3, "total_views": 1_000_000}]
        ranked  = self.mod.analyze_hashtags(yt_tags, SAMPLE_TT_HASHTAGS)
        result  = self.mod.build_optimal_set(ranked, "")
        assert result["caption_block"].startswith("#")

    def test_extract_niche_hashtags(self):
        text = "Check out #fitness and #gymtok tips for your #workout"
        result = self.mod.extract_niche_hashtags(text)
        assert "fitness" in result
        assert "gymtok"  in result
        assert "workout" in result

    def test_filter_by_niche(self):
        items = [
            {"hashtag": "moneytok",  "category": "finance"},
            {"hashtag": "gymtok",    "category": "fitness"},
            {"hashtag": "investing", "category": "finance"},
        ]
        result = self.mod.filter_by_niche(items, "finance")
        assert len(result) == 2
        assert all("finance" in r.get("category","") or "finance" in r.get("hashtag","") for r in result)


# ── music_tracker tests ───────────────────────────────────────────────────────

class TestMusicTracker:
    def setup_method(self):
        from cli_anything.viral_trends.core import music_tracker
        self.mod = music_tracker

    def test_usage_guide_structure(self):
        guide = self.mod.get_usage_guide()
        assert "tips" in guide
        assert "platform_notes" in guide
        assert "licensing" in guide
        assert "workflow" in guide

    def test_usage_tips_not_empty(self):
        guide = self.mod.get_usage_guide()
        assert len(guide["tips"]) > 0

    def test_platform_notes_covers_tiktok(self):
        guide = self.mod.get_usage_guide()
        assert "tiktok" in guide["platform_notes"]

    def test_rank_sounds_by_engagement(self):
        sounds = [
            {"sound": "Track A", "plays": 100},
            {"sound": "Track B", "plays": 500},
            {"sound": "Track C", "plays": 200},
        ]
        ranked = self.mod.rank_sounds_by_engagement(sounds)
        assert ranked[0]["sound"] == "Track B"
        assert ranked[-1]["sound"] == "Track A"

    def test_cross_platform_music_structure(self):
        with (
            patch.object(self.mod.tiktok_scraper, "get_trending_sounds",
                         return_value=[{"sound": "As It Was", "category": "pop"}]),
            patch.object(self.mod.youtube_scraper, "get_trending_music_from_videos",
                         return_value=[{"title": "As It Was - Harry Styles", "channel": "Harry Styles",
                                        "views": 1_000_000, "url": "", "hashtags": []}]),
        ):
            result = self.mod.get_cross_platform_music(10)
        assert "tiktok_sounds"  in result
        assert "youtube_music"  in result
        assert "cross_platform" in result
        assert "usage_tips"     in result


# ── account_optimizer tests ───────────────────────────────────────────────────

class TestAccountOptimizer:
    def setup_method(self, monkeypatch=None):
        from cli_anything.viral_trends.core import account_optimizer
        self.mod = account_optimizer

    def test_add_and_get_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        result = self.mod.add_account("testuser", "tiktok", "fitness", 5000)
        assert result["handle"] == "testuser"
        assert result["platform"] == "tiktok"
        fetched = self.mod.get_account("testuser", "tiktok")
        assert fetched is not None

    def test_list_accounts_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        assert self.mod.list_accounts() == []

    def test_update_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        self.mod.add_account("testuser2", "instagram", "food", 10_000)
        updated = self.mod.update_account("testuser2", "instagram", followers=12_000)
        assert updated["followers"] == 12_000

    def test_remove_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        self.mod.add_account("rmme", "tiktok", "gaming", 500)
        assert self.mod.remove_account("rmme", "tiktok") is True
        assert self.mod.get_account("rmme", "tiktok") is None

    def test_remove_nonexistent_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        assert self.mod.remove_account("ghost", "tiktok") is False

    def test_posting_schedule_tiktok(self):
        schedule = self.mod.get_posting_schedule("tiktok")
        assert "best_days" in schedule
        assert "best_hours" in schedule
        assert "frequency" in schedule

    def test_posting_schedule_unknown_platform(self):
        schedule = self.mod.get_posting_schedule("snapchat")
        assert "best_days" in schedule  # falls back to default

    def test_generate_bio_brand(self):
        bio = self.mod.generate_bio("brand", niche="fitness", frequency="daily")
        assert "fitness" in bio

    def test_generate_bio_theme(self):
        bio = self.mod.generate_bio("theme", niche="cooking", audience="food lovers", emoji="🍳")
        assert "cooking" in bio

    def test_generate_caption_returns_string(self):
        caption = self.mod.generate_caption(0, topic="fitness", hook="Watch this", body="Details here", cta="Follow", hashtags="#fyp", n=1)
        assert isinstance(caption, str)

    def test_analyze_account_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        result = self.mod.analyze_account("nobody", "tiktok")
        assert "error" in result

    def test_analyze_account_returns_report(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        self.mod.add_account("creator", "tiktok", "fitness", 25_000, avg_views=5000)
        result = self.mod.analyze_account("creator", "tiktok")
        assert "engagement_rate" in result
        assert "growth_stage" in result
        assert "priority_actions" in result

    def test_next_milestone_below_1k(self):
        m = self.mod._next_milestone(500)
        assert m["target"] == 1_000

    def test_next_milestone_at_1M(self):
        m = self.mod._next_milestone(2_000_000)
        assert m["target"] == "1M+"

    def test_growth_playbook_all_stages(self):
        all_pb = self.mod.get_growth_playbook()
        assert "0_1k" in all_pb
        assert "100k_plus" in all_pb

    def test_growth_playbook_single_stage(self):
        pb = self.mod.get_growth_playbook("1k_10k")
        assert "actions" in pb


# ── theme_page_guide tests ────────────────────────────────────────────────────

class TestThemePageGuide:
    def setup_method(self):
        from cli_anything.viral_trends.core import theme_page_guide
        self.mod = theme_page_guide

    def test_full_guide_not_empty(self):
        guide = self.mod.get_full_guide()
        assert isinstance(guide, dict)
        assert len(guide) > 0

    def test_list_sections(self):
        sections = self.mod.list_sections()
        assert "what_is_a_theme_page" in sections
        assert "niches" in sections
        assert "converting_a_theme_page" in sections

    def test_get_section_valid(self):
        section = self.mod.get_section("niches")
        assert section is not None
        assert "highest_monetization" in section

    def test_get_section_invalid(self):
        assert self.mod.get_section("nonexistent_key") is None

    def test_get_niches_structure(self):
        niches = self.mod.get_niches()
        assert "highest_monetization" in niches
        assert "easiest_to_grow" in niches

    def test_get_conversion_steps_is_list(self):
        steps = self.mod.get_conversion_steps()
        assert isinstance(steps, list)
        assert len(steps) >= 3

    def test_conversion_steps_have_step_and_detail(self):
        steps = self.mod.get_conversion_steps()
        for s in steps:
            assert "step" in s
            assert "detail" in s

    def test_acquisition_guide_structure(self):
        guide = self.mod.get_acquisition_guide()
        assert "where_to_find" in guide
        assert "due_diligence" in guide
        assert "fair_pricing" in guide

    def test_acquisition_due_diligence_not_empty(self):
        guide = self.mod.get_acquisition_guide()
        assert len(guide["due_diligence"]) >= 4

    def test_creating_from_scratch_has_4_phases(self):
        section = self.mod.get_section("creating_from_scratch")
        assert section is not None
        assert len(section["phases"]) == 4


# ── state tests ───────────────────────────────────────────────────────────────

class TestState:
    def setup_method(self):
        from cli_anything.viral_trends.utils import state
        self.mod = state

    def test_record_and_get_history(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        self.mod.record_command("test cmd", "summary here")
        history = self.mod.get_history(10)
        assert len(history) == 1
        assert history[0]["command"] == "test cmd"

    def test_set_and_get_pref(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        self.mod.set_pref("default_niche", "fitness")
        val = self.mod.get_pref("default_niche")
        assert val == "fitness"

    def test_get_pref_default(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        val = self.mod.get_pref("missing_key", "fallback")
        assert val == "fallback"

    def test_clear_history(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        self.mod.record_command("cmd1", "ok")
        self.mod.clear_history()
        assert self.mod.get_history() == []

    def test_history_capped_at_200(self, tmp_path, monkeypatch):
        monkeypatch.setattr(self.mod, "SESSION_FILE", tmp_path / "session.json")
        monkeypatch.setattr(self.mod, "CONFIG_DIR", tmp_path)
        for i in range(250):
            self.mod.record_command(f"cmd{i}", "ok")
        history = self.mod.get_history(999)
        assert len(history) <= 200
