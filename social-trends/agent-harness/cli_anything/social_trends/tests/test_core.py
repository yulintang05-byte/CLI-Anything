"""Unit tests for social-trends core modules — no external API calls."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from cli_anything.social_trends.core import optimizer as opt_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.core import config as cfg_mod


# ── optimizer tests ───────────────────────────────────────────────

class TestScoreTrend:
    def test_zero_engagement_returns_zero(self):
        score = opt_mod.score_trend({})
        assert score == 0.0

    def test_high_views_increases_score(self):
        low  = opt_mod.score_trend({"view_count": 1_000})
        high = opt_mod.score_trend({"view_count": 100_000_000})
        assert high > low

    def test_rising_trend_bonus(self):
        base    = opt_mod.score_trend({"view_count": 1_000_000, "trend": ""})
        rising  = opt_mod.score_trend({"view_count": 1_000_000, "trend": "rising"})
        assert rising > base

    def test_score_caps_at_100(self):
        score = opt_mod.score_trend({
            "view_count": 10_000_000_000,
            "like_count": 10_000_000,
            "share_count": 5_000_000,
            "comment_count": 1_000_000,
            "clip_count": 2_000_000,
        })
        assert score <= 100.0


class TestRankTrends:
    def test_sorted_descending(self):
        trends = [
            {"view_count": 100},
            {"view_count": 1_000_000},
            {"view_count": 500_000},
        ]
        ranked = opt_mod.rank_trends(trends)
        scores = [t["virality_score"] for t in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_adds_virality_score_field(self):
        trends = [{"view_count": 1000}]
        ranked = opt_mod.rank_trends(trends)
        assert "virality_score" in ranked[0]


class TestBuildHashtagSet:
    def test_fitness_niche_includes_seeds(self):
        result = opt_mod.build_hashtag_set("fitness", [], "tiktok", include_niche_seeds=True)
        tags = result["hashtags"]
        assert any("fitness" in t.lower() or "workout" in t.lower() for t in tags)

    def test_count_within_platform_limits(self):
        result = opt_mod.build_hashtag_set("food", [], "tiktok")
        limits = opt_mod.HASHTAG_LIMITS["tiktok"]
        assert limits["min"] <= result["count"] <= limits["max"]

    def test_trending_hashtags_included(self):
        trending = [{"hashtag": "#viral2024"}, {"hashtag": "#trending"}]
        result = opt_mod.build_hashtag_set("general", trending, "tiktok")
        # trending tags should be in the result
        assert any(t in result["hashtags"] for t in ["#viral2024", "#trending"])

    def test_no_duplicates(self):
        trending = [{"hashtag": "#fitness"}, {"hashtag": "#workout"}]
        result = opt_mod.build_hashtag_set("fitness", trending, "tiktok")
        assert len(result["hashtags"]) == len(set(result["hashtags"]))

    def test_instagram_allows_more_hashtags(self):
        result = opt_mod.build_hashtag_set("beauty", [], "instagram")
        limits = opt_mod.HASHTAG_LIMITS["instagram"]
        assert result["count"] <= limits["max"]


class TestGeneratePostingSchedule:
    def test_returns_list_of_dicts(self):
        schedule = opt_mod.generate_posting_schedule("tiktok")
        assert isinstance(schedule, list)
        assert all(isinstance(s, dict) for s in schedule)

    def test_schedule_has_required_fields(self):
        schedule = opt_mod.generate_posting_schedule("tiktok")
        required = {"date", "day", "time_window", "platform", "post_number"}
        for slot in schedule:
            assert required.issubset(slot.keys())

    def test_respects_posts_per_week(self):
        schedule = opt_mod.generate_posting_schedule("youtube", posts_per_week=3)
        assert len(schedule) <= 3

    def test_platform_in_schedule(self):
        for platform in ("tiktok", "instagram", "youtube"):
            schedule = opt_mod.generate_posting_schedule(platform)
            assert all(s["platform"] == platform for s in schedule)


class TestGenerateAccountReport:
    def test_report_structure(self):
        account = {"platform": "tiktok", "handle": "mypage", "niche": "fitness", "goals": ["grow"]}
        report = opt_mod.generate_account_report(account, [], [])
        assert "account" in report
        assert "profile_checklist" in report
        assert "posting_schedule" in report
        assert "content_pillars" in report
        assert "growth_tips" in report

    def test_checklist_not_empty(self):
        account = {"platform": "tiktok", "handle": "test", "niche": "fitness", "goals": []}
        report = opt_mod.generate_account_report(account, [], [])
        assert len(report["profile_checklist"]) > 0

    def test_content_pillars_count(self):
        account = {"platform": "instagram", "handle": "test", "niche": "travel", "goals": []}
        report = opt_mod.generate_account_report(account)
        assert len(report["content_pillars"]) == 4

    def test_unknown_niche_uses_default_pillars(self):
        account = {"platform": "tiktok", "handle": "test", "niche": "quantum_physics", "goals": []}
        report = opt_mod.generate_account_report(account)
        assert len(report["content_pillars"]) > 0


# ── theme_pages tests ─────────────────────────────────────────────

class TestThemePages:
    def test_list_niches_returns_list(self):
        niches = theme_mod.list_niches()
        assert isinstance(niches, list)
        assert len(niches) > 0

    def test_niches_have_required_fields(self):
        for n in theme_mod.list_niches():
            assert "niche" in n
            assert "monetization" in n
            assert "difficulty" in n

    def test_sort_by_difficulty(self):
        niches = theme_mod.list_niches(sort_by="difficulty")
        difficulties = [n["difficulty"] for n in niches]
        assert difficulties == sorted(difficulties)

    def test_get_niche_detail_exact_match(self):
        detail = theme_mod.get_niche_detail("Fitness / Body Transformation")
        assert detail is not None
        assert detail["niche"] == "Fitness / Body Transformation"

    def test_get_niche_detail_fuzzy_match(self):
        detail = theme_mod.get_niche_detail("fitness")
        assert detail is not None

    def test_get_niche_detail_not_found(self):
        detail = theme_mod.get_niche_detail("QuantumBubbleWrapping")
        assert detail is None

    def test_playbook_has_7_steps(self):
        playbook = theme_mod.get_playbook()
        assert len(playbook) == 7

    def test_playbook_step_filter(self):
        step = theme_mod.get_playbook(step=3)
        assert len(step) == 1
        assert step[0]["step"] == 3

    def test_conversion_tips_categories(self):
        tips = theme_mod.get_conversion_tips()
        expected = {"bio_cta", "caption_hooks", "engagement_boosters", "link_in_bio_stack"}
        assert expected.issubset(tips.keys())

    def test_conversion_tips_category_filter(self):
        tips = theme_mod.get_conversion_tips("bio_cta")
        assert "bio_cta" in tips
        assert len(tips) == 1


# ── config tests ──────────────────────────────────────────────────

class TestConfig:
    def test_load_config_returns_dict(self):
        cfg = cfg_mod.load_config()
        assert isinstance(cfg, dict)

    def test_load_accounts_returns_list(self):
        accounts = cfg_mod.load_accounts()
        assert isinstance(accounts, list)

    def test_add_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        entry = cfg_mod.add_account("tiktok", "@testpage", "fitness", ["grow"])
        assert entry["platform"] == "tiktok"
        assert entry["handle"] == "testpage"
        assert entry["niche"] == "fitness"

    def test_add_account_deduplicates(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        cfg_mod.add_account("tiktok", "@testpage", "fitness", [])
        cfg_mod.add_account("tiktok", "@testpage", "beauty", [])
        accounts = cfg_mod.load_accounts()
        tiktok_test = [a for a in accounts if a["handle"] == "testpage"]
        assert len(tiktok_test) == 1
        assert tiktok_test[0]["niche"] == "beauty"

    def test_remove_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        cfg_mod.add_account("tiktok", "@testpage", "fitness", [])
        removed = cfg_mod.remove_account("tiktok", "@testpage")
        assert removed is True
        assert cfg_mod.load_accounts() == []

    def test_remove_nonexistent_returns_false(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cfg_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        monkeypatch.setattr(cfg_mod, "CONFIG_DIR", tmp_path)
        assert cfg_mod.remove_account("tiktok", "@nobody") is False


# ── youtube helper tests (no API calls) ──────────────────────────

class TestYoutubeHelpers:
    def test_extract_trending_hashtags_from_titles(self):
        from cli_anything.social_trends.core import youtube as yt_mod
        videos = [
            {"title": "Best #fitness tips", "description": "#workout #gym", "tags": ["fitness"]},
            {"title": "#workout routine", "description": "#gym motivation", "tags": []},
        ]
        hashtags = yt_mod.extract_trending_hashtags_from_titles(videos)
        assert isinstance(hashtags, list)
        tag_names = [h["hashtag"] for h in hashtags]
        assert "#gym" in tag_names or "#workout" in tag_names

    def test_extract_empty_input(self):
        from cli_anything.social_trends.core import youtube as yt_mod
        result = yt_mod.extract_trending_hashtags_from_titles([])
        assert result == []

    def test_extract_deduplicates_counts(self):
        from cli_anything.social_trends.core import youtube as yt_mod
        videos = [
            {"title": "#viral", "description": "#viral", "tags": ["viral"]},
            {"title": "#viral content", "description": "", "tags": []},
        ]
        hashtags = yt_mod.extract_trending_hashtags_from_titles(videos)
        viral = [h for h in hashtags if h["hashtag"] == "#viral"]
        assert len(viral) == 1
        assert viral[0]["count"] >= 2


# ── tiktok helper tests (no API calls) ───────────────────────────

class TestTiktokHelpers:
    def test_walk_for_hashtags_empty(self):
        from cli_anything.social_trends.core.tiktok import _walk_for_hashtags
        result = _walk_for_hashtags({})
        assert result == []

    def test_walk_for_hashtags_nested(self):
        from cli_anything.social_trends.core.tiktok import _walk_for_hashtags
        data = {
            "items": [
                {"challengeName": "fitness2024", "id": "abc", "stats": {"videoCount": 5000}},
                {"challengeName": "workout", "id": "xyz", "stats": {"videoCount": 3000}},
            ]
        }
        result = _walk_for_hashtags(data)
        names = [r["hashtag"] for r in result]
        assert "#fitness2024" in names
        assert "#workout" in names
