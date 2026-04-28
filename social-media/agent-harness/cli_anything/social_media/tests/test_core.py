"""Unit tests for social-media CLI core modules (no network required)."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../.."))

from cli_anything.social_media.core.session import Session
from cli_anything.social_media.core import trend_analyzer as analyzer
from cli_anything.social_media.core import account_optimizer as optimizer
from cli_anything.social_media.core import theme_page as theme
from cli_anything.social_media.core.youtube_scraper import (
    extract_hashtags_from_videos,
    _parse_renderer,
)
from cli_anything.social_media.core.tiktok_scraper import (
    _get_known_viral_hashtags_2026,
    scrape_trending_hashtags,
)
from cli_anything.social_media.core.trend_analyzer import (
    score_hashtag,
    _parse_view_string,
    merge_platform_trends,
    generate_content_calendar,
    _hook_template,
)


# ---------------------------------------------------------------------------
# Session tests
# ---------------------------------------------------------------------------

class TestSession:
    def test_new_session_has_no_workspace(self):
        sess = Session()
        assert not sess.has_workspace()

    def test_set_and_get_workspace(self):
        sess = Session()
        ws = {"name": "test", "accounts": []}
        sess.set_workspace(ws)
        assert sess.has_workspace()
        assert sess.get_workspace()["name"] == "test"

    def test_snapshot_and_undo(self):
        sess = Session()
        sess.set_workspace({"value": 1})
        sess.snapshot("initial")
        sess.get_workspace()["value"] = 2
        desc = sess.undo()
        assert sess.get_workspace()["value"] == 1

    def test_undo_redo_cycle(self):
        sess = Session()
        sess.set_workspace({"x": 0})
        sess.snapshot("step0")
        sess.get_workspace()["x"] = 1
        sess.snapshot("step1")
        sess.get_workspace()["x"] = 2
        sess.undo()
        assert sess.get_workspace()["x"] == 1
        sess.undo()
        assert sess.get_workspace()["x"] == 0
        sess.redo()
        assert sess.get_workspace()["x"] == 1

    def test_undo_raises_when_empty(self):
        sess = Session()
        sess.set_workspace({"x": 1})
        with pytest.raises(RuntimeError):
            sess.undo()

    def test_redo_raises_when_empty(self):
        sess = Session()
        sess.set_workspace({"x": 1})
        with pytest.raises(RuntimeError):
            sess.redo()

    def test_get_workspace_raises_when_none(self):
        sess = Session()
        with pytest.raises(RuntimeError):
            sess.get_workspace()

    def test_save_and_load(self, tmp_path):
        sess = Session()
        ws = {"name": "saved_test", "data": [1, 2, 3]}
        sess.set_workspace(ws)
        path = str(tmp_path / "test_workspace.json")
        sess.save(path)
        sess2 = Session()
        loaded = sess2.load(path)
        assert loaded["name"] == "saved_test"
        assert loaded["data"] == [1, 2, 3]

    def test_status(self):
        sess = Session()
        status = sess.status()
        assert "has_workspace" in status
        assert "modified" in status
        assert status["has_workspace"] is False

    def test_modified_flag(self):
        sess = Session()
        sess.set_workspace({"x": 1})
        assert not sess.modified
        sess.snapshot("test")
        assert sess.modified

    def test_max_undo_limit(self):
        sess = Session()
        sess.set_workspace({"x": 0})
        for i in range(60):
            sess.snapshot(f"snap{i}")
        assert len(sess._undo_stack) <= Session.MAX_UNDO


# ---------------------------------------------------------------------------
# YouTube scraper tests (no network)
# ---------------------------------------------------------------------------

class TestYouTubeScraper:
    def test_extract_hashtags_from_videos(self):
        videos = [
            {"hashtags": ["fitness", "workout"]},
            {"hashtags": ["fitness", "health"]},
            {"hashtags": ["workout", "gym"]},
        ]
        result = extract_hashtags_from_videos(videos)
        assert len(result) > 0
        tags = [r["hashtag"] for r in result]
        assert "#fitness" in tags
        # fitness appears twice so should rank highest
        assert result[0]["hashtag"] in ("#fitness", "#workout")

    def test_extract_hashtags_deduplicates(self):
        videos = [
            {"hashtags": ["test", "test", "test"]},
        ]
        result = extract_hashtags_from_videos(videos)
        hashtags = [r["hashtag"] for r in result]
        assert hashtags.count("#test") == 1

    def test_extract_hashtags_empty(self):
        result = extract_hashtags_from_videos([])
        assert result == []

    def test_extract_hashtags_virality_score_capped(self):
        videos = [{"hashtags": ["mega"]} for _ in range(20)]
        result = extract_hashtags_from_videos(videos)
        assert result[0]["virality_score"] <= 100

    def test_parse_renderer_missing_fields(self):
        result = _parse_renderer({})
        # should not crash, may return None or empty dict
        assert result is None or isinstance(result, dict)

    def test_parse_renderer_full(self):
        renderer = {
            "videoId": "abc123",
            "title": {"runs": [{"text": "How to #fitness workout"}]},
            "ownerText": {"runs": [{"text": "FitChannel"}]},
            "viewCountText": {"simpleText": "1.2M views"},
            "publishedTimeText": {"simpleText": "2 days ago"},
        }
        result = _parse_renderer(renderer)
        assert result is not None
        assert result["video_id"] == "abc123"
        assert result["title"] == "How to #fitness workout"
        assert result["channel"] == "FitChannel"
        assert "fitness" in result["hashtags"]

    def test_hashtag_extraction_returns_ranked_list(self):
        videos = [{"hashtags": ["alpha", "beta"]}, {"hashtags": ["alpha"]}]
        result = extract_hashtags_from_videos(videos)
        tags = [r["hashtag"] for r in result]
        assert "#alpha" in tags
        assert result[0]["hashtag"] == "#alpha"  # most frequent first


# ---------------------------------------------------------------------------
# TikTok scraper tests (no network)
# ---------------------------------------------------------------------------

class TestTikTokScraper:
    def test_known_viral_hashtags_returns_list(self):
        result = _get_known_viral_hashtags_2026()
        assert isinstance(result, list)
        assert len(result) >= 10

    def test_known_viral_hashtags_have_required_fields(self):
        result = _get_known_viral_hashtags_2026()
        for item in result:
            assert "hashtag" in item
            assert item["hashtag"].startswith("#")
            assert "category" in item

    def test_scrape_trending_no_network_returns_curated(self):
        # live=False falls back to curated list only
        result = scrape_trending_hashtags(live=False)
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0
        assert result["platform"] == "tiktok"

    def test_scrape_trending_niche_filter(self):
        result = scrape_trending_hashtags(live=False, niche="fitness")
        assert "hashtags" in result
        # Should return some fitness-related hashtags
        for h in result["hashtags"]:
            assert (
                "fitness" in h.get("hashtag", "").lower()
                or "fitness" in h.get("category", "").lower()
            )

    def test_scrape_trending_limit(self):
        result = scrape_trending_hashtags(live=False, limit=5)
        assert len(result["hashtags"]) <= 5

    def test_scrape_trending_has_metadata(self):
        result = scrape_trending_hashtags(live=False)
        assert "scraped_at" in result
        assert "method" in result
        assert "total" in result


# ---------------------------------------------------------------------------
# Trend analyzer tests
# ---------------------------------------------------------------------------

class TestTrendAnalyzer:
    def test_score_hashtag_cross_platform(self):
        score = score_hashtag("fitness", yt_count=3, tt_count=2)
        assert score > 40  # cross-platform bonus

    def test_score_hashtag_yt_only(self):
        score = score_hashtag("workout", yt_count=5, tt_count=0)
        assert 0 < score <= 50

    def test_score_hashtag_tt_only(self):
        score = score_hashtag("fyp", yt_count=0, tt_count=1, tt_views_str="900B+")
        assert score > 10

    def test_score_hashtag_zero(self):
        score = score_hashtag("nonexistent", yt_count=0, tt_count=0)
        assert score == 0

    def test_score_hashtag_capped_at_100(self):
        score = score_hashtag("viral", yt_count=100, tt_count=100, tt_views_str="900B+")
        assert score <= 100

    def test_parse_view_string_billions(self):
        assert _parse_view_string("1B+") == 1_000_000_000
        assert _parse_view_string("900B+") == 900_000_000_000

    def test_parse_view_string_millions(self):
        assert _parse_view_string("1.5M") == 1_500_000

    def test_parse_view_string_thousands(self):
        assert _parse_view_string("50K") == 50_000

    def test_parse_view_string_invalid(self):
        assert _parse_view_string("unknown") == 0

    def test_merge_platform_trends_structure(self):
        yt_data = {
            "videos": [
                {"hashtags": ["fitness", "workout"]},
                {"hashtags": ["fitness", "health"]},
            ],
            "top_hashtags": [
                {"tag": "#fitness", "count": 2},
            ],
        }
        tt_data = {
            "hashtags": [
                {"hashtag": "#fitness", "category": "health", "avg_views": "100B+", "type": "niche"},
                {"hashtag": "#fyp", "category": "reach", "avg_views": "900B+", "type": "discovery"},
            ],
            "trending_sounds": [],
        }
        merged = merge_platform_trends(yt_data, tt_data)
        assert "top_hashtags" in merged
        assert "cross_platform_hits" in merged
        assert "recommended_hashtag_mix" in merged
        assert "content_signals" in merged

    def test_merge_returns_cross_platform_hits(self):
        yt_data = {
            "videos": [{"hashtags": ["fitness"]}],
            "top_hashtags": [{"tag": "#fitness", "count": 1}],
        }
        tt_data = {
            "hashtags": [{"hashtag": "#fitness", "category": "health", "avg_views": "", "type": "niche"}],
            "trending_sounds": [],
        }
        merged = merge_platform_trends(yt_data, tt_data)
        cross = merged["cross_platform_hits"]
        assert any(h["hashtag"] == "#fitness" for h in cross)

    def test_content_calendar_structure(self):
        cal = generate_content_calendar("fitness", ["tiktok"], posts_per_week=3, weeks=2)
        assert "calendar" in cal
        assert len(cal["calendar"]) == 6  # 3 posts * 2 weeks
        for entry in cal["calendar"]:
            assert "day" in entry
            assert "format" in entry
            assert "hook_template" in entry

    def test_content_calendar_niche_in_hook(self):
        cal = generate_content_calendar("finance", ["tiktok"], posts_per_week=2, weeks=1)
        for entry in cal["calendar"]:
            assert "finance" in entry["hook_template"].lower()

    def test_hook_template_all_formats(self):
        formats = ["tutorial", "storytime", "listicle", "motivational", "product-review",
                   "educational", "challenge", "transformation", "day-in-life", "reaction"]
        for fmt in formats:
            result = _hook_template(fmt, "fitness")
            assert isinstance(result, str)
            assert len(result) > 10


# ---------------------------------------------------------------------------
# Account optimizer tests
# ---------------------------------------------------------------------------

class TestAccountOptimizer:
    def test_audit_basic_structure(self):
        result = optimizer.audit_account(
            platform="tiktok",
            username="testuser",
            followers=10000,
            avg_views=3000,
            avg_likes=200,
            avg_comments=50,
            avg_shares=30,
            avg_saves=100,
            posts_per_week=4,
            niche="fitness",
            bio_has_cta=True,
            has_link_in_bio=True,
        )
        assert "health_score" in result
        assert "grade" in result
        assert "issues" in result
        assert "recommendations" in result
        assert "strengths" in result
        assert 0 <= result["health_score"] <= 100

    def test_audit_score_higher_with_good_metrics(self):
        good = optimizer.audit_account(
            platform="tiktok",
            username="good",
            followers=10000,
            avg_views=5000,
            avg_likes=400,
            avg_comments=100,
            avg_shares=50,
            avg_saves=200,
            posts_per_week=4,
            niche="fitness",
            bio_has_cta=True,
            has_link_in_bio=True,
        )
        bad = optimizer.audit_account(
            platform="tiktok",
            username="bad",
            followers=10000,
            avg_views=100,
            avg_likes=5,
            avg_comments=1,
            avg_shares=0,
            avg_saves=0,
            posts_per_week=1,
            niche="",
            bio_has_cta=False,
            has_link_in_bio=False,
        )
        assert good["health_score"] > bad["health_score"]

    def test_audit_critical_issue_when_not_posting(self):
        result = optimizer.audit_account(
            platform="tiktok",
            username="inactive",
            followers=5000,
            avg_views=0,
            posts_per_week=0,
            niche="",
        )
        critical = [i for i in result["issues"] if i["priority"] == "critical"]
        assert len(critical) > 0

    def test_audit_grade_mapping(self):
        assert optimizer._score_to_grade(85) == "A - Optimized"
        assert optimizer._score_to_grade(65) == "B - Good"
        assert optimizer._score_to_grade(45) == "C - Needs Work"
        assert optimizer._score_to_grade(25) == "D - Underperforming"
        assert optimizer._score_to_grade(5) == "F - Critical Issues"

    def test_audit_all_platforms(self):
        platforms = ["tiktok", "youtube_shorts", "youtube_long", "instagram_reels"]
        for platform in platforms:
            result = optimizer.audit_account(
                platform=platform,
                username="test",
                followers=1000,
                avg_views=200,
            )
            assert "health_score" in result

    def test_audit_has_posting_times(self):
        result = optimizer.audit_account(
            platform="tiktok",
            username="test",
        )
        assert "posting_times" in result

    def test_bulk_optimize(self):
        accounts = [
            {"platform": "tiktok", "username": "acc1", "followers": 10000, "avg_views": 2000, "niche": "fitness"},
            {"platform": "tiktok", "username": "acc2", "followers": 5000, "avg_views": 500, "niche": ""},
        ]
        result = optimizer.bulk_optimize_accounts(accounts)
        assert "accounts_audited" in result
        assert result["accounts_audited"] == 2
        assert "portfolio_avg_score" in result
        assert "results" in result


# ---------------------------------------------------------------------------
# Theme page tests
# ---------------------------------------------------------------------------

class TestThemePage:
    def test_create_plan_structure(self):
        result = theme.create_theme_page_plan(
            niche="finance",
            archetype="educator",
            platforms=["tiktok", "youtube_shorts"],
        )
        assert "niche_analysis" in result
        assert "90_day_roadmap" in result
        assert "conversion_funnel" in result
        assert "content_pillars" in result
        assert "account_setup_checklist" in result
        assert "top_hashtags" in result

    def test_create_plan_90_day_roadmap_has_4_phases(self):
        result = theme.create_theme_page_plan(niche="fitness", archetype="curator")
        assert len(result["90_day_roadmap"]) == 4

    def test_create_plan_content_pillars_has_4(self):
        result = theme.create_theme_page_plan(niche="beauty", archetype="product_reviewer")
        assert len(result["content_pillars"]) == 4

    def test_create_plan_monetization_score_valid(self):
        result = theme.create_theme_page_plan(niche="ai_tools", archetype="educator")
        score = result["niche_analysis"]["monetization_score"]
        assert 0 <= score <= 100

    def test_niche_list_returns_all_niches(self):
        result = theme.get_niche_list()
        assert "niches" in result
        assert len(result["niches"]) == len(theme.NICHE_DATABASE)

    def test_niche_list_sorted_by_score(self):
        result = theme.get_niche_list()
        scores = [n["monetization_score"] for n in result["niches"]]
        assert scores == sorted(scores, reverse=True)

    def test_conversion_funnel_has_7_stages(self):
        assert len(theme.CONVERSION_FUNNEL_STAGES) == 7

    def test_conversion_funnel_stage_structure(self):
        for stage in theme.CONVERSION_FUNNEL_STAGES:
            assert "stage" in stage
            assert "name" in stage
            assert "goal" in stage
            assert "tactics" in stage
            assert len(stage["tactics"]) >= 2

    def test_all_archetypes_produce_valid_plans(self):
        for archetype in theme.PAGE_ARCHETYPES.keys():
            result = theme.create_theme_page_plan(niche="business", archetype=archetype)
            assert result["archetype"] == archetype
            assert "launch_steps" in result

    def test_unknown_niche_falls_back_gracefully(self):
        result = theme.create_theme_page_plan(niche="underwater_basket_weaving")
        assert "niche_analysis" in result
        assert result["niche_analysis"]["monetization_score"] > 0

    def test_checklist_has_required_items(self):
        result = theme.create_theme_page_plan(niche="finance")
        items = [c["item"] for c in result["account_setup_checklist"]]
        assert "Bio (line 1)" in items
        assert "Link in bio" in items
        assert "Lead magnet" in items
