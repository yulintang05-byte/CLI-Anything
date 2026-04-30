"""Unit tests for social-media CLI core modules."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from cli_anything.social_media.core.session import Session
from cli_anything.social_media.core import trends as trends_mod
from cli_anything.social_media.core import hashtags as hashtags_mod
from cli_anything.social_media.core import music as music_mod
from cli_anything.social_media.core import accounts as accounts_mod
from cli_anything.social_media.core import theme_pages as theme_mod


# -- Session Tests ------------------------------------------------------------

class TestSession:
    def test_initial_state(self):
        sess = Session()
        assert not sess.has_project()

    def test_set_get_project(self):
        sess = Session()
        proj = trends_mod.create_project("Test")
        sess.set_project(proj)
        assert sess.has_project()
        assert sess.get_project()["name"] == "Test"

    def test_get_project_raises_without_project(self):
        sess = Session()
        with pytest.raises(RuntimeError, match="No project loaded"):
            sess.get_project()

    def test_snapshot_and_undo(self):
        sess = Session()
        proj = trends_mod.create_project("Test")
        sess.set_project(proj)
        original_name = proj["name"]
        sess.snapshot("change name")
        proj["name"] = "Changed"
        desc = sess.undo()
        assert desc == "change name"

    def test_undo_raises_with_no_history(self):
        sess = Session()
        sess.set_project(trends_mod.create_project())
        with pytest.raises(RuntimeError):
            sess.undo()

    def test_status_keys(self):
        sess = Session()
        sess.set_project(trends_mod.create_project("My Project"))
        status = sess.status()
        assert "has_project" in status
        assert "project_name" in status
        assert status["project_name"] == "My Project"


# -- Trends Module Tests ------------------------------------------------------

class TestTrendsModule:
    def test_create_project(self):
        proj = trends_mod.create_project("Test Project")
        assert proj["name"] == "Test Project"
        assert "accounts" in proj
        assert "trend_history" in proj
        assert isinstance(proj["accounts"], list)

    def test_get_project_info(self):
        proj = trends_mod.create_project("Info Test")
        info = trends_mod.get_project_info(proj)
        assert info["name"] == "Info Test"
        assert info["accounts"] == 0
        assert info["trend_snapshots"] == 0

    def test_fetch_trends_auto_creates_project(self):
        proj = trends_mod.create_project()
        result = trends_mod.fetch_trends(proj, platforms=["tiktok"], country="US", limit=5)
        assert "fetched_at" in result
        assert "tiktok" in result.get("data", {})
        assert len(proj["trend_history"]) == 1

    def test_fetch_trends_youtube(self):
        proj = trends_mod.create_project()
        result = trends_mod.fetch_trends(proj, platforms=["youtube"], country="US", limit=5)
        assert "youtube" in result.get("data", {})

    def test_fetch_trends_both_platforms(self):
        proj = trends_mod.create_project()
        result = trends_mod.fetch_trends(proj, platforms=["tiktok", "youtube"], limit=5)
        data = result.get("data", {})
        assert "tiktok" in data
        assert "youtube" in data

    def test_analyze_trends_raises_without_data(self):
        proj = trends_mod.create_project()
        with pytest.raises(ValueError, match="No trend data"):
            trends_mod.analyze_trends(proj)

    def test_analyze_trends_returns_insights(self):
        proj = trends_mod.create_project()
        trends_mod.fetch_trends(proj, platforms=["tiktok"], limit=5)
        analysis = trends_mod.analyze_trends(proj)
        assert "top_hashtags_cross_platform" in analysis
        assert "actionable_insights" in analysis
        assert isinstance(analysis["actionable_insights"], list)

    def test_trend_history_capped_at_10(self):
        proj = trends_mod.create_project()
        for _ in range(12):
            trends_mod.fetch_trends(proj, platforms=["tiktok"], limit=3)
        assert len(proj["trend_history"]) <= 10

    def test_get_latest_trends_raises_without_data(self):
        proj = trends_mod.create_project()
        with pytest.raises(ValueError):
            trends_mod.get_latest_trends(proj)


# -- Hashtags Module Tests ----------------------------------------------------

class TestHashtagsModule:
    def test_generate_balanced(self):
        result = hashtags_mod.generate_hashtag_set("finance", "tiktok", "balanced")
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0
        assert "caption_format" in result
        assert "tips" in result

    def test_generate_all_strategies(self):
        for strategy in ["balanced", "aggressive", "niche", "stealth"]:
            result = hashtags_mod.generate_hashtag_set("fitness", "tiktok", strategy)
            assert len(result["hashtags"]) > 0

    def test_generate_all_platforms(self):
        for platform in ["tiktok", "instagram", "youtube_shorts", "youtube"]:
            result = hashtags_mod.generate_hashtag_set("lifestyle", platform)
            assert result["platform"] == platform

    def test_generate_with_custom_tags(self):
        result = hashtags_mod.generate_hashtag_set(
            "fashion", "tiktok", custom_tags=["#mycustom", "#brand"]
        )
        assert "#mycustom" in result["hashtags"] or "#mycustom" in result["extended_set"]

    def test_score_hashtags(self):
        tags = ["#fyp", "#money", "#investing", "#debtfree"]
        result = hashtags_mod.score_hashtags(tags, platform="tiktok")
        assert "avg_score" in result
        assert "overall_rating" in result
        assert "scored_tags" in result
        assert len(result["scored_tags"]) == len(tags)

    def test_score_detects_too_many_tags(self):
        tags = [f"#tag{i}" for i in range(20)]
        result = hashtags_mod.score_hashtags(tags, platform="tiktok")
        assert any("Too many" in issue for issue in result["issues"])

    def test_list_niches(self):
        niches = hashtags_mod.list_niches()
        assert len(niches) > 5
        niche_names = [n["niche"] for n in niches]
        assert "finance" in niche_names
        assert "fitness" in niche_names

    def test_save_and_list_hashtag_sets(self):
        proj = trends_mod.create_project()
        hashtags_mod.save_hashtag_set(proj, "my-set", ["#fyp", "#money"], "finance", "tiktok")
        sets = hashtags_mod.list_hashtag_sets(proj)
        assert len(sets) == 1
        assert sets[0]["name"] == "my-set"


# -- Music Module Tests -------------------------------------------------------

class TestMusicModule:
    def test_fetch_trending_tiktok(self):
        result = music_mod.fetch_trending_music(platform="tiktok", region="US")
        assert "trending_sounds" in result
        assert isinstance(result["trending_sounds"], list)
        assert "usage_tips" in result

    def test_fetch_trending_youtube(self):
        result = music_mod.fetch_trending_music(platform="youtube", region="US")
        assert "trending_sounds" in result

    def test_recommend_sounds_all_niches(self):
        for niche in ["finance", "fitness", "lifestyle", "fashion", "food", "beauty"]:
            result = music_mod.recommend_sounds(niche)
            assert "recommendation" in result
            assert "copyright_tips" in result

    def test_list_categories(self):
        categories = music_mod.list_sound_categories()
        assert len(categories) > 3
        for cat in categories:
            assert "category" in cat
            assert "description" in cat


# -- Accounts Module Tests ----------------------------------------------------

class TestAccountsModule:
    def setup_method(self):
        self.proj = trends_mod.create_project("Test")

    def test_add_account(self):
        acc = accounts_mod.add_account(
            self.proj, "testuser", "tiktok", "finance",
            followers=5000, bio="Daily finance tips 💰"
        )
        assert acc["username"] == "testuser"
        assert acc["platform"] == "tiktok"
        assert acc["niche"] == "finance"

    def test_list_accounts(self):
        accounts_mod.add_account(self.proj, "user1", "tiktok", "fitness")
        accounts_mod.add_account(self.proj, "user2", "instagram", "fashion")
        accs = accounts_mod.list_accounts(self.proj)
        assert len(accs) == 2

    def test_get_account(self):
        accounts_mod.add_account(self.proj, "myuser", "tiktok", "lifestyle")
        acc = accounts_mod.get_account(self.proj, "myuser")
        assert acc["username"] == "myuser"

    def test_get_account_raises_not_found(self):
        with pytest.raises(ValueError):
            accounts_mod.get_account(self.proj, "nonexistent")

    def test_remove_account(self):
        accounts_mod.add_account(self.proj, "delme", "tiktok", "food")
        removed = accounts_mod.remove_account(self.proj, "delme")
        assert removed["username"] == "delme"
        assert len(accounts_mod.list_accounts(self.proj)) == 0

    def test_optimize_account_structure(self):
        accounts_mod.add_account(
            self.proj, "optuser", "tiktok", "finance",
            followers=15000, bio="Finance tips for millennials 💰 Link ↓"
        )
        result = accounts_mod.optimize_account(self.proj, "optuser")
        assert "optimization_score" in result
        assert "posting_plan" in result
        assert "hook_templates" in result
        assert "monetization_roadmap" in result
        assert "profile_checklist" in result
        assert isinstance(result["hook_templates"], list)

    def test_optimize_score_in_range(self):
        accounts_mod.add_account(self.proj, "scoreuser", "instagram", "lifestyle", followers=1000)
        result = accounts_mod.optimize_account(self.proj, "scoreuser")
        assert 0 <= result["optimization_score"] <= 100

    def test_score_account(self):
        accounts_mod.add_account(self.proj, "quickuser", "tiktok", "beauty", followers=2000)
        result = accounts_mod.score_account(self.proj, "quickuser")
        assert "score" in result
        assert "rating" in result
        assert 0 <= result["score"] <= 100

    def test_update_account(self):
        accounts_mod.add_account(self.proj, "updateme", "tiktok", "travel")
        accounts_mod.update_account(self.proj, "updateme", followers=25000, bio="Travel the world 🌍")
        acc = accounts_mod.get_account(self.proj, "updateme")
        assert acc["followers"] == 25000
        assert acc["bio"] == "Travel the world 🌍"

    def test_set_posting_schedule(self):
        accounts_mod.add_account(self.proj, "scheduser", "tiktok", "motivation")
        schedule = {"Monday": "8 AM", "Wednesday": "7 PM", "Friday": "6 PM"}
        result = accounts_mod.set_posting_schedule(self.proj, "scheduser", schedule)
        assert result["schedule"]["Monday"] == "8 AM"


# -- Theme Pages Module Tests -------------------------------------------------

class TestThemePagesModule:
    def test_list_niches_returns_data(self):
        niches = theme_mod.list_niches()
        assert len(niches) >= 5
        for n in niches:
            assert "niche" in n
            assert "competition" in n
            assert "monetization_ease" in n

    def test_get_conversion_guide_structure(self):
        guide = theme_mod.get_conversion_guide("finance")
        assert "conversion_funnel" in guide
        assert "dm_scripts" in guide
        assert "content_sourcing" in guide
        assert "monetization_methods" in guide
        assert "tools" in guide

    def test_conversion_funnel_has_5_stages(self):
        guide = theme_mod.get_conversion_guide()
        stages = guide["conversion_funnel"]["stages"]
        assert len(stages) == 5
        for i, stage in enumerate(stages, 1):
            assert stage["stage"] == i

    def test_get_niche_guide(self):
        guide = theme_mod.get_niche_guide("finance")
        assert "setup_steps" in guide
        assert "content_calendar" in guide
        assert "monetization_methods" in guide
        assert "growth_hacks" in guide

    def test_get_funnel_stage_valid(self):
        for i in range(1, 6):
            stage = theme_mod.get_funnel_stage(i)
            assert stage["stage"] == i
            assert "tactics" in stage

    def test_get_funnel_stage_invalid(self):
        with pytest.raises(ValueError):
            theme_mod.get_funnel_stage(0)
        with pytest.raises(ValueError):
            theme_mod.get_funnel_stage(6)

    def test_get_dm_scripts(self):
        result = theme_mod.get_dm_scripts()
        assert "scripts" in result
        assert "tips" in result
        scripts = result["scripts"]
        assert "new_follower_welcome" in scripts
        assert "soft_pitch" in scripts

    def test_monetization_methods_has_multiple(self):
        guide = theme_mod.get_conversion_guide("fitness")
        methods = guide["monetization_methods"]
        assert len(methods) >= 4
        for m in methods:
            assert "method" in m
            assert "earning_range" in m
