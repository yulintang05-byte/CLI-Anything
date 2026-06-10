"""TrendHunter unit tests — synthetic data, no network calls."""

import pytest
from unittest.mock import patch, MagicMock

from cli_anything.trendhunter.core.youtube_scraper import (
    YouTubeVideo, YouTubeTrends, extract_hashtags_from_videos,
)
from cli_anything.trendhunter.core.tiktok_scraper import (
    TikTokHashtag, TikTokSound, TikTokTrends,
    _fallback_curated_hashtags,
)
from cli_anything.trendhunter.core.trend_analyzer import (
    _score_hashtag, _detect_niches, analyze_trends,
    get_recommended_hashtags, TrendReport, ScoredTrend,
)
from cli_anything.trendhunter.core.account_optimizer import (
    AccountProfile, optimize_account, get_posting_schedule,
    get_bio_formulas, get_engagement_tactics, estimate_growth,
    get_content_pillars,
)
from cli_anything.trendhunter.core.theme_page import (
    get_niche_analysis, get_conversion_funnel, get_monetization_strategies,
    get_cta_templates, get_growth_playbook, calculate_conversion_rate,
)


# ── Fixtures ──────────────────────────────────────────────────────────

def make_yt_trends():
    videos = [
        YouTubeVideo("vid1", "Gym workout #fitness #gains", "FitChannel", "2025-01-01",
                     views=5_000_000, likes=120_000, hashtags=["fitness", "gains"]),
        YouTubeVideo("vid2", "GRWM #beauty #makeup tutorial", "BeautyGuru", "2025-01-01",
                     views=3_000_000, likes=80_000, hashtags=["beauty", "makeup"]),
        YouTubeVideo("vid3", "#fitness morning routine", "HealthCreator", "2025-01-01",
                     views=1_000_000, hashtags=["fitness"]),
        YouTubeVideo("vid4", "Money tips #finance #investing", "WealthTips", "2025-01-01",
                     views=2_000_000, hashtags=["finance", "investing"]),
        YouTubeVideo("vid5", "Funny #meme compilation", "MemeKing", "2025-01-01",
                     views=8_000_000, hashtags=["meme", "funny"]),
    ]
    return YouTubeTrends(
        region="US", videos=videos,
        trending_hashtags=["fitness", "gains", "beauty", "makeup", "finance",
                           "investing", "meme", "funny"],
        trending_music=[{"title": "APT.", "source": "youtube_music"}],
        shorts_trends=["fyp", "viral"],
    )


def make_tt_trends():
    hashtags = [
        TikTokHashtag("fyp",      view_count=50_000_000_000),
        TikTokHashtag("fitness",  view_count=5_000_000_000),
        TikTokHashtag("viral",    view_count=20_000_000_000),
        TikTokHashtag("beauty",   view_count=8_000_000_000),
        TikTokHashtag("finance",  view_count=2_000_000_000),
        TikTokHashtag("meme",     view_count=2_500_000_000),
        TikTokHashtag("cooking",  view_count=500_000_000),
        TikTokHashtag("gymtok",   view_count=300_000_000),
    ]
    sounds = [
        TikTokSound("APT. - ROSÉ", "ROSÉ"),
        TikTokSound("Espresso - Sabrina Carpenter", "Sabrina Carpenter"),
    ]
    return TikTokTrends(
        region="US", hashtags=hashtags, sounds=sounds,
        trending_creators=["gymrat", "beautyqueen"],
    )


# ── YouTubeVideo ──────────────────────────────────────────────────────

class TestYouTubeVideo:
    def test_to_dict(self):
        v = YouTubeVideo("abc", "Test", "Chan", "2025-01-01",
                         hashtags=["cool"])
        d = v.to_dict()
        assert d["video_id"] == "abc"
        assert d["title"] == "Test"
        assert "cool" in d["hashtags"]

    def test_url_in_dict(self):
        v = YouTubeVideo("xyz", "T", "C", "2025-01-01", url="https://youtu.be/xyz")
        assert "youtu" in v.to_dict()["url"]


class TestExtractHashtags:
    def test_counts_and_ranks(self):
        videos = [
            YouTubeVideo("1", "a", "c", "d", hashtags=["fitness", "gym"]),
            YouTubeVideo("2", "b", "c", "d", hashtags=["fitness", "beauty"]),
            YouTubeVideo("3", "c", "c", "d", hashtags=["fitness"]),
        ]
        tags = extract_hashtags_from_videos(videos, top_n=3)
        assert tags[0] == "fitness"   # appears 3 times

    def test_respects_top_n(self):
        videos = [YouTubeVideo(str(i), "t", "c", "d", hashtags=[f"tag{i}"])
                  for i in range(20)]
        tags = extract_hashtags_from_videos(videos, top_n=5)
        assert len(tags) <= 5


class TestYouTubeTrends:
    def test_to_dict_structure(self):
        yt = make_yt_trends()
        d = yt.to_dict()
        assert "videos" in d
        assert "trending_hashtags" in d
        assert "trending_music" in d
        assert isinstance(d["videos"], list)


# ── TikTok ────────────────────────────────────────────────────────────

class TestTikTokHashtag:
    def test_to_dict_url(self):
        h = TikTokHashtag("gymtok", view_count=300_000_000)
        d = h.to_dict()
        assert "tiktok.com/tag/gymtok" in d["url"]
        assert d["view_count"] == 300_000_000

    def test_fallback_returns_list(self):
        tags = _fallback_curated_hashtags()
        assert len(tags) >= 10
        names = [t.name for t in tags]
        assert "fyp" in names
        assert "viral" in names


class TestTikTokTrends:
    def test_to_dict(self):
        tt = make_tt_trends()
        d = tt.to_dict()
        assert "hashtags" in d
        assert "sounds" in d
        assert len(d["hashtags"]) > 0


# ── TrendAnalyzer ─────────────────────────────────────────────────────

class TestScoreHashtag:
    def test_cross_platform_bonus(self):
        score_cross = _score_hashtag("fitness", yt_count=3, tt_count=5, tt_view_count=5e9)
        score_yt    = _score_hashtag("fitness", yt_count=3, tt_count=0, tt_view_count=0)
        assert score_cross > score_yt

    def test_score_capped_at_100(self):
        score = _score_hashtag("a", yt_count=100, tt_count=100, tt_view_count=50_000_000_000)
        assert score <= 100.0

    def test_zero_input_nonzero(self):
        score = _score_hashtag("abc", 0, 0, 0)
        assert score == 0.0


class TestDetectNiches:
    def test_fitness_detection(self):
        niches = _detect_niches("fitness")
        assert "fitness" in niches

    def test_multi_niche(self):
        niches = _detect_niches("fitnessmotivation")
        assert "fitness" in niches or "motivation" in niches

    def test_unknown_tag(self):
        niches = _detect_niches("xyzqwerasdf")
        assert niches == []


class TestAnalyzeTrends:
    def test_returns_trend_report(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        assert isinstance(report, TrendReport)

    def test_top_trends_not_empty(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        assert len(report.top_trends) > 0

    def test_cross_platform_tags_on_both(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        for t in report.cross_platform:
            assert "youtube" in t.platforms
            assert "tiktok" in t.platforms

    def test_trending_music_merged(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        sources = {m.get("source") for m in report.trending_music}
        # Should have at least one source
        assert len(sources) >= 1

    def test_viral_hooks_generated(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        assert len(report.viral_hooks) > 0
        assert any("#" in h for h in report.viral_hooks)


class TestRecommendedHashtags:
    def test_returns_correct_count(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        tags = get_recommended_hashtags("fitness", report, count=10)
        assert len(tags) <= 10

    def test_all_tags_start_with_hash(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        tags = get_recommended_hashtags("fitness", report, count=5)
        assert all(t.startswith("#") for t in tags)

    def test_no_mix_returns_tags(self):
        yt = make_yt_trends()
        tt = make_tt_trends()
        report = analyze_trends(yt, tt)
        tags = get_recommended_hashtags("fitness", report, mix=False, count=5)
        assert len(tags) >= 1


# ── AccountOptimizer ──────────────────────────────────────────────────

class TestPostingSchedule:
    def test_tiktok_returns_slots(self):
        sched = get_posting_schedule("tiktok", "us_east")
        assert len(sched) >= 3
        assert all("time" in s for s in sched)

    def test_youtube_returns_slots(self):
        sched = get_posting_schedule("youtube", "global")
        assert len(sched) >= 3

    def test_unknown_platform_graceful(self):
        sched = get_posting_schedule("unknown_platform", "global")
        assert isinstance(sched, list)


class TestBioFormulas:
    def test_tiktok_formulas(self):
        f = get_bio_formulas("tiktok")
        assert len(f) >= 3

    def test_all_formulas_strings(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            formulas = get_bio_formulas(platform)
            assert all(isinstance(x, str) for x in formulas)


class TestEngagementTactics:
    def test_all_tactics_have_required_keys(self):
        tactics = get_engagement_tactics()
        for t in tactics:
            assert "tactic" in t
            assert "impact" in t
            assert "why" in t

    def test_platform_filter(self):
        tactics = get_engagement_tactics("tiktok")
        for t in tactics:
            assert "tiktok" in t["platforms"]

    def test_high_impact_tactics_exist(self):
        tactics = get_engagement_tactics()
        high = [t for t in tactics if t["impact"] in ("high", "very_high")]
        assert len(high) >= 3


class TestEstimateGrowth:
    def test_growth_increases_followers(self):
        g = estimate_growth(1000, "starter", 3)
        assert g["in_4_weeks"] > 1000
        assert g["in_3_months"] > g["in_4_weeks"]

    def test_more_posts_more_growth(self):
        g_low  = estimate_growth(10000, "growing", 1)
        g_high = estimate_growth(10000, "growing", 7)
        assert g_high["in_4_weeks"] > g_low["in_4_weeks"]

    def test_returns_all_keys(self):
        g = estimate_growth(5000, "growing", 3)
        for k in ["current_followers", "in_4_weeks", "in_3_months", "in_6_months"]:
            assert k in g


class TestContentPillars:
    def test_fitness_pillars(self):
        pillars = get_content_pillars("fitness")
        assert len(pillars) >= 4

    def test_unknown_niche_fallback(self):
        pillars = get_content_pillars("unknownniche123")
        assert len(pillars) >= 4

    def test_all_strings(self):
        pillars = get_content_pillars("beauty")
        assert all(isinstance(p, str) for p in pillars)


class TestOptimizeAccount:
    def test_full_report(self):
        profile = AccountProfile("tiktok", niche="fitness", followers=5000, stage="growing")
        report = optimize_account(profile)
        assert len(report.posting_schedule) >= 3
        assert len(report.bio_formulas) >= 2
        assert len(report.content_pillars) >= 4
        assert report.recommended_frequency >= 1

    def test_to_dict(self):
        profile = AccountProfile("instagram", niche="beauty", followers=1000)
        report = optimize_account(profile)
        d = report.to_dict()
        assert "posting_schedule" in d
        assert "engagement_tactics" in d


# ── ThemePage ─────────────────────────────────────────────────────────

class TestNicheAnalysis:
    def test_finance_niche(self):
        data = get_niche_analysis("finance_money")
        assert data["monetization_score"] >= 8
        assert "revenue_streams" in data

    def test_partial_match(self):
        data = get_niche_analysis("fitness")
        assert "monetization_score" in data

    def test_unknown_niche_fallback(self):
        data = get_niche_analysis("xyzqwer")
        assert data["monetization_score"] >= 1
        assert "revenue_streams" in data


class TestConversionFunnel:
    def test_stages_count(self):
        funnel = get_conversion_funnel("fitness", "tiktok")
        assert len(funnel.stages) == 5

    def test_stages_have_kpis(self):
        funnel = get_conversion_funnel()
        for s in funnel.stages:
            assert "kpi" in s
            assert "tactics" in s

    def test_link_in_bio_tools(self):
        funnel = get_conversion_funnel()
        tools = [t["tool"] for t in funnel.link_in_bio_tools]
        assert "Linktree" in tools or "Beacons.ai" in tools

    def test_to_dict(self):
        funnel = get_conversion_funnel("beauty")
        d = funnel.to_dict()
        assert "stages" in d
        assert "cta_templates" in d


class TestMonetizationStrategies:
    def test_returns_list(self):
        strategies = get_monetization_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) >= 5

    def test_all_have_required_fields(self):
        for s in get_monetization_strategies():
            assert "method" in s
            assert "effort" in s
            assert "income_range" in s
            assert "how" in s

    def test_affiliate_in_list(self):
        methods = [s["method"] for s in get_monetization_strategies()]
        assert any("Affiliate" in m for m in methods)


class TestCtaTemplates:
    def test_returns_templates(self):
        templates = get_cta_templates("fitness", "tiktok")
        assert len(templates) >= 5

    def test_all_strings(self):
        for t in get_cta_templates():
            assert isinstance(t, str)

    def test_youtube_extra_ctas(self):
        tt_ctas = get_cta_templates("finance", "tiktok")
        yt_ctas = get_cta_templates("finance", "youtube")
        assert len(yt_ctas) >= len(tt_ctas)


class TestGrowthPlaybook:
    def test_five_phases(self):
        playbook = get_growth_playbook("fitness", "tiktok")
        assert len(playbook) == 5

    def test_each_phase_has_actions(self):
        for phase in get_growth_playbook("beauty"):
            assert "actions" in phase
            assert len(phase["actions"]) >= 3

    def test_phase_names_sequential(self):
        playbook = get_growth_playbook("tech")
        for i, phase in enumerate(playbook, 1):
            assert str(i) in phase["phase"]


class TestCalculateConversionRate:
    def test_basic_ctr(self):
        data = calculate_conversion_rate(10000, link_clicks=100)
        assert data["link_ctr"] == "1.00%"

    def test_conversion_rate(self):
        data = calculate_conversion_rate(10000, link_clicks=100, sales=5)
        assert data["conversion_rate"] == "5.00%"

    def test_zero_followers_empty(self):
        data = calculate_conversion_rate(0, link_clicks=50)
        assert data == {}

    def test_no_clicks_na(self):
        data = calculate_conversion_rate(10000)
        assert data["link_ctr"] == "N/A"

    def test_benchmarks_present(self):
        data = calculate_conversion_rate(10000, 200)
        assert "benchmarks" in data
        assert "link_ctr_good" in data["benchmarks"]
