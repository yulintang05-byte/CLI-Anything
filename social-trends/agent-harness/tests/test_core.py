"""Unit tests for social-trends core modules."""

import json
import os
import tempfile
import pytest

from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import account as account_mod
from cli_anything.social_trends.core import theme_page as theme_mod


# ── trends ────────────────────────────────────────────────────────────────────

class TestTrends:
    def test_fetch_returns_sources(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        result = trends_mod.fetch_trends("all", force=True)
        assert "sources" in result
        assert "tiktok" in result["sources"]
        assert "youtube" in result["sources"]

    def test_list_trends_tiktok(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        trends_mod.fetch_trends("tiktok", force=True)
        result = trends_mod.list_trends("tiktok")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(t.get("platform") == "tiktok" for t in result)

    def test_list_trends_all_platforms(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        trends_mod.fetch_trends("all", force=True)
        result = trends_mod.list_trends("all")
        platforms = {t.get("platform") for t in result}
        assert "tiktok" in platforms
        assert "youtube" in platforms

    def test_show_trend_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        trends_mod.fetch_trends("tiktok", force=True)
        all_t = trends_mod.list_trends("tiktok")
        first_id = all_t[0]["id"]
        detail = trends_mod.show_trend(first_id)
        assert detail["id"] == first_id

    def test_show_trend_missing_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        trends_mod.fetch_trends("tiktok", force=True)
        with pytest.raises(ValueError, match="not found"):
            trends_mod.show_trend("nonexistent_id")

    def test_add_custom_trend(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        trends_mod.fetch_trends("tiktok", force=True)
        result = trends_mod.add_custom_trend(
            "tiktok", "Test Trend", "test", "A test trend", ["#test", "#fyp"]
        )
        assert result["title"] == "Test Trend"
        assert result["status"] == "tracking"
        assert "#test" in result["hashtags"]

    def test_get_cache_info(self, tmp_path, monkeypatch):
        monkeypatch.setattr(trends_mod, "_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(trends_mod, "_CACHE_FILE", str(tmp_path / "cache.json"))
        trends_mod.fetch_trends("all", force=True)
        info = trends_mod.get_cache_info()
        assert "platforms" in info
        assert "tiktok" in info["platforms"]

    def test_seed_data_structure(self):
        for platform, items in trends_mod._SEED_TRENDS.items():
            assert isinstance(items, list)
            for item in items:
                assert "id" in item
                assert "title" in item
                assert "status" in item
                assert "hashtags" in item


# ── hashtags ──────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_suggest_returns_sets(self):
        result = hashtags_mod.suggest_hashtags("fitness", "tiktok")
        assert "primary_set" in result
        assert "extended_set" in result
        assert "copy_paste" in result
        assert len(result["primary_set"]) > 0

    def test_suggest_respects_platform_limit(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            result = hashtags_mod.suggest_hashtags("fitness", platform)
            assert len(result["primary_set"]) <= result["optimal_count"]

    def test_suggest_invalid_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            hashtags_mod.suggest_hashtags("fitness", "myspace")

    def test_suggest_invalid_niche(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            hashtags_mod.suggest_hashtags("astrology", "tiktok")

    def test_all_platforms_covers_all(self):
        result = hashtags_mod.hashtag_set_all_platforms("finance")
        assert set(result.keys()) == {"tiktok", "youtube", "instagram"}

    def test_trending_hashtags_tiktok(self):
        result = hashtags_mod.trending_hashtags("tiktok")
        assert isinstance(result, list)
        assert len(result) > 0
        assert all("tag" in t for t in result)

    def test_trending_hashtags_invalid_platform(self):
        with pytest.raises(ValueError):
            hashtags_mod.trending_hashtags("snapchat")

    def test_list_niches_nonempty(self):
        niches = hashtags_mod.list_niches()
        assert isinstance(niches, list)
        assert "fitness" in niches
        assert "finance" in niches

    def test_hashtags_are_prefixed(self):
        result = hashtags_mod.suggest_hashtags("music", "instagram", "viral")
        for tag in result["primary_set"]:
            assert tag.startswith("#"), f"Tag missing # prefix: {tag}"

    def test_all_goals_work(self):
        for goal in ["viral", "growth", "engagement", "sales", "community"]:
            result = hashtags_mod.suggest_hashtags("tech", "tiktok", goal)
            assert len(result["primary_set"]) > 0


# ── music ─────────────────────────────────────────────────────────────────────

class TestMusic:
    def test_trending_tiktok(self):
        result = music_mod.trending_music("tiktok")
        assert isinstance(result, list)
        assert len(result) > 0
        required_fields = {"id", "title", "artist", "genre", "status"}
        for track in result:
            assert required_fields.issubset(track.keys())

    def test_trending_youtube(self):
        result = music_mod.trending_music("youtube")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_trending_invalid_platform(self):
        with pytest.raises(ValueError):
            music_mod.trending_music("pinterest")

    def test_search_by_title(self):
        result = music_mod.search_music("phonk")
        assert len(result) > 0
        assert any("phonk" in r["title"].lower() or "phonk" in r["genre"].lower() for r in result)

    def test_search_by_genre(self):
        result = music_mod.search_music("lo-fi")
        assert len(result) > 0

    def test_search_empty_returns_all(self):
        result = music_mod.search_music("", "all")
        all_tiktok = music_mod.trending_music("tiktok")
        all_yt = music_mod.trending_music("youtube")
        assert len(result) == len(all_tiktok) + len(all_yt)

    def test_get_music_by_trend(self):
        result = music_mod.get_music_by_trend("Phonk Dance")
        assert len(result) > 0

    def test_music_by_use_case_gym(self):
        result = music_mod.music_by_use_case("gym")
        assert len(result) > 0

    def test_list_genres_nonempty(self):
        genres = music_mod.list_genres()
        assert isinstance(genres, list)
        assert len(genres) > 0


# ── account ───────────────────────────────────────────────────────────────────

class TestAccount:
    def test_optimize_returns_checklist(self):
        for p in ["tiktok", "youtube", "instagram"]:
            result = account_mod.optimize_account(p)
            assert "checklist" in result
            assert len(result["checklist"]) > 0
            assert "critical_items" in result
            assert len(result["critical_items"]) > 0

    def test_optimize_invalid_platform(self):
        with pytest.raises(ValueError):
            account_mod.optimize_account("twitch")

    def test_schedule_returns_windows(self):
        for p in ["tiktok", "youtube", "instagram"]:
            result = account_mod.account_schedule(p)
            assert "best_days" in result
            assert "best_times" in result
            assert "frequency" in result

    def test_analyze_perfect_score(self):
        checklist = account_mod.optimize_account("tiktok")["checklist"]
        all_items = [i["item"] for i in checklist]
        result = account_mod.analyze_account("tiktok", "fitness", all_items)
        assert result["score"] == result["max_score"]
        assert result["grade"] == "A"

    def test_analyze_zero_score(self):
        result = account_mod.analyze_account("tiktok", "fitness", [])
        assert result["score"] == 0
        assert result["grade"] == "D"

    def test_analyze_returns_next_actions(self):
        result = account_mod.analyze_account("youtube", "tech", [])
        assert "next_actions" in result
        assert len(result["next_actions"]) > 0

    def test_growth_roadmap_seed_phase(self):
        result = account_mod.growth_roadmap("tiktok", 100)
        assert result["current_phase"] == "seed"

    def test_growth_roadmap_monetize_phase(self):
        result = account_mod.growth_roadmap("tiktok", 15000)
        assert result["current_phase"] == "monetize"

    def test_growth_roadmap_has_next_milestone(self):
        result = account_mod.growth_roadmap("youtube", 500)
        assert result["next_milestone"] is not None
        assert result["followers_to_next"] > 0

    def test_list_platforms(self):
        platforms = account_mod.list_platforms()
        assert "tiktok" in platforms
        assert "youtube" in platforms
        assert "instagram" in platforms


# ── theme_page ────────────────────────────────────────────────────────────────

class TestThemePage:
    def test_create_blueprint_fields(self):
        result = theme_mod.create_theme_page("finance")
        required = {
            "niche", "name", "difficulty", "monthly_potential",
            "first_30_days", "setup_action_plan", "monetization_stack",
        }
        assert required.issubset(result.keys())
        assert len(result["first_30_days"]) == 5
        assert len(result["setup_action_plan"]) == 6

    def test_create_invalid_niche(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            theme_mod.create_theme_page("knitting")

    def test_list_niches(self):
        niches = theme_mod.list_niches()
        assert isinstance(niches, list)
        assert len(niches) > 0
        assert all("niche" in n and "monthly_potential" in n for n in niches)

    def test_monetize_returns_methods(self):
        result = theme_mod.monetize("ai_tools")
        assert "all_methods" in result
        assert len(result["all_methods"]) > 0
        assert "action_steps" in result["all_methods"][0]

    def test_content_calendar_length(self):
        calendar = theme_mod.content_calendar("fitness", days=7)
        assert len(calendar) == 7

    def test_content_calendar_structure(self):
        calendar = theme_mod.content_calendar("motivation", days=3)
        for day in calendar:
            assert "day" in day
            assert "date" in day
            assert "format" in day
            assert "hook_idea" in day
            assert "cta" in day

    def test_compare_niches(self):
        result = theme_mod.compare_niches(["finance", "fitness", "ai_tools"])
        assert len(result) == 3
        niches_out = {r["niche"] for r in result}
        assert niches_out == {"finance", "fitness", "ai_tools"}

    def test_compare_invalid_niche(self):
        with pytest.raises(ValueError):
            theme_mod.compare_niches(["finance", "woodworking"])

    def test_all_niches_have_required_fields(self):
        for niche_id, data in theme_mod._NICHES.items():
            assert "name" in data
            assert "difficulty" in data
            assert "monetization" in data
            assert "content_types" in data
            assert len(data["content_types"]) > 0
