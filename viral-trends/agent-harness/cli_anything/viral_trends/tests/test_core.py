"""Unit tests for viral-trends core modules (no network required)."""

import pytest
from cli_anything.viral_trends.core import analyzer, optimizer, theme_pages


# ─── Analyzer ────────────────────────────────────────────────────────────────

SAMPLE_VIDEOS = [
    {
        "id": "v1",
        "title": "Best workout 2025",
        "platform": "tiktok",
        "views": 1_000_000,
        "likes": 80_000,
        "comments": 5_000,
        "shares": 2_000,
        "hashtags": ["#fitness", "#workout", "#gym"],
        "music": {"track": "Blinding Lights", "artist": "The Weeknd"},
    },
    {
        "id": "v2",
        "title": "Finance tips",
        "platform": "youtube",
        "views": 500_000,
        "likes": 30_000,
        "comments": 3_000,
        "shares": 0,
        "hashtags": ["#finance", "#money", "#fitness"],
        "music": None,
    },
    {
        "id": "v3",
        "title": "Trending dance",
        "platform": "tiktok",
        "views": 2_000_000,
        "likes": 200_000,
        "comments": 10_000,
        "shares": 50_000,
        "hashtags": ["#fyp", "#fitness", "#viral"],
        "music": {"track": "Blinding Lights", "artist": "The Weeknd"},
    },
]


def test_extract_hashtags_basic():
    tags = analyzer.extract_hashtags(SAMPLE_VIDEOS)
    assert len(tags) > 0
    assert tags[0]["hashtag"].startswith("#")


def test_extract_hashtags_counts():
    tags = analyzer.extract_hashtags(SAMPLE_VIDEOS)
    tag_map = {t["hashtag"]: t for t in tags}
    assert tag_map["#fitness"]["frequency"] == 3


def test_extract_hashtags_top_limit():
    tags = analyzer.extract_hashtags(SAMPLE_VIDEOS, top=2)
    assert len(tags) <= 2


def test_extract_music():
    tracks = analyzer.extract_music(SAMPLE_VIDEOS)
    assert len(tracks) >= 1
    weeknd = next((t for t in tracks if "Weeknd" in t.get("artist", "")), None)
    assert weeknd is not None
    assert weeknd["use_count"] == 2


def test_engagement_score_high():
    viral = SAMPLE_VIDEOS[2]  # 200k likes, 10k comments, 50k shares on 2M views
    score = analyzer.engagement_score(viral)
    assert score > 0


def test_engagement_score_zero_views():
    v = {"views": 0, "likes": 0, "comments": 0}
    score = analyzer.engagement_score(v)
    assert score == 0.0


def test_summarize_trends():
    report = analyzer.summarize_trends(SAMPLE_VIDEOS)
    assert "top_hashtags" in report
    assert "top_music" in report
    assert "top_videos_by_engagement" in report
    assert report["total_analyzed"] == 3
    assert "youtube" in report["platforms"]
    assert "tiktok" in report["platforms"]


def test_summarize_trends_empty():
    report = analyzer.summarize_trends([])
    assert "error" in report


# ─── Optimizer ───────────────────────────────────────────────────────────────

SAMPLE_ACCOUNT = {
    "platform": "tiktok",
    "niche": "fitness",
    "followers": 5_000,
    "avg_views": 1_000,
    "avg_likes": 50,
    "avg_comments": 5,
    "post_frequency": "3x per week",
    "hashtags_used": ["#fitness", "#workout"],
}


def test_generate_account_report_structure():
    report = optimizer.generate_account_report(SAMPLE_ACCOUNT)
    assert "account" in report
    assert "metrics" in report
    assert "action_items" in report
    assert "platform_best_practices" in report
    assert "niche_hashtag_stack" in report


def test_tier_classification_nano():
    acc = {**SAMPLE_ACCOUNT, "followers": 500}
    report = optimizer.generate_account_report(acc)
    assert report["account"]["tier"] == "nano"


def test_tier_classification_micro():
    acc = {**SAMPLE_ACCOUNT, "followers": 5_000}
    report = optimizer.generate_account_report(acc)
    assert report["account"]["tier"] == "micro"


def test_tier_classification_macro():
    acc = {**SAMPLE_ACCOUNT, "followers": 500_000}
    report = optimizer.generate_account_report(acc)
    assert report["account"]["tier"] == "macro"


def test_engagement_rate_calculation():
    report = optimizer.generate_account_report(SAMPLE_ACCOUNT)
    # (50 + 5) / 5000 * 100 = 1.1%
    assert abs(report["metrics"]["engagement_rate_pct"] - 1.1) < 0.01


def test_low_engagement_flag():
    low_acc = {**SAMPLE_ACCOUNT, "followers": 10_000, "avg_likes": 50, "avg_comments": 5}
    report = optimizer.generate_account_report(low_acc)
    areas = [a["area"] for a in report["action_items"]]
    assert "Engagement" in areas


def test_template_structure():
    tmpl = optimizer.generate_template()
    assert "platform" in tmpl
    assert "niche" in tmpl
    assert "followers" in tmpl
    assert "hashtags_used" in tmpl


def test_optimize_multiple():
    accounts = [SAMPLE_ACCOUNT, {**SAMPLE_ACCOUNT, "niche": "finance"}]
    reports = optimizer.optimize_multiple(accounts)
    assert len(reports) == 2


def test_trend_recommendations_injected():
    report = optimizer.generate_account_report(SAMPLE_ACCOUNT, trend_data=SAMPLE_VIDEOS)
    assert "trend_recommendations" in report
    # Should have trending_hashtags rec since SAMPLE_VIDEOS has hashtags
    types = [r["type"] for r in report["trend_recommendations"]]
    assert "trending_hashtags" in types


# ─── Theme Pages ─────────────────────────────────────────────────────────────

def test_list_niches_not_empty():
    niches = theme_pages.list_niches()
    assert len(niches) > 0
    for n in niches:
        assert "niche" in n
        assert "monetization" in n or "top_monetization" in n


def test_get_niche_guide_fitness():
    guide = theme_pages.get_niche_guide("fitness")
    assert "monetization" in guide
    assert "growth_phases" in guide
    assert "hook_formulas" in guide
    assert guide["niche"] == "fitness"


def test_get_niche_guide_unknown():
    guide = theme_pages.get_niche_guide("underwater_basket_weaving")
    assert "error" in guide
    assert "available" in guide


def test_get_conversion_guide():
    guide = theme_pages.get_conversion_guide()
    assert "steps" in guide
    assert "growth_phases" in guide
    assert len(guide["steps"]) >= 5


def test_growth_phases_ordered():
    phases = theme_pages.get_growth_phases()
    assert len(phases) >= 4
    for i, p in enumerate(phases):
        assert p["phase"] == i + 1


def test_hook_formulas_not_empty():
    hooks = theme_pages.HOOK_FORMULAS
    assert len(hooks) >= 5
    for h in hooks:
        assert isinstance(h, str)
        assert len(h) > 5
