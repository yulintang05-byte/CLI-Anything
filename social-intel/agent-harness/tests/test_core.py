"""Unit tests for social-intel core modules (no API calls required)."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_intel.core.optimizer import generate_report, BEST_TIMES, HOOK_FORMULAS
from cli_anything.social_intel.core.theme_pages import (
    score_niche, list_niches, get_monetization_roadmap,
    get_conversion_funnel, get_curation_guide, generate_content_calendar,
    NICHE_DATABASE,
)
from cli_anything.social_intel.core.tiktok import (
    _competition_tiktok, _opportunity_score,
)
from cli_anything.social_intel.core.youtube import (
    _competition_level, _parse_music_title,
)


# ── optimizer.py ─────────────────────────────────────────────────

class TestOptimizer:
    def test_generate_report_tiktok(self):
        r = generate_report("tiktok", "fitness")
        assert r["platform"] == "tiktok"
        assert "best_posting_times_utc" in r
        assert "hashtag_strategy" in r
        assert "hook_formulas" in r
        assert "bio_optimization" in r
        assert "content_mix" in r
        assert "profile_checklist" in r
        assert "growth_levers" in r

    def test_generate_report_youtube(self):
        r = generate_report("youtube")
        assert "youtube" in r["platform"]

    def test_generate_report_instagram_reels(self):
        r = generate_report("instagram_reels")
        assert "instagram" in r["platform"]

    def test_alias_tt(self):
        r = generate_report("tt")
        assert r["platform"] == "tiktok"

    def test_alias_yt_shorts(self):
        r = generate_report("yt_shorts")
        assert "youtube" in r["platform"]

    def test_best_times_all_days(self):
        for platform, schedule in BEST_TIMES.items():
            assert len(schedule) == 7, f"{platform} missing days"

    def test_hook_formulas_structure(self):
        for hook in HOOK_FORMULAS:
            assert "name" in hook
            assert "template" in hook
            assert "example" in hook
            assert "best_for" in hook

    def test_checklist_has_priority(self):
        r = generate_report("tiktok")
        for item in r["profile_checklist"]:
            assert item["priority"] in ("high", "medium", "low")

    def test_growth_levers_have_impact(self):
        r = generate_report("tiktok")
        valid_impacts = {"high", "very_high", "medium", "low"}
        for lever in r["growth_levers"]:
            assert lever["impact"] in valid_impacts


# ── theme_pages.py ───────────────────────────────────────────────

class TestThemePages:
    def test_list_niches_sorted(self):
        result = list_niches()
        niches = result["niches"]
        assert len(niches) == len(NICHE_DATABASE)
        scores = [float(n["monetization_score"].split("/")[0]) for n in niches]
        assert scores == sorted(scores, reverse=True)

    def test_score_niche_fitness(self):
        r = score_niche("fitness")
        assert r["niche"] == "fitness"
        assert "scores" in r
        assert "affiliate_programs" in r
        assert "recommendation" in r
        assert "sub_niches" in r

    def test_score_niche_unknown(self):
        r = score_niche("unicorn_tears")
        assert "error" in r
        assert "available_niches" in r

    def test_score_niche_case_insensitive(self):
        r = score_niche("FITNESS")
        assert r["niche"] == "fitness"

    def test_monetization_roadmap_tiers(self):
        tier_map = [
            (500, "0–1K"),
            (2500, "1K–5K"),
            (10000, "5K–25K"),
            (50000, "25K–100K"),
            (500000, "100K+"),
        ]
        for followers, expected_tier in tier_map:
            r = get_monetization_roadmap(followers)
            assert r["tier"] == expected_tier, f"{followers} followers should be {expected_tier}"

    def test_monetization_roadmap_has_next_tier(self):
        r = get_monetization_roadmap(500)
        assert "next_tier_preview" in r

    def test_monetization_roadmap_top_tier_no_next(self):
        r = get_monetization_roadmap(999_999)
        assert "next_tier_preview" not in r

    def test_conversion_funnel_stages(self):
        r = get_conversion_funnel()
        funnel = r["funnel"]
        for stage in ["awareness", "interest", "desire", "action", "retention"]:
            assert stage in funnel
            assert "tactics" in funnel[stage]

    def test_curation_guide_structure(self):
        r = get_curation_guide()
        assert "legal_guidelines" in r
        assert "content_sources" in r
        assert "tools" in r
        assert len(r["legal_guidelines"]) > 0

    def test_content_calendar_7_days(self):
        r = generate_content_calendar("fitness", "tiktok", posts_per_week=7)
        assert len(r["week_calendar"]) == 7
        assert "Monday" in r["week_calendar"]
        assert "Sunday" in r["week_calendar"]

    def test_content_calendar_posts_per_day(self):
        r = generate_content_calendar("cars", "instagram", posts_per_week=14)
        for day, posts in r["week_calendar"].items():
            assert len(posts) == 2

    def test_content_calendar_has_cta(self):
        r = generate_content_calendar("pets", "tiktok", posts_per_week=7)
        for day, posts in r["week_calendar"].items():
            for post in posts:
                assert "cta" in post
                assert post["cta"]


# ── tiktok.py (pure logic) ───────────────────────────────────────

class TestTikTokLogic:
    def test_competition_levels(self):
        assert _competition_tiktok(10_000_000) == "very_high"
        assert _competition_tiktok(2_000_000) == "high"
        assert _competition_tiktok(500_000) == "medium"
        assert _competition_tiktok(50_000) == "low"

    def test_opportunity_score(self):
        # vpv = views / videos; thresholds: >50K excellent, >10K good, >1K fair, else poor
        assert _opportunity_score(6_000_000, 100) == "excellent"   # 60K vpv
        assert _opportunity_score(600_000, 50) == "good"           # 12K vpv
        assert _opportunity_score(60_000, 50) == "fair"            # 1.2K vpv
        assert _opportunity_score(500, 50) == "poor"               # 10 vpv
        assert _opportunity_score(0, 0) == "unknown"


# ── youtube.py (pure logic) ──────────────────────────────────────

class TestYouTubeLogic:
    def test_competition_level(self):
        assert _competition_level(2_000_000) == "very_high"
        assert _competition_level(500_000) == "high"
        assert _competition_level(50_000) == "medium"
        assert _competition_level(5_000) == "low"

    def test_parse_music_title_dash(self):
        artist, song = _parse_music_title("Drake - God's Plan")
        assert artist == "Drake"
        assert song == "God's Plan"

    def test_parse_music_title_em_dash(self):
        artist, song = _parse_music_title("Taylor Swift — Anti-Hero")
        assert artist == "Taylor Swift"
        assert song == "Anti-Hero"

    def test_parse_music_title_no_separator(self):
        artist, song = _parse_music_title("Viral Dance Video 2024")
        assert artist == ""
        assert song == "Viral Dance Video 2024"
