"""Unit tests for social-trends core modules (no network calls required)."""
import pytest
from unittest.mock import patch, MagicMock

from cli_anything.social.core.youtube_trends    import extract_trending_hashtags, extract_trending_music, _extract_hashtags
from cli_anything.social.core.tiktok_trends     import _fmt_views, _fallback_trending_hashtags, _fallback_trending_sounds, get_tiktok_trends
from cli_anything.social.core.hashtag_analyzer  import build_hashtag_set, cross_platform_trend_merge, generate_hashtag_calendar, PLATFORM_HASHTAG_RULES, NICHE_HASHTAGS
from cli_anything.social.core.music_trends      import get_music_trends, ROYALTY_FREE_SOURCES, TRENDING_GENRES
from cli_anything.social.core.account_optimizer import optimize_account, optimize_all_platforms, generate_content_calendar, POSTING_TIMES
from cli_anything.social.core.theme_page_guide  import get_theme_page_guide, HIGH_CONVERTING_NICHES, GROWTH_PHASES


# ── youtube ───────────────────────────────────────────────────────────────────

class TestYouTubeTrends:
    def test_extract_hashtags_from_text(self):
        tags = _extract_hashtags("Check #fitness and #gym tips #FYP")
        assert "#fitness" in tags
        assert "#gym" in tags
        assert "#FYP" in tags

    def test_extract_hashtags_empty(self):
        assert _extract_hashtags("") == []

    def test_extract_trending_hashtags_frequency(self):
        videos = [
            {"hashtags": ["#fitness", "#gym"]},
            {"hashtags": ["#fitness", "#health"]},
            {"hashtags": ["#fitness"]},
        ]
        result = extract_trending_hashtags(videos, top_n=5)
        assert result[0]["hashtag"] == "#fitness"
        assert result[0]["frequency"] == 3

    def test_extract_trending_hashtags_empty(self):
        assert extract_trending_hashtags([]) == []

    def test_extract_trending_music_filters_correctly(self):
        videos = [
            {"title": "Top 10 Workout Tips", "uploader": "FitGuru", "view_count": 5000, "url": ""},
            {"title": "Espresso Official Music Video", "uploader": "Sabrina", "view_count": 10000000, "url": ""},
            {"title": "Summer Album Audio Release", "uploader": "Artist", "view_count": 2000000, "url": ""},
        ]
        music = extract_trending_music(videos)
        titles = [m["title"] for m in music]
        assert "Espresso Official Music Video" in titles
        assert "Summer Album Audio Release" in titles
        assert "Top 10 Workout Tips" not in titles

    def test_extract_trending_music_empty(self):
        assert extract_trending_music([]) == []


# ── tiktok ────────────────────────────────────────────────────────────────────

class TestTikTokTrends:
    def test_fmt_views_trillion(self):
        assert _fmt_views(7_600_000_000_000) == "7.6T"

    def test_fmt_views_billion(self):
        assert _fmt_views(1_200_000_000) == "1.2B"

    def test_fmt_views_million(self):
        assert _fmt_views(3_500_000) == "3.5M"

    def test_fmt_views_thousand(self):
        assert _fmt_views(45_000) == "45.0K"

    def test_fmt_views_small(self):
        assert _fmt_views(500) == "500"

    def test_fmt_views_none(self):
        assert _fmt_views(None) == "N/A"

    def test_fallback_hashtags_not_empty(self):
        tags = _fallback_trending_hashtags()
        assert len(tags) >= 10
        assert all("hashtag" in t for t in tags)
        assert all(t["hashtag"].startswith("#") for t in tags)

    def test_fallback_sounds_not_empty(self):
        sounds = _fallback_trending_sounds()
        assert len(sounds) >= 5
        assert all("title" in s and "artist" in s for s in sounds)

    @patch("cli_anything.social.core.tiktok_trends.scrape_trending_hashtags")
    @patch("cli_anything.social.core.tiktok_trends.scrape_trending_sounds")
    def test_get_tiktok_trends_structure(self, mock_sounds, mock_hashtags):
        mock_hashtags.return_value = [{"hashtag": "#fyp", "views": "7T", "source": "test"}]
        mock_sounds.return_value   = [{"title": "Test Song", "artist": "Test", "source": "test"}]
        result = get_tiktok_trends()
        assert "hashtags"  in result
        assert "sounds"    in result
        assert "insights"  in result
        assert "count"     in result
        assert result["count"]["hashtags"] == 1
        assert result["count"]["sounds"]   == 1


# ── hashtag analyzer ─────────────────────────────────────────────────────────

class TestHashtagAnalyzer:
    def test_build_hashtag_set_tiktok(self):
        result = build_hashtag_set(niche="fitness", platform="tiktok")
        assert "hashtags" in result
        assert result["platform"] == "tiktok"
        assert len(result["hashtags"]) <= PLATFORM_HASHTAG_RULES["tiktok"]["max"]
        assert all(h.startswith("#") for h in result["hashtags"])

    def test_build_hashtag_set_instagram(self):
        result = build_hashtag_set(niche="fashion", platform="instagram")
        assert result["platform"] == "instagram"
        assert result["count"] <= PLATFORM_HASHTAG_RULES["instagram"]["max"]

    def test_build_hashtag_set_unknown_niche_fallback(self):
        result = build_hashtag_set(niche="unknownniche123", platform="tiktok")
        assert result["hashtags"]  # Falls back to general
        assert result["niche"] == "unknownniche123"

    def test_build_hashtag_set_trending_injection(self):
        result = build_hashtag_set(niche="fitness", platform="tiktok", trending=["#newtrend"])
        assert "#newtrend" in result["hashtags"] or "#newtrend" in result["breakdown"]["trending"]

    def test_build_hashtag_set_count_override(self):
        result = build_hashtag_set(niche="business", platform="instagram", count=3)
        assert len(result["hashtags"]) <= 3

    def test_cross_platform_merge_finds_overlap(self):
        yt_tags = [{"hashtag": "#fitness"}, {"hashtag": "#gym"}, {"hashtag": "#youtube"}]
        tt_tags = [{"hashtag": "#fitness"}, {"hashtag": "#fyp"}, {"hashtag": "#trending"}]
        merged  = cross_platform_trend_merge(yt_tags, tt_tags)
        cross   = [h for h in merged if h.get("cross_platform")]
        single  = [h for h in merged if not h.get("cross_platform")]
        assert any(h["hashtag"] == "#fitness" for h in cross)
        assert any(h["hashtag"] == "#youtube" for h in single)

    def test_cross_platform_merge_no_overlap(self):
        yt_tags = [{"hashtag": "#youtube"}]
        tt_tags = [{"hashtag": "#fyp"}]
        merged  = cross_platform_trend_merge(yt_tags, tt_tags)
        cross   = [h for h in merged if h.get("cross_platform")]
        assert len(cross) == 0

    def test_generate_hashtag_calendar_structure(self):
        calendar = generate_hashtag_calendar(niche="fitness", platforms=["tiktok", "instagram"], days=7)
        assert len(calendar) == 7
        for entry in calendar:
            assert "day" in entry
            assert "tags" in entry
            assert "tiktok" in entry["tags"]
            assert "instagram" in entry["tags"]

    def test_all_niches_have_required_tiers(self):
        for niche, tiers in NICHE_HASHTAGS.items():
            assert "mega" in tiers
            assert "large" in tiers
            assert "medium" in tiers
            assert "niche" in tiers


# ── music trends ──────────────────────────────────────────────────────────────

class TestMusicTrends:
    def test_get_music_trends_structure(self):
        data = get_music_trends()
        assert "trending_tracks"      in data
        assert "trending_genres"      in data
        assert "royalty_free_sources" in data
        assert "strategy"             in data
        assert "action_items"         in data

    def test_get_music_trends_cross_platform_detection(self):
        yt_music  = [{"title": "Espresso", "artist": "Sabrina", "views": 1000000, "url": ""}]
        tt_sounds = [{"title": "Espresso", "artist": "Sabrina", "source": "test"}]
        data      = get_music_trends(yt_music, tt_sounds)
        tracks    = data["trending_tracks"]
        cross     = [t for t in tracks if t.get("cross_platform")]
        assert len(cross) >= 1
        assert "Espresso" in [t["title"] for t in cross]

    def test_royalty_free_sources_populated(self):
        assert len(ROYALTY_FREE_SOURCES) >= 4
        for src in ROYALTY_FREE_SOURCES:
            assert "name" in src
            assert "cost" in src

    def test_trending_genres_populated(self):
        assert len(TRENDING_GENRES) >= 5
        for g in TRENDING_GENRES:
            assert "genre" in g
            assert "platform" in g

    def test_action_items_with_tracks(self):
        data = get_music_trends(
            yt_music_data=[{"title": "BigHit", "artist": "Famous", "views": 5000000, "url": ""}]
        )
        assert len(data["action_items"]) >= 1


# ── account optimizer ─────────────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_optimize_account_structure(self):
        result = optimize_account(platform="tiktok", niche="fitness")
        assert "platform"           in result
        assert "posting_schedule"   in result
        assert "bio_template"       in result
        assert "content_pillars"    in result
        assert "seo_tips"           in result
        assert "growth_tactics"     in result
        assert "quick_wins"         in result

    def test_optimize_account_platforms(self):
        for platform in ["tiktok", "instagram", "youtube", "twitter"]:
            result = optimize_account(platform=platform, niche="business")
            assert result["platform"] == platform

    def test_optimize_all_platforms_covers_all(self):
        results = optimize_all_platforms(niche="fitness")
        assert "tiktok"     in results
        assert "instagram"  in results
        assert "youtube"    in results
        assert "twitter"    in results

    def test_generate_content_calendar_length(self):
        calendar = generate_content_calendar(niche="fitness", platform="tiktok", weeks=2)
        assert len(calendar) == 14  # 2 weeks × 7 days

    def test_generate_content_calendar_structure(self):
        calendar = generate_content_calendar(niche="fashion", platform="instagram", weeks=1)
        for entry in calendar:
            assert "week"  in entry
            assert "day"   in entry
            assert "posts" in entry
            for post in entry["posts"]:
                assert "time"   in post
                assert "pillar" in post
                assert "prompt" in post

    def test_posting_times_all_days(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for platform in ["tiktok", "instagram", "youtube"]:
            times = POSTING_TIMES.get(platform, {})
            for day in days:
                assert day in times, f"Missing {day} for {platform}"


# ── theme page guide ──────────────────────────────────────────────────────────

class TestThemePageGuide:
    def test_guide_structure(self):
        guide = get_theme_page_guide()
        assert "niche_analysis"     in guide
        assert "all_niches"         in guide
        assert "growth_phases"      in guide
        assert "monetization"       in guide
        assert "dm_templates"       in guide
        assert "learning_resources" in guide
        assert "30_day_action_plan" in guide
        assert "key_rules"          in guide

    def test_guide_niche_lookup(self):
        guide = get_theme_page_guide(niche="fitness")
        niche = guide["niche_analysis"]
        assert "Fitness" in niche["niche"]

    def test_guide_business_niche(self):
        guide = get_theme_page_guide(niche="business")
        niche = guide["niche_analysis"]
        assert "Business" in niche["niche"]

    def test_all_niches_populated(self):
        assert len(HIGH_CONVERTING_NICHES) >= 5
        for n in HIGH_CONVERTING_NICHES:
            assert "niche"          in n
            assert "monetization"   in n
            assert "avg_cpm"        in n
            assert "best_platforms" in n
            assert "affiliate_cos"  in n

    def test_growth_phases_count(self):
        assert len(GROWTH_PHASES) == 4  # Setup, Foundation, Acceleration, Monetization

    def test_30_day_plan_covers_all_stages(self):
        guide = get_theme_page_guide()
        plan  = guide["30_day_action_plan"]
        assert len(plan) == 7
        stages = {p["focus"] for p in plan}
        assert "Setup" in stages

    def test_key_rules_not_empty(self):
        guide = get_theme_page_guide()
        assert len(guide["key_rules"]) >= 8

    def test_monetization_rate_card(self):
        guide = get_theme_page_guide()
        mc = guide["monetization"]
        assert "paid_shoutouts"       in mc
        assert "affiliate_commissions" in mc
        assert "digital_products"     in mc
        assert len(mc["paid_shoutouts"]) >= 3

    def test_dm_templates_exist(self):
        guide = get_theme_page_guide()
        dms = guide["dm_templates"]
        assert "warm_lead_opener"    in dms
        assert "cold_brand_outreach" in dms
        assert "paid_promo_rate"     in dms
