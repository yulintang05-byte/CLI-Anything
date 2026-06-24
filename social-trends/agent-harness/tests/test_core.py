"""Unit tests for cli-anything-social-trends core modules.

All tests use synthetic data — no network calls, no API keys required.
Tests cover: optimizer, theme_pages, and the data-normalization logic
inside youtube.py and tiktok.py.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_trends.core import optimizer as opt
from cli_anything.social_trends.core import theme_pages as theme
from cli_anything.social_trends.core import youtube as yt
from cli_anything.social_trends.core import tiktok as tt


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_video(platform="tiktok", views=100000, likes=5000, comments=200, shares=100):
    return {
        "id": "abc123",
        "platform": platform,
        "title": "Test video",
        "description": "#fitness #workout #gym",
        "views": views,
        "likes": likes,
        "comments": comments,
        "shares": shares,
        "hashtags": ["fitness", "workout", "gym"],
        "music_id": "m001",
        "music_title": "Trending Song",
        "music_author": "Artist",
    }


def make_hashtag_list(platform="tiktok"):
    return [
        {"tag": "#fitness", "count": 20, "platform": platform},
        {"tag": "#workout", "count": 15, "platform": platform},
        {"tag": "#gym", "count": 10, "platform": platform},
        {"tag": "#motivation", "count": 8, "platform": platform},
        {"tag": "#viral", "count": 50, "platform": platform},
        {"tag": "#travel", "count": 5, "platform": platform},
        {"tag": "#food", "count": 3, "platform": platform},
    ]


# ── Optimizer: score_viral_potential ─────────────────────────────────────────

class TestScoreViralPotential:
    def test_returns_sorted_list(self):
        videos = [
            make_video(views=1000, likes=10, shares=1),
            make_video(views=1000, likes=500, shares=100),
        ]
        scored = opt.score_viral_potential(videos)
        assert len(scored) == 2
        assert scored[0]["viral_score"] >= scored[1]["viral_score"]

    def test_viral_score_fields_present(self):
        videos = [make_video()]
        scored = opt.score_viral_potential(videos)
        assert "viral_score" in scored[0]
        assert "engagement_rate_pct" in scored[0]
        assert "share_ratio" in scored[0]

    def test_zero_views_handled(self):
        video = make_video(views=0)
        scored = opt.score_viral_potential([video])
        assert scored[0]["viral_score"] >= 0

    def test_viral_score_nonnegative(self):
        video = make_video(views=10000, likes=0, comments=0, shares=0)
        scored = opt.score_viral_potential([video])
        assert scored[0]["viral_score"] >= 0

    def test_high_share_ratio_boosts_score(self):
        low_shares = make_video(views=100000, likes=5000, shares=100)
        high_shares = make_video(views=100000, likes=5000, shares=5000)
        scored = opt.score_viral_potential([low_shares, high_shares])
        assert scored[0]["viral_score"] > scored[1]["viral_score"]

    def test_empty_list(self):
        result = opt.score_viral_potential([])
        assert result == []

    def test_preserves_original_fields(self):
        video = make_video()
        video["custom_field"] = "kept"
        scored = opt.score_viral_potential([video])
        assert scored[0]["custom_field"] == "kept"


# ── Optimizer: analyze_hashtag_opportunity ────────────────────────────────────

class TestAnalyzeHashtagOpportunity:
    def test_returns_recommendations(self):
        tags = make_hashtag_list()
        result = opt.analyze_hashtag_opportunity(tags, ["fitness"])
        assert "top_recommendations" in result
        assert "suggested_set" in result
        assert "strategy" in result

    def test_niche_relevance_boosts_score(self):
        tags = make_hashtag_list()
        result = opt.analyze_hashtag_opportunity(tags, ["fitness"])
        top = result["top_recommendations"]
        # #fitness should rank higher than #travel due to niche match
        fitness_rank = next((i for i, h in enumerate(top) if h["tag"] == "#fitness"), 99)
        travel_rank = next((i for i, h in enumerate(top) if h["tag"] == "#travel"), 99)
        assert fitness_rank < travel_rank

    def test_empty_tags(self):
        result = opt.analyze_hashtag_opportunity([], ["fitness"])
        assert result["recommendations"] == []

    def test_suggested_set_max_5(self):
        tags = make_hashtag_list()
        result = opt.analyze_hashtag_opportunity(tags, ["fitness"])
        assert len(result["suggested_set"]) <= 5

    def test_tier_classification(self):
        tags = [
            {"tag": "#mega", "count": 100, "platform": "tiktok"},
            {"tag": "#micro", "count": 1, "platform": "tiktok"},
        ]
        result = opt.analyze_hashtag_opportunity(tags, [])
        tiers = {h["tag"]: h["tier"] for h in result["top_recommendations"]}
        assert tiers.get("#micro") == "micro"


# ── Optimizer: get_posting_schedule ──────────────────────────────────────────

class TestGetPostingSchedule:
    def test_tiktok_schedule(self):
        result = opt.get_posting_schedule(["tiktok"])
        assert "tiktok" in result["posting_schedule"]
        sched = result["posting_schedule"]["tiktok"]
        assert "best_days" in sched
        assert "best_hours_utc" in sched
        assert "cadence" in sched

    def test_youtube_schedule(self):
        result = opt.get_posting_schedule(["youtube"])
        assert "youtube" in result["posting_schedule"]

    def test_timezone_adjustment(self):
        result = opt.get_posting_schedule(["tiktok"], timezone_offset=-5)
        sched = result["posting_schedule"]["tiktok"]
        assert "best_hours_local" in sched
        assert "timezone_offset" in sched
        assert sched["timezone_offset"] == "UTC-5"

    def test_unknown_platform_ignored(self):
        result = opt.get_posting_schedule(["twitter"])
        assert result["posting_schedule"] == {}

    def test_multiple_platforms(self):
        result = opt.get_posting_schedule(["tiktok", "youtube", "instagram"])
        assert "tiktok" in result["posting_schedule"]
        assert "youtube" in result["posting_schedule"]
        assert "instagram" in result["posting_schedule"]


# ── Optimizer: get_content_strategy ──────────────────────────────────────────

class TestGetContentStrategy:
    def test_structure(self):
        result = opt.get_content_strategy(["tiktok"], niche="fitness")
        assert "platform_strategies" in result
        assert "tiktok" in result["platform_strategies"]
        assert "niche_tips" in result
        assert len(result["niche_tips"]) > 0

    def test_fitness_niche_tips(self):
        result = opt.get_content_strategy(["tiktok"], niche="fitness")
        tips = result["niche_tips"]
        assert any("challenge" in t.lower() or "transformation" in t.lower() for t in tips)

    def test_generic_niche_fallback(self):
        result = opt.get_content_strategy(["tiktok"], niche="beekeeping")
        assert len(result["niche_tips"]) > 0

    def test_follower_tiers(self):
        for tier in ["micro", "mid", "macro", "mega"]:
            result = opt.get_content_strategy(["youtube"], niche="tech", follower_tier=tier)
            assert "platform_strategies" in result


# ── Optimizer: get_optimization_report ───────────────────────────────────────

class TestGetOptimizationReport:
    def test_full_report_structure(self):
        result = opt.get_optimization_report(
            platforms=["tiktok", "youtube"],
            niche="fitness",
            region="US",
        )
        assert "account_summary" in result
        assert "posting_schedule" in result
        assert "content_strategy" in result
        assert "niche_tips" in result
        assert "quick_wins" in result

    def test_with_hashtag_data(self):
        tags = make_hashtag_list()
        result = opt.get_optimization_report(
            platforms=["tiktok"],
            niche="fitness",
            trending_hashtags=tags,
            niche_keywords=["fitness"],
        )
        assert "hashtag_report" in result
        assert len(result["hashtag_report"]) > 0

    def test_quick_wins_list(self):
        result = opt.get_optimization_report(platforms=["tiktok"], niche="cooking")
        assert isinstance(result["quick_wins"], list)
        assert len(result["quick_wins"]) >= 3


# ── Theme pages: evaluate_niche ───────────────────────────────────────────────

class TestEvaluateNiche:
    def test_known_niche_fitness(self):
        result = theme.evaluate_niche("fitness")
        assert result["found"] is True
        assert "monetization_paths" in result
        assert "difficulty" in result

    def test_known_niche_finance(self):
        result = theme.evaluate_niche("finance")
        assert result["found"] is True
        assert result["monetization_ceiling"] == "very_high"

    def test_known_niche_luxury(self):
        result = theme.evaluate_niche("luxury")
        assert result["found"] is True

    def test_unknown_niche_fallback(self):
        result = theme.evaluate_niche("extreme ironing")
        assert result["found"] is False
        assert "recommendations" in result

    def test_case_insensitive(self):
        r1 = theme.evaluate_niche("FITNESS")
        r2 = theme.evaluate_niche("fitness")
        assert r1["found"] == r2["found"]


# ── Theme pages: get_monetization_playbook ───────────────────────────────────

class TestGetMonetizationPlaybook:
    def test_shoutouts_playbook(self):
        result = theme.get_monetization_playbook("shoutouts")
        assert "pricing_guide" in result
        assert "when_to_start" in result
        assert "tips" in result

    def test_affiliate_marketing(self):
        result = theme.get_monetization_playbook("affiliate_marketing")
        assert "top_programs" in result

    def test_digital_products(self):
        result = theme.get_monetization_playbook("digital_products")
        assert "product_ideas" in result

    def test_page_flipping(self):
        result = theme.get_monetization_playbook("page_flipping")
        assert "valuation_formula" in result
        assert "where_to_sell" in result

    def test_brand_deals(self):
        result = theme.get_monetization_playbook("brand_deals")
        assert "rate_guide" in result
        assert "how_to_land" in result

    def test_unknown_strategy_raises(self):
        with pytest.raises(ValueError, match="Unknown strategy"):
            theme.get_monetization_playbook("unknown_strategy")


# ── Theme pages: get_content_calendar ────────────────────────────────────────

class TestGetContentCalendar:
    def test_7_day_template(self):
        result = theme.get_content_calendar("7_day_theme_page")
        assert "calendar" in result
        cal = result["calendar"]
        assert "day_1" in cal
        assert "day_7" in cal

    def test_30_day_template(self):
        result = theme.get_content_calendar("30_day_growth_sprint")
        assert "calendar" in result
        cal = result["calendar"]
        assert "week_1" in cal
        assert "week_4" in cal
        assert "kpis" in cal

    def test_unknown_template_raises(self):
        with pytest.raises(ValueError, match="Unknown template"):
            theme.get_content_calendar("999_day_template")


# ── Theme pages: get_page_setup_checklist ─────────────────────────────────────

class TestGetPageSetupChecklist:
    def test_tiktok_checklist(self):
        result = theme.get_page_setup_checklist("tiktok", "fitness")
        assert "universal_checklist" in result
        assert "platform_checklist" in result
        assert "monetization_unlock_milestones" in result
        assert len(result["platform_checklist"]) > 0

    def test_youtube_checklist(self):
        result = theme.get_page_setup_checklist("youtube", "tech")
        assert any("banner" in item.lower() for item in result["platform_checklist"])

    def test_instagram_checklist(self):
        result = theme.get_page_setup_checklist("instagram", "beauty")
        assert any("reel" in item.lower() or "highlight" in item.lower()
                   for item in result["platform_checklist"])

    def test_milestones_present(self):
        result = theme.get_page_setup_checklist("tiktok", "finance")
        milestones = result["monetization_unlock_milestones"]
        assert "1K_followers" in milestones
        assert "10K_followers" in milestones

    def test_first_30_days_plan(self):
        result = theme.get_page_setup_checklist("tiktok", "cooking")
        plan = result.get("first_30_days_content_plan", [])
        assert len(plan) >= 5


# ── Theme pages: get_full_theme_page_guide ───────────────────────────────────

class TestGetFullThemePageGuide:
    def test_full_guide_structure(self):
        result = theme.get_full_theme_page_guide("fitness", "tiktok")
        assert "guide_title" in result
        assert "niche_evaluation" in result
        assert "page_setup_checklist" in result
        assert "week_1_content_calendar" in result
        assert "30_day_growth_sprint" in result
        assert "conversion_optimization" in result

    def test_conversion_fields(self):
        result = theme.get_full_theme_page_guide("luxury", "instagram")
        conv = result["conversion_optimization"]
        assert "bio_cta" in conv
        assert "email_capture" in conv

    def test_monetization_playbook_included(self):
        result = theme.get_full_theme_page_guide("finance", "youtube", "brand_deals")
        assert "rate_guide" in result.get("monetization_playbook", {})


# ── Theme pages: list functions ───────────────────────────────────────────────

class TestListFunctions:
    def test_list_niches(self):
        result = theme.list_available_niches()
        assert "available_niches" in result
        assert result["total"] > 0
        for n in result["available_niches"]:
            assert "key" in n
            assert "difficulty" in n
            assert "monetization_ceiling" in n

    def test_list_strategies(self):
        result = theme.list_monetization_strategies()
        assert "strategies" in result
        assert result["total"] > 0
        keys = [s["key"] for s in result["strategies"]]
        assert "shoutouts" in keys
        assert "affiliate_marketing" in keys
        assert "page_flipping" in keys


# ── YouTube: normalization ────────────────────────────────────────────────────

class TestYouTubeNormalization:
    def test_normalize_video(self):
        raw = {
            "id": "vid001",
            "snippet": {
                "title": "Test Video",
                "channelTitle": "Test Channel",
                "channelId": "UCtest",
                "publishedAt": "2025-01-01T00:00:00Z",
                "description": "A test video #fitness #gym",
                "tags": ["fitness", "workout"],
                "categoryId": "26",
                "thumbnails": {"high": {"url": "https://example.com/thumb.jpg"}},
            },
            "statistics": {
                "viewCount": "100000",
                "likeCount": "5000",
                "commentCount": "200",
            },
            "contentDetails": {"duration": "PT5M30S"},
        }
        result = yt._normalize_video(raw)
        assert result["id"] == "vid001"
        assert result["platform"] == "youtube"
        assert result["views"] == 100000
        assert result["likes"] == 5000
        assert result["comments"] == 200
        assert "youtube.com" in result["url"]
        assert result["tags"] == ["fitness", "workout"]

    def test_normalize_video_missing_stats(self):
        raw = {
            "id": "vid002",
            "snippet": {"title": "No stats video"},
            "statistics": {},
            "contentDetails": {},
        }
        result = yt._normalize_video(raw)
        assert result["views"] == 0
        assert result["likes"] == 0

    def test_description_truncated_to_300(self):
        long_desc = "x" * 500
        raw = {
            "id": "vid003",
            "snippet": {"description": long_desc},
            "statistics": {},
            "contentDetails": {},
        }
        result = yt._normalize_video(raw)
        assert len(result["description"]) <= 300


# ── TikTok: normalization ─────────────────────────────────────────────────────

class TestTikTokNormalization:
    def test_normalize_research_video(self):
        raw = {
            "id": 12345678,
            "video_description": "Workout #fitness #gym",
            "create_time": 1700000000,
            "author_info": {"display_name": "fitness_pro", "sec_uid": "uid001"},
            "view_count": 500000,
            "like_count": 20000,
            "comment_count": 1000,
            "share_count": 500,
            "hashtag_info_list": [{"name": "fitness"}, {"name": "gym"}],
            "music_info": {"id": 987, "title": "Trending Track", "author": "DJ Test"},
            "duration": 30,
        }
        result = tt._normalize_research_video(raw)
        assert result["id"] == "12345678"
        assert result["platform"] == "tiktok"
        assert result["views"] == 500000
        assert result["hashtags"] == ["fitness", "gym"]
        assert result["music_title"] == "Trending Track"
        assert "tiktok.com" in result["url"]

    def test_normalize_scraped_video(self):
        raw = {
            "id": "tt_001",
            "desc": "Check this out #viral #trending",
            "createTime": 1700000000,
            "author": {"nickname": "creator1", "id": "u1", "uniqueId": "creator1"},
            "stats": {
                "playCount": 1000000,
                "diggCount": 50000,
                "commentCount": 2000,
                "shareCount": 1000,
            },
            "music": {"id": "m1", "title": "Hit Song", "authorName": "Artist"},
            "video": {"duration": 15},
        }
        result = tt._normalize_scraped_video(raw)
        assert result["id"] == "tt_001"
        assert result["platform"] == "tiktok"
        assert result["views"] == 1000000
        assert "viral" in result["hashtags"]
        assert "trending" in result["hashtags"]

    def test_scraped_hashtag_extraction(self):
        raw = {
            "id": "tt_002",
            "desc": "#python #coding #100daysofcode",
            "author": {"nickname": "coder", "uniqueId": "coder"},
            "stats": {},
            "music": {},
            "video": {},
        }
        result = tt._normalize_scraped_video(raw)
        assert set(result["hashtags"]) == {"python", "coding", "100daysofcode"}
