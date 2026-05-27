"""Core unit tests for social-trends harness (no network required)."""
import pytest
from cli_anything.social_trends.hashtags import rank_hashtags, _parse_view_count, extract_hashtags
from cli_anything.social_trends.optimizer import generate_account_audit, optimize_profile, _score_to_grade
from cli_anything.social_trends.theme_pages import get_theme_page_guide
from cli_anything.social_trends.music import _extract_tt_music, _deduplicate_music


# ── hashtag ranking ───────────────────────────────────────────────────────────

SAMPLE_TT_ITEMS = [
    {"source": "tiktok", "description": "Gym day #fitness #gym", "hashtags": ["fitness", "gym"], "likes": 50000, "shares": 2000, "comments": 500, "plays": 1000000},
    {"source": "tiktok", "description": "Morning workout #fitness #motivation", "hashtags": ["fitness", "motivation"], "likes": 30000, "shares": 1000, "comments": 300, "plays": 500000},
    {"source": "tiktok", "description": "Recipe time #food #cooking", "hashtags": ["food", "cooking"], "likes": 20000, "shares": 800, "comments": 200, "plays": 300000},
    {"source": "youtube", "title": "Best fitness tips #fitness", "views": "1.2M views", "description_snippet": "Top gym hacks"},
]


def test_rank_hashtags_returns_sorted():
    ranked = rank_hashtags(SAMPLE_TT_ITEMS, top_n=10)
    assert len(ranked) > 0
    scores = [r["viral_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_rank_hashtags_fitness_is_top():
    ranked = rank_hashtags(SAMPLE_TT_ITEMS, top_n=5)
    top_tag = ranked[0]["tag"]
    assert top_tag == "#fitness"


def test_rank_hashtags_structure():
    ranked = rank_hashtags(SAMPLE_TT_ITEMS)
    for item in ranked:
        assert "tag" in item
        assert "count" in item
        assert "viral_score" in item
        assert item["tag"].startswith("#")


def test_rank_hashtags_empty():
    assert rank_hashtags([]) == []


def test_extract_hashtags_from_description():
    items = [{"description": "Check this out #viral #fyp #trending"}]
    tags = extract_hashtags(items)
    assert "viral" in tags
    assert "fyp" in tags


def test_parse_view_count():
    assert _parse_view_count("1.2M views") == 1_200_000
    assert _parse_view_count("500K views") == 500_000
    assert _parse_view_count("1B views") == 1_000_000_000
    assert _parse_view_count("12,345") == 12_345
    assert _parse_view_count("invalid") == 0


# ── account audit ─────────────────────────────────────────────────────────────

def test_audit_structure():
    result = generate_account_audit(
        platform="tiktok",
        username="test_account",
        niche="fitness",
        current_followers=10000,
        avg_views=5000,
        avg_likes=200,
        bio="I post fitness content follow me for tips",
        current_hashtags=["#fitness", "#gym"],
    )
    assert "score" in result
    assert "grade" in result
    assert "issues" in result
    assert "wins" in result
    assert "action_plan" in result
    assert "recommended_hashtags" in result
    assert 0 <= result["score"] <= 100


def test_audit_low_engagement_flagged():
    result = generate_account_audit(
        platform="tiktok",
        username="test",
        niche="finance",
        current_followers=100000,
        avg_likes=50,  # 0.05% engagement — terrible
        bio="Finance tips",
    )
    severities = [i["severity"] for i in result["issues"]]
    assert "high" in severities


def test_audit_score_to_grade():
    assert _score_to_grade(95) == "A"
    assert _score_to_grade(85) == "B"
    assert _score_to_grade(75) == "C"
    assert _score_to_grade(65) == "D"
    assert _score_to_grade(50) == "F"


def test_optimize_profile_structure():
    result = optimize_profile(platform="tiktok", niche="fitness")
    assert "optimized_bio" in result
    assert "hashtag_stack" in result
    assert "content_calendar_skeleton" in result
    assert "hook_templates" in result
    assert len(result["hook_templates"]) > 0


def test_optimize_all_platform_keys():
    from cli_anything.social_trends.optimizer import optimize_profile
    for platform in ["tiktok", "instagram", "youtube", "x_twitter"]:
        result = optimize_profile(platform=platform, niche="comedy")
        assert result["platform"] == platform


# ── theme pages ───────────────────────────────────────────────────────────────

def test_theme_page_guide_structure():
    guide = get_theme_page_guide(niche="fitness", goal="monetize", current_followers=5000)
    assert "overview" in guide
    assert "setup_checklist" in guide
    assert "content_strategy" in guide
    assert "monetization_roadmap" in guide
    assert "growth_hacks" in guide
    assert "common_mistakes" in guide


def test_theme_page_monetization_has_stages():
    guide = get_theme_page_guide(niche="finance", goal="monetize", current_followers=0)
    stages = guide["monetization_roadmap"]
    assert len(stages) == 5
    assert any(s["is_current"] for s in stages)


def test_theme_page_convert_goal():
    guide = get_theme_page_guide(niche="luxury", goal="convert", current_followers=1000)
    conversion = guide["conversion_guide"]
    assert "step_by_step" in conversion
    assert len(conversion["step_by_step"]) > 0


def test_theme_page_setup_checklist_ordered():
    guide = get_theme_page_guide(niche="pets")
    checklist = guide["setup_checklist"]
    steps = [int(c["step"]) for c in checklist]
    assert steps == sorted(steps)


# ── music ─────────────────────────────────────────────────────────────────────

def test_extract_tt_music_counts():
    items = [
        {"music_id": "123", "music_title": "Viral Song", "music_author": "Artist A", "likes": 1000},
        {"music_id": "123", "music_title": "Viral Song", "music_author": "Artist A", "likes": 2000},
        {"music_id": "456", "music_title": "Other Song", "music_author": "Artist B", "likes": 500},
    ]
    music = _extract_tt_music(items, top_n=10)
    assert music[0]["music_id"] == "123"
    assert music[0]["trending_video_count"] == 2


def test_deduplicate_music():
    items = [
        {"music_id": "123", "title": "Song A"},
        {"music_id": "123", "title": "Song A"},
        {"music_id": "456", "title": "Song B"},
    ]
    deduped = _deduplicate_music(items)
    assert len(deduped) == 2
