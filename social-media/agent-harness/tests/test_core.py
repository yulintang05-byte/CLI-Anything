"""Core unit tests for cli-anything-social-media."""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_media.core import trends, hashtags, optimizer, content, theme_pages


# ──────────────────────────────────────────────
#  Trends
# ──────────────────────────────────────────────

def test_youtube_fallback_returns_items():
    items = trends._youtube_fallback(10)
    assert len(items) == 10
    for item in items:
        assert item.platform == "youtube"
        assert item.rank >= 1
        assert item.title


def test_tiktok_hashtag_fallback_limit():
    data = trends._tiktok_hashtag_fallback(5)
    assert len(data) == 5
    assert all("hashtag" in d for d in data)
    assert all("growth" in d for d in data)


def test_tiktok_sounds_returns_list():
    sounds = trends.tiktok_trending_sounds(limit=5)
    assert len(sounds) == 5
    for s in sounds:
        assert "title" in s
        assert "artist" in s
        assert "bpm" in s


def test_google_trends_no_pytrends():
    # Without pytrends installed, should return an error dict not raise
    result = trends.google_trends(["fitness"], geo="US")
    assert isinstance(result, dict)


def test_trend_items_to_dict():
    items = trends._youtube_fallback(3)
    dicts = trends.trend_items_to_dict(items)
    assert len(dicts) == 3
    assert all(isinstance(d, dict) for d in dicts)


# ──────────────────────────────────────────────
#  Hashtags
# ──────────────────────────────────────────────

def test_list_niches_nonempty():
    niches = hashtags.list_niches()
    assert len(niches) >= 5
    assert "fitness" in niches
    assert "finance" in niches


def test_build_caption_hashtags_valid_niche():
    result = hashtags.build_caption_hashtags("fitness", max_tags=20)
    assert "hashtags" in result
    assert len(result["hashtags"]) <= 20
    assert result["total_tags"] == len(result["hashtags"])
    assert "#fyp" in result["hashtags"]


def test_build_caption_hashtags_unknown_niche():
    result = hashtags.build_caption_hashtags("unknownniche123")
    assert "error" in result


def test_hashtag_audit_flags_banned():
    result = hashtags.hashtag_audit(["#fyp", "#like4like", "#fitness"])
    assert result["flagged"] == 1
    assert result["ok"] == 2


def test_hashtag_audit_all_clean():
    result = hashtags.hashtag_audit(["#fitness", "#gym", "#workout"])
    assert result["flagged"] == 0


def test_get_hashtag_set():
    hs = hashtags.get_hashtag_set("finance")
    assert hs is not None
    assert hs.niche == "finance"
    assert len(hs.mega) > 0


# ──────────────────────────────────────────────
#  Optimizer
# ──────────────────────────────────────────────

def test_audit_high_engagement():
    result = optimizer.audit_account(
        platform="tiktok",
        follower_count=10000,
        avg_views=50000,
        avg_likes=1000,
        avg_comments=100,
        posting_days_per_week=5,
        has_cta_in_bio=True,
        has_link_in_bio=True,
    )
    assert result["grade"] in ("A", "B", "C", "D")
    assert "metrics" in result
    assert "priority_actions" in result
    assert result["metrics"]["engagement_rate_pct"] > 0


def test_audit_low_engagement():
    result = optimizer.audit_account(
        platform="instagram",
        follower_count=5000,
        avg_views=100,
        avg_likes=10,
        avg_comments=0,
        posting_days_per_week=1,
    )
    assert len(result["issues"]) > 0
    assert len(result["priority_actions"]) > 0


def test_get_posting_schedule_tiktok():
    sched = optimizer.get_posting_schedule("tiktok", timezone_offset=-5)
    assert "schedule" in sched
    assert "monday" in sched["schedule"]
    assert sched["timezone_offset_hours"] == -5


def test_get_posting_schedule_unknown_platform():
    result = optimizer.get_posting_schedule("snapchat")
    assert "error" in result


def test_platform_specs_valid():
    specs = optimizer.platform_specs("youtube")
    assert "algorithm_signals" in specs
    assert "growth_tactics" in specs


def test_platform_specs_invalid():
    result = optimizer.platform_specs("myspace")
    assert "error" in result


def test_generate_bio():
    result = optimizer.generate_bio(
        platform="tiktok",
        account_type="themepage",
        niche="motivation",
        audience="entrepreneurs",
        outcome="build their dream life",
    )
    assert "bio" in result
    assert result["char_limit"] == 80


# ──────────────────────────────────────────────
#  Content
# ──────────────────────────────────────────────

def test_generate_hooks_all_types():
    result = content.generate_hooks("fitness", hook_type="all", count=10)
    assert "hooks" in result
    assert len(result["hooks"]) <= 10
    assert all("hook" in h and "type" in h for h in result["hooks"])


def test_generate_hooks_specific_type():
    result = content.generate_hooks("finance", hook_type="curiosity", count=3)
    assert all(h["type"] == "curiosity" for h in result["hooks"])


def test_generate_hooks_invalid_type():
    result = content.generate_hooks("fitness", hook_type="nonexistent")
    assert "error" in result


def test_generate_content_calendar():
    result = content.generate_content_calendar("motivation", weeks=2)
    assert result["total_posts"] == 14
    assert len(result["calendar"]) == 14
    assert all("date" in d and "hook" in d for d in result["calendar"])


def test_get_viral_templates():
    result = content.get_viral_templates("finance")
    assert "templates" in result
    assert len(result["templates"]) >= 3
    assert all("filled" in t for t in result["templates"])


# ──────────────────────────────────────────────
#  Theme pages
# ──────────────────────────────────────────────

def test_get_playbook_full():
    data = theme_pages.get_playbook()
    assert "stages" in data
    assert "30_day_action_plan" in data
    assert len(data["stages"]) == 6


def test_get_playbook_section():
    data = theme_pages.get_playbook("copyright_rules")
    assert "copyright_rules" in data
    assert isinstance(data["copyright_rules"], list)


def test_get_playbook_unknown_section():
    data = theme_pages.get_playbook("unknown_section_xyz")
    assert "error" in data


def test_get_stage_valid():
    stage = theme_pages.get_stage(1)
    assert stage["stage"] == 1
    assert "actions" in stage
    assert "tools" in stage


def test_get_stage_invalid():
    stage = theme_pages.get_stage(99)
    assert "error" in stage


def test_all_stages_have_required_keys():
    for i in range(1, 7):
        stage = theme_pages.get_stage(i)
        assert "name" in stage
        assert "duration" in stage
        assert "actions" in stage
