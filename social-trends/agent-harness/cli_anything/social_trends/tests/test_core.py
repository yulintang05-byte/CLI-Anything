"""Unit tests for Social Trends core modules."""

import pytest
import json
import os
import tempfile

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import project as proj_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.core import content_calendar as cal_mod
from cli_anything.social_trends.core import music as music_mod


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def session():
    s = Session()
    proj_mod.new_project(s, "test_project")
    return s

@pytest.fixture
def session_with_account(session):
    accounts_mod.add_account(session, name="Test Account", platform="tiktok", handle="testhandle", niche="fitness")
    return session

@pytest.fixture
def session_with_trends(session):
    session.get_project()["trends"] = [
        {
            "video_id": "vid1",
            "platform": "youtube",
            "title": "Fitness Workout #fitness #gym",
            "description": "Best workout routine",
            "view_count": 1_000_000,
            "like_count": 50_000,
            "hashtags": ["#fitness", "#gym", "#workout"],
            "fetched_at": "2024-01-01",
        },
        {
            "video_id": "vid2",
            "platform": "tiktok",
            "title": "Dance Challenge #dance #viral",
            "description": "Trending dance move",
            "view_count": 5_000_000,
            "like_count": 200_000,
            "hashtags": ["#dance", "#viral", "#trending"],
            "fetched_at": "2024-01-01",
        },
        {
            "video_id": "vid3",
            "platform": "tiktok",
            "title": "Gym motivation",
            "description": "Fitness motivation video",
            "view_count": 2_500_000,
            "like_count": 100_000,
            "hashtags": ["#fitness", "#motivation", "#gym"],
            "fetched_at": "2024-01-01",
        },
    ]
    return session


# ── Session tests ─────────────────────────────────────────────────────────────

class TestSession:
    def test_new_session_has_no_project(self):
        s = Session()
        assert not s.has_project()

    def test_get_project_raises_without_project(self):
        s = Session()
        with pytest.raises(RuntimeError, match="No project loaded"):
            s.get_project()

    def test_snapshot_and_undo(self, session):
        p = session.get_project()
        p["name"] = "original"
        session.snapshot("set name original")
        p["name"] = "changed"
        desc = session.undo()
        assert desc == "set name original"
        assert session.get_project()["name"] == "original"

    def test_undo_empty_raises(self, session):
        with pytest.raises(RuntimeError, match="Nothing to undo"):
            session.undo()

    def test_redo_after_undo(self, session):
        p = session.get_project()
        p["name"] = "v1"
        session.snapshot("v1")
        p["name"] = "v2"
        session.undo()
        session.redo()
        assert session.get_project()["name"] == "v2"

    def test_redo_empty_raises(self, session):
        with pytest.raises(RuntimeError, match="Nothing to redo"):
            session.redo()

    def test_status(self, session):
        status = session.status()
        assert status["has_project"] is True
        assert status["project_name"] == "test_project"

    def test_save_and_load(self, session):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            session.save_session(path)
            assert os.path.isfile(path)
            with open(path) as f:
                data = json.load(f)
            assert data["name"] == "test_project"
        finally:
            os.unlink(path)

    def test_max_undo_stack(self, session):
        p = session.get_project()
        for i in range(Session.MAX_UNDO + 10):
            p["name"] = f"v{i}"
            session.snapshot(f"step {i}")
        assert len(session._undo_stack) == Session.MAX_UNDO

    def test_history_list(self, session):
        session.snapshot("action 1")
        session.snapshot("action 2")
        history = session.list_history()
        assert len(history) == 2
        assert history[0]["description"] == "action 2"


# ── Project tests ─────────────────────────────────────────────────────────────

class TestProject:
    def test_new_project_structure(self):
        s = Session()
        p = proj_mod.new_project(s, "myproject")
        assert p["name"] == "myproject"
        assert "config" in p
        assert "accounts" in p
        assert "trends" in p
        assert "hashtag_sets" in p
        assert "calendar" in p

    def test_set_config(self, session):
        result = proj_mod.set_config(session, "youtube_api_key", "testkey123")
        assert result["value"] == "testkey123"
        assert session.get_project()["config"]["youtube_api_key"] == "testkey123"

    def test_get_config_masks_api_key(self, session):
        proj_mod.set_config(session, "youtube_api_key", "abcdefghijklmno")
        config = proj_mod.get_config(session)
        assert "..." in config["youtube_api_key"]
        assert "abcdefgh" in config["youtube_api_key"]

    def test_open_missing_file_raises(self):
        s = Session()
        with pytest.raises(FileNotFoundError):
            proj_mod.open_project(s, "/nonexistent/path.json")

    def test_save_and_open_roundtrip(self, session):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            session.save_session(path)
            s2 = Session()
            p2 = proj_mod.open_project(s2, path)
            assert p2["name"] == "test_project"
        finally:
            os.unlink(path)

    def test_project_info(self, session):
        info = proj_mod.project_info(session)
        assert info["name"] == "test_project"
        assert "accounts_count" in info
        assert "trends_cached" in info


# ── Hashtag tests ─────────────────────────────────────────────────────────────

class TestHashtags:
    def test_research_returns_tags(self, session):
        result = hashtags_mod.research_hashtags(session, topic="fitness", platform="tiktok")
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0

    def test_research_includes_platform_rules(self, session):
        result = hashtags_mod.research_hashtags(session, topic="fitness", platform="tiktok")
        assert "platform_rules" in result
        assert result["platform_rules"]["max_hashtags"] == 5

    def test_score_known_hashtag(self):
        result = hashtags_mod.score_hashtag("#fitness")
        assert result["niche"] == "fitness"
        assert result["tier"] in hashtags_mod.HASHTAG_TIERS

    def test_score_unknown_hashtag(self):
        result = hashtags_mod.score_hashtag("#unknownrandometag123")
        assert result["tier"] == "unknown"

    def test_generate_set_saves_to_project(self, session):
        result = hashtags_mod.generate_hashtag_set(session, niche="fitness", platform="tiktok")
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0
        assert len(session.get_project()["hashtag_sets"]) == 1

    def test_generate_set_balanced(self, session):
        result = hashtags_mod.generate_hashtag_set(session, niche="fitness", platform="tiktok", mix="balanced")
        assert result["mix_strategy"] == "balanced"

    def test_generate_set_aggressive(self, session):
        result = hashtags_mod.generate_hashtag_set(session, niche="fitness", platform="tiktok", mix="aggressive")
        assert result["mix_strategy"] == "aggressive"

    def test_generate_set_safe(self, session):
        result = hashtags_mod.generate_hashtag_set(session, niche="fitness", platform="tiktok", mix="safe")
        assert result["mix_strategy"] == "safe"

    def test_list_hashtag_sets(self, session):
        hashtags_mod.generate_hashtag_set(session, niche="fitness", platform="tiktok")
        hashtags_mod.generate_hashtag_set(session, niche="beauty", platform="instagram")
        sets = hashtags_mod.list_hashtag_sets(session)
        assert len(sets) == 2

    def test_caption_ready_field(self, session):
        result = hashtags_mod.generate_hashtag_set(session, niche="fitness")
        assert result["caption_ready"].startswith("#")

    def test_recommended_mix_structure(self, session):
        result = hashtags_mod.research_hashtags(session, topic="beauty", platform="instagram")
        mix = result["recommended_mix"]
        assert "tags" in mix
        assert "count" in mix
        assert "strategy" in mix

    def test_all_niches_have_tiers(self):
        for niche, tiers in hashtags_mod.NICHE_HASHTAG_DB.items():
            assert len(tiers) >= 3, f"Niche '{niche}' has fewer than 3 tiers"

    def test_platform_rules_all_platforms(self):
        for platform in ["tiktok", "instagram", "youtube", "twitter"]:
            assert platform in hashtags_mod.PLATFORM_HASHTAG_RULES

    def test_research_with_cached_trends(self, session_with_trends):
        result = hashtags_mod.research_hashtags(session_with_trends, topic="fitness", platform="tiktok")
        assert len(result["hashtags"]) > 0


# ── Accounts tests ────────────────────────────────────────────────────────────

class TestAccounts:
    def test_add_account(self, session):
        result = accounts_mod.add_account(session, name="Main", platform="tiktok", handle="myhandle")
        assert result["handle"] == "myhandle"
        assert result["platform"] == "tiktok"

    def test_add_duplicate_raises(self, session_with_account):
        with pytest.raises(ValueError, match="already exists"):
            accounts_mod.add_account(session_with_account, name="Dup", platform="tiktok", handle="testhandle")

    def test_invalid_platform_raises(self, session):
        with pytest.raises(ValueError, match="Unsupported platform"):
            accounts_mod.add_account(session, name="Bad", platform="snapchat", handle="user")

    def test_list_accounts(self, session_with_account):
        result = accounts_mod.list_accounts(session_with_account)
        assert len(result) == 1
        assert result[0]["handle"] == "testhandle"

    def test_list_accounts_filter_platform(self, session):
        accounts_mod.add_account(session, name="TikTok", platform="tiktok", handle="tt_user")
        accounts_mod.add_account(session, name="YouTube", platform="youtube", handle="yt_user")
        result = accounts_mod.list_accounts(session, platform="tiktok")
        assert len(result) == 1
        assert result[0]["platform"] == "tiktok"

    def test_update_stats(self, session_with_account):
        result = accounts_mod.update_account_stats(
            session_with_account, handle="testhandle", platform="tiktok",
            followers=10000, posts=50, avg_likes=500, avg_comments=30
        )
        assert result["stats"]["followers"] == 10000
        assert result["stats"]["engagement_rate"] > 0

    def test_engagement_rate_calculated(self, session_with_account):
        accounts_mod.update_account_stats(
            session_with_account, handle="testhandle", platform="tiktok",
            followers=1000, avg_likes=50, avg_comments=10
        )
        accs = accounts_mod.list_accounts(session_with_account)
        assert accs[0]["stats"]["engagement_rate"] == 6.0

    def test_optimize_returns_score(self, session_with_account):
        accounts_mod.update_account_stats(
            session_with_account, handle="testhandle", platform="tiktok",
            followers=10000, posts=50
        )
        result = accounts_mod.optimize_account(session_with_account, handle="testhandle", platform="tiktok")
        assert "optimization_score" in result
        assert "grade" in result
        assert "checks" in result
        assert "top_tips" in result
        assert result["grade"] in ["A", "B", "C", "D", "F"]

    def test_optimize_stores_score_on_account(self, session_with_account):
        accounts_mod.optimize_account(session_with_account, handle="testhandle", platform="tiktok")
        accs = accounts_mod.list_accounts(session_with_account)
        assert accs[0]["optimization_score"] is not None

    def test_remove_account(self, session_with_account):
        result = accounts_mod.remove_account(session_with_account, handle="testhandle", platform="tiktok")
        assert result["removed"] == 1
        assert len(accounts_mod.list_accounts(session_with_account)) == 0

    def test_remove_nonexistent_raises(self, session):
        with pytest.raises(ValueError, match="not found"):
            accounts_mod.remove_account(session, handle="nobody", platform="tiktok")

    def test_optimize_not_found_raises(self, session):
        with pytest.raises(ValueError, match="not found"):
            accounts_mod.optimize_account(session, handle="ghost", platform="tiktok")

    def test_all_platforms_have_optimization_rules(self):
        for platform in accounts_mod.SUPPORTED_PLATFORMS:
            assert platform in accounts_mod.PLATFORM_OPTIMIZATION


# ── Theme Page tests ──────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches_nonempty(self):
        niches = theme_mod.list_niches()
        assert len(niches) >= 5

    def test_list_niches_structure(self):
        niches = theme_mod.list_niches()
        for n in niches:
            assert "niche_key" in n
            assert "label" in n
            assert "difficulty" in n
            assert "monetization_potential" in n

    def test_get_niche_guide_valid(self):
        guide = theme_mod.get_niche_guide("luxury_lifestyle")
        assert guide["label"] == "Luxury Lifestyle"
        assert "content_pillars" in guide
        assert len(guide["content_pillars"]) >= 3

    def test_get_niche_guide_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            theme_mod.get_niche_guide("nonexistent_niche")

    def test_get_strategy_structure(self):
        result = theme_mod.get_strategy("motivation")
        assert "content_pillars" in result
        assert "monetization" in result
        assert "conversion_funnel" in result

    def test_get_content_pillars(self):
        result = theme_mod.get_content_pillars("fitness")
        assert "pillars" in result
        assert len(result["pillars"]) >= 3
        assert "content_mix" in result
        assert "repost_guidelines" in result

    def test_get_posting_schedule(self):
        result = theme_mod.get_posting_schedule("fitness", "tiktok")
        assert "daily_posts" in result
        assert "times" in result
        assert "content_rotation" in result
        assert len(result["content_rotation"]) == 7

    def test_converting_guide_phases(self):
        guide = theme_mod.converting_theme_page_guide()
        assert "phases" in guide
        assert len(guide["phases"]) >= 5
        assert "tools_needed" in guide
        assert "income_timeline" in guide
        assert "common_mistakes" in guide

    def test_all_niches_have_required_fields(self):
        for key, data in theme_mod.THEME_PAGE_NICHES.items():
            assert "content_pillars" in data, f"{key} missing content_pillars"
            assert "top_hashtags" in data, f"{key} missing top_hashtags"
            assert "monetization_paths" in data, f"{key} missing monetization_paths"

    def test_converting_guide_has_income_timeline(self):
        guide = theme_mod.converting_theme_page_guide()
        timeline = guide["income_timeline"]
        assert "month_1" in timeline
        assert "month_6" in timeline
        assert "month_12" in timeline


# ── Content Calendar tests ────────────────────────────────────────────────────

class TestContentCalendar:
    def test_generate_calendar_entries(self, session):
        result = cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=2)
        assert result["success"] is True
        assert result["total_entries"] > 0
        assert len(session.get_project()["calendar"]) > 0

    def test_generate_calendar_weeks(self, session):
        result = cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        assert result["weeks"] == 1
        assert result["total_entries"] <= 7 * 4  # max 4 posts/day * 7 days

    def test_view_calendar_empty(self, session):
        entries = cal_mod.view_calendar(session)
        assert entries == []

    def test_view_calendar_after_generate(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        entries = cal_mod.view_calendar(session)
        assert len(entries) > 0

    def test_view_calendar_filter_platform(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        cal_mod.generate_calendar(session, platform="instagram", niche="fitness", weeks=1)
        tiktok_entries = cal_mod.view_calendar(session, platform="tiktok")
        insta_entries = cal_mod.view_calendar(session, platform="instagram")
        assert all(e["platform"] == "tiktok" for e in tiktok_entries)
        assert all(e["platform"] == "instagram" for e in insta_entries)

    def test_add_calendar_entry(self, session):
        result = cal_mod.add_calendar_entry(
            session,
            date="2025-01-15",
            platform="tiktok",
            content_type="trending_repost",
            title="Viral fitness clip",
        )
        assert result["date"] == "2025-01-15"
        assert result["status"] == "planned"

    def test_add_invalid_content_type_raises(self, session):
        with pytest.raises(ValueError, match="Unknown content type"):
            cal_mod.add_calendar_entry(session, date="2025-01-15", platform="tiktok", content_type="invalid_type", title="test")

    def test_update_status(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        entries = cal_mod.view_calendar(session)
        entry_id = entries[0]["id"]
        result = cal_mod.update_entry_status(session, entry_id=entry_id, status="posted")
        assert result["status"] == "posted"
        assert "posted_at" in result

    def test_update_status_invalid_raises(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        entries = cal_mod.view_calendar(session)
        entry_id = entries[0]["id"]
        with pytest.raises(ValueError, match="Invalid status"):
            cal_mod.update_entry_status(session, entry_id=entry_id, status="deleted")

    def test_update_status_not_found_raises(self, session):
        with pytest.raises(ValueError, match="not found"):
            cal_mod.update_entry_status(session, entry_id="badid", status="posted")

    def test_export_json(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        result = cal_mod.export_calendar(session, fmt="json")
        assert result["format"] == "json"
        assert "entries" in result

    def test_export_csv(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        result = cal_mod.export_calendar(session, fmt="csv")
        assert result["format"] == "csv"
        assert "id,date" in result["content"]

    def test_export_text(self, session):
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        result = cal_mod.export_calendar(session, fmt="text")
        assert result["format"] == "text"
        assert "===" in result["content"]

    def test_export_invalid_format_raises(self, session):
        with pytest.raises(ValueError, match="Unknown format"):
            cal_mod.export_calendar(session, fmt="xml")

    def test_calendar_entry_has_hashtags_when_set_exists(self, session):
        from cli_anything.social_trends.core import hashtags as hashtags_mod
        hashtags_mod.generate_hashtag_set(session, niche="fitness", platform="tiktok")
        cal_mod.generate_calendar(session, platform="tiktok", niche="fitness", weeks=1)
        entries = cal_mod.view_calendar(session, platform="tiktok")
        assert any(e.get("hashtags") for e in entries)

    def test_content_types_list(self):
        assert "trending_repost" in cal_mod.CONTENT_TYPES
        assert "tutorial" in cal_mod.CONTENT_TYPES
        assert "motivation_quote" in cal_mod.CONTENT_TYPES


# ── Trends core tests (without network) ──────────────────────────────────────

class TestTrendsCore:
    def test_list_cached_empty(self, session):
        from cli_anything.social_trends.core import trends as trends_mod
        result = trends_mod.list_cached_trends(session)
        assert result == []

    def test_list_cached_with_data(self, session_with_trends):
        from cli_anything.social_trends.core import trends as trends_mod
        result = trends_mod.list_cached_trends(session_with_trends)
        assert len(result) == 3
        assert result[0]["view_count"] >= result[1]["view_count"]

    def test_list_cached_filter_platform(self, session_with_trends):
        from cli_anything.social_trends.core import trends as trends_mod
        yt = trends_mod.list_cached_trends(session_with_trends, platform="youtube")
        tt = trends_mod.list_cached_trends(session_with_trends, platform="tiktok")
        assert all(t["platform"] == "youtube" for t in yt)
        assert all(t["platform"] == "tiktok" for t in tt)

    def test_search_trends(self, session_with_trends):
        from cli_anything.social_trends.core import trends as trends_mod
        results = trends_mod.search_trends(session_with_trends, query="fitness")
        assert len(results) >= 1
        assert all("fitness" in r["title"].lower() or "fitness" in r["description"].lower() or "fitness" in " ".join(r.get("hashtags", [])).lower() for r in results)

    def test_top_trends(self, session_with_trends):
        from cli_anything.social_trends.core import trends as trends_mod
        top = trends_mod.get_top_trends(session_with_trends, n=2)
        assert len(top) == 2
        assert top[0]["view_count"] >= top[1]["view_count"]

    def test_extract_hashtags_frequency(self, session_with_trends):
        from cli_anything.social_trends.core import trends as trends_mod
        tags = trends_mod.extract_trend_hashtags(session_with_trends)
        # #fitness appears in 2 videos, #gym appears in 2
        tag_names = [t["tag"] for t in tags]
        assert "fitness" in tag_names or "#fitness" in tag_names
        fitness_data = next((t for t in tags if t["tag"] in ("fitness", "#fitness")), None)
        assert fitness_data is not None
        assert fitness_data["frequency"] >= 2


# ── Music core tests (without network) ───────────────────────────────────────

class TestMusicCore:
    def test_list_music_empty(self, session):
        result = music_mod.list_music(session)
        assert result == []

    def test_search_music_empty(self, session):
        result = music_mod.search_music(session, query="pop")
        assert result == []

    def test_recommend_music_empty_cache(self, session):
        result = music_mod.recommend_music(session, niche="fitness", platform="tiktok")
        assert result == []

    def test_music_cached_after_fetch_youtube_music(self, session):
        from cli_anything.social_trends.core.music import _fetch_youtube_trending_music, _cache_music
        tracks = _fetch_youtube_trending_music(limit=5)
        assert len(tracks) <= 5
        _cache_music(session.get_project(), tracks)
        result = music_mod.list_music(session)
        assert len(result) <= 5

    def test_recommend_music_with_cached_data(self, session):
        from cli_anything.social_trends.core.music import _fetch_youtube_trending_music, _cache_music
        tracks = _fetch_youtube_trending_music(limit=8)
        for t in tracks:
            t["platform"] = "youtube"
        _cache_music(session.get_project(), tracks)
        result = music_mod.recommend_music(session, niche="fitness", platform="youtube", n=3)
        assert isinstance(result, list)
