"""Unit tests for social_trends core modules.

All tests run offline — no real network calls are made.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from cli_anything.social_trends.core import trend_analyzer, account_optimizer, theme_page_guide, content_planner


# ── trend_analyzer tests ──────────────────────────────────────────────────────

class TestTrendAnalyzer:
    def test_normalize_tag_adds_hash(self):
        result = trend_analyzer._normalize_tag("fyp")
        assert result == "#fyp"

    def test_normalize_tag_keeps_hash(self):
        result = trend_analyzer._normalize_tag("#fyp")
        assert result == "#fyp"

    def test_merge_hashtags_cross_platform_bonus(self):
        yt = [{"hashtag": "#fyp", "frequency": 3}]
        tt = [{"hashtag": "#fyp", "views": 1_000_000}]
        merged = trend_analyzer.merge_hashtags(yt, tt)
        assert len(merged) == 1
        assert merged[0]["cross_platform"] is True
        assert merged[0]["score"] > 30  # cross-platform bonus applied

    def test_merge_hashtags_separate_platforms(self):
        yt = [{"hashtag": "#gaming", "frequency": 2}]
        tt = [{"hashtag": "#fitness", "views": 500_000}]
        merged = trend_analyzer.merge_hashtags(yt, tt)
        assert len(merged) == 2
        assert not any(m["cross_platform"] for m in merged)

    def test_score_hashtag_set_returns_analysis(self):
        result = trend_analyzer.score_hashtag_set(["#fyp", "#fitness", "#workout"])
        assert "hashtags" in result
        assert "mix_score" in result
        assert "suggestion" in result
        assert len(result["hashtags"]) == 3

    def test_hashtag_tier_discovery(self):
        tier = trend_analyzer._hashtag_tier("#fyp")
        assert tier["tier"] == "discovery"

    def test_hashtag_tier_large_niche(self):
        tier = trend_analyzer._hashtag_tier("#fitness")
        assert tier["tier"] == "large-niche"

    def test_hashtag_tier_micro_niche(self):
        tier = trend_analyzer._hashtag_tier("#sourdoughbaking")
        assert tier["tier"] == "micro-niche"

    def test_mix_score_excellent(self):
        ranked = [
            {"tier": "discovery"},
            {"tier": "large-niche"},
            {"tier": "micro-niche"},
        ]
        score = trend_analyzer._mix_score(ranked)
        assert "Excellent" in score or "Good" in score

    def test_extract_themes_returns_dict(self):
        videos = [
            {"title": "Best workout routine 2024", "description": "gym training",
             "tags": [], "hashtags": []},
            {"title": "Top recipes for fitness", "description": "meal prep food",
             "tags": [], "hashtags": []},
        ]
        themes = trend_analyzer._extract_themes(videos)
        assert isinstance(themes, dict)
        assert "fitness" in themes or "food" in themes

    def test_merge_trends_structure(self):
        yt = [{"title": "Gaming video", "description": "gaming gameplay",
               "tags": [], "hashtags": []}]
        tt = [{"title": "Gaming clip", "description": "game gameplay",
               "hashtags": [], "tags": []}]
        result = trend_analyzer.merge_trends(yt, tt)
        assert "top_themes" in result
        assert "youtube_video_count" in result
        assert "tiktok_video_count" in result


# ── account_optimizer tests ───────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_optimise_tiktok_returns_report(self):
        result = account_optimizer.optimise_account("tiktok", niche="fitness",
                                                    followers=5000, avg_views=2000)
        assert result["platform"] == "tiktok"
        assert "profile_checklist" in result
        assert "posting_schedule" in result
        assert "growth_tactics" in result
        assert "monetisation_readiness" in result

    def test_optimise_youtube_returns_report(self):
        result = account_optimizer.optimise_account("youtube", niche="gaming",
                                                    followers=10000, avg_views=5000)
        assert result["platform"] == "youtube"
        assert "channel_checklist" in result
        assert "upload_schedule" in result

    def test_optimise_instagram_returns_report(self):
        result = account_optimizer.optimise_account("instagram", niche="fashion",
                                                    followers=3000, avg_views=1500)
        assert result["platform"] == "instagram"
        assert "reels_strategy" in result
        assert "content_mix" in result

    def test_unsupported_platform_raises(self):
        with pytest.raises(ValueError, match="Unsupported platform"):
            account_optimizer.optimise_account("snapchat")

    def test_engagement_rate_calculation(self):
        er = account_optimizer._engagement_rate(10000, 500)
        assert er == 5.0

    def test_engagement_rate_zero_followers(self):
        er = account_optimizer._engagement_rate(0, 100)
        assert er == 0.0

    def test_growth_stage_starter(self):
        assert account_optimizer._growth_stage(500) == "starter"

    def test_growth_stage_growing(self):
        assert account_optimizer._growth_stage(5000) == "growing"

    def test_growth_stage_established(self):
        assert account_optimizer._growth_stage(50000) == "established"

    def test_growth_stage_authority(self):
        assert account_optimizer._growth_stage(500000) == "authority"

    def test_add_and_list_accounts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(account_optimizer, "PROFILES_FILE", tmp_path / "accounts.json")
        account_optimizer.add_account("tiktok", "testuser", "fitness", 5000, 2000)
        accounts = account_optimizer.list_accounts()
        assert len(accounts) == 1
        assert accounts[0]["username"] == "testuser"

    def test_remove_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(account_optimizer, "PROFILES_FILE", tmp_path / "accounts.json")
        account_optimizer.add_account("tiktok", "testuser", "fitness")
        account_optimizer.remove_account("tiktok", "testuser")
        assert account_optimizer.list_accounts() == []

    def test_remove_nonexistent_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(account_optimizer, "PROFILES_FILE", tmp_path / "accounts.json")
        with pytest.raises(KeyError):
            account_optimizer.remove_account("tiktok", "nobody")

    def test_monetisation_at_10k(self):
        info = account_optimizer._tt_monetisation(10000)
        assert "tiktok_creator_fund" in info

    def test_monetisation_under_1k(self):
        info = account_optimizer._tt_monetisation(500)
        assert "focus" in info


# ── theme_page_guide tests ────────────────────────────────────────────────────

class TestThemePageGuide:
    def test_list_niches_returns_all(self):
        niches = theme_page_guide.list_niches()
        assert len(niches) >= 10
        assert all("niche" in n for n in niches)

    def test_list_niches_sorted_viral(self):
        niches = theme_page_guide.list_niches("viral_potential")
        potentials = [n["viral_potential"] for n in niches]
        assert potentials[0] in ("very-high", "high")

    def test_get_niche_info_valid(self):
        info = theme_page_guide.get_niche_info("fitness")
        assert info["niche"] == "fitness"
        assert "monetisation" in info
        assert "competition" in info

    def test_get_niche_info_invalid_raises(self):
        with pytest.raises(ValueError, match="not found"):
            theme_page_guide.get_niche_info("unknownniche12345")

    def test_get_sourcing_all(self):
        strategies = theme_page_guide.get_sourcing_strategy()
        assert isinstance(strategies, list)
        assert len(strategies) >= 3

    def test_get_sourcing_specific(self):
        result = theme_page_guide.get_sourcing_strategy("repost_with_credit")
        assert "steps" in result
        assert "effort" in result

    def test_get_monetisation_all(self):
        strategies = theme_page_guide.get_monetisation_strategy()
        assert isinstance(strategies, list)
        assert len(strategies) >= 4

    def test_get_monetisation_filtered_by_followers(self):
        all_strategies = theme_page_guide.get_monetisation_strategy(followers=0)
        few_strategies = theme_page_guide.get_monetisation_strategy(followers=50)
        assert len(all_strategies) >= len(few_strategies)

    def test_get_setup_checklist(self):
        checklist = theme_page_guide.get_setup_checklist()
        assert len(checklist) == 6
        steps = [c["step"] for c in checklist]
        assert steps == list(range(1, 7))

    def test_get_conversion_funnel_structure(self):
        funnel = theme_page_guide.get_conversion_funnel("fitness", 5000)
        assert "funnel_stages" in funnel
        assert len(funnel["funnel_stages"]) == 5
        assert "immediate_actions" in funnel
        stages = [s["stage"] for s in funnel["funnel_stages"]]
        assert "Awareness" in stages
        assert "Conversion" in stages


# ── content_planner tests ─────────────────────────────────────────────────────

class TestContentPlanner:
    def test_optimal_time_returns_string(self):
        t = content_planner._optimal_time("tiktok", 0, 0)
        assert isinstance(t, str)
        assert "AM" in t or "PM" in t

    def test_select_hashtags_count(self):
        tags = content_planner._select_hashtags(["#viral", "#trending"], "fitness", "tiktok", 5)
        assert len(tags) <= 5
        assert len(tags) >= 1

    def test_select_hashtags_unique(self):
        tags = content_planner._select_hashtags(["#fyp", "#fitness"], "fitness", "tiktok", 7)
        assert len(tags) == len(set(tags))

    def test_niche_hashtags_known_niche(self):
        tags = content_planner._niche_hashtags("fitness", "tiktok")
        assert any("fitness" in t for t in tags)

    def test_niche_hashtags_unknown_niche(self):
        tags = content_planner._niche_hashtags("unknownniche", "tiktok")
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_content_themes_known_niche(self):
        themes = content_planner._content_themes_for_niche("motivation")
        assert len(themes) > 0
        assert all("type" in t and "hook" in t for t in themes)

    def test_content_themes_fallback(self):
        themes = content_planner._content_themes_for_niche("unknownniche")
        assert len(themes) > 0

    def test_effort_estimate_returns_string(self):
        assert content_planner._effort_estimate("tutorial") in ("low", "medium", "high")

    def test_viral_estimate_returns_string(self):
        assert content_planner._viral_estimate("story-time") in ("standard", "medium", "high")

    def test_generate_hashtag_set_offline(self, monkeypatch):
        # Patch live scraping to return empty
        monkeypatch.setattr(
            "cli_anything.social_trends.core.tiktok_trends.get_trending_hashtags",
            lambda *a, **kw: [],
        )
        result = content_planner.generate_hashtag_set("fitness", "tiktok", "US", 5)
        assert "hashtag_set" in result
        assert "copy_paste" in result
        assert "analysis" in result

    def test_generate_content_ideas_offline(self, monkeypatch):
        monkeypatch.setattr(
            "cli_anything.social_trends.core.youtube_trends.get_trending_videos",
            lambda *a, **kw: [],
        )
        monkeypatch.setattr(
            "cli_anything.social_trends.core.tiktok_trends.get_trending_videos",
            lambda *a, **kw: [],
        )
        ideas = content_planner.generate_content_ideas("fitness", 5, "US")
        assert isinstance(ideas, list)
        assert len(ideas) >= 1
