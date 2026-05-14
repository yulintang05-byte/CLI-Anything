"""Unit tests for viraltrends core modules (no network required)."""
import pytest
from cli_anything.viraltrends.core import trends as tr
from cli_anything.viraltrends.core import account as ac
from cli_anything.viraltrends.core import themepage as tp
from cli_anything.viraltrends.core.scraper import (
    _extract_hashtags,
    _safe_int,
    _parse_view_count,
    _parse_tiktok_item,
)


# ── scraper utilities ─────────────────────────────────────────────────────────

def test_extract_hashtags():
    tags = _extract_hashtags("Check #fitness and #gym tips #Fitness")
    assert "#fitness" in tags
    assert "#gym" in tags
    assert len(tags) == 2  # deduped (case-insensitive)


def test_safe_int():
    assert _safe_int("1,234") == 1234
    assert _safe_int("") == 0
    assert _safe_int("abc") == 0
    assert _safe_int("42") == 42


def test_parse_view_count():
    assert _parse_view_count("1.2M views") == 1_200_000
    assert _parse_view_count("500K views") == 500_000
    assert _parse_view_count("2B views") == 2_000_000_000
    assert _parse_view_count("12,345 views") == 12345


def test_parse_tiktok_item_minimal():
    item = {
        "id": "123",
        "desc": "Check out #fitness tips",
        "stats": {"playCount": 100000, "diggCount": 5000, "commentCount": 300, "shareCount": 100},
        "music": {"title": "Viral Song", "authorName": "Artist", "id": 456},
        "author": {"uniqueId": "testuser", "followerCount": 50000},
        "challenges": [{"title": "fitnesschallenge"}],
        "video": {"duration": 30},
    }
    result = _parse_tiktok_item(item, 1)
    assert result["rank"] == 1
    assert result["platform"] == "tiktok"
    assert result["plays"] == 100000
    assert result["music_title"] == "Viral Song"
    assert "fitnesschallenge" in result["hashtags"] or "#fitness" in result["hashtags"]


# ── trends ────────────────────────────────────────────────────────────────────

def test_score_video_tiktok():
    v = {"plays": 1_000_000, "likes": 50_000, "comments": 2_000, "shares": 500}
    score = tr.score_video(v)
    assert score > 0
    assert isinstance(score, float)


def test_score_video_youtube():
    v = {"views": 500_000, "likes": 10_000}
    score = tr.score_video(v)
    assert score >= 0


def test_merge_trends():
    yt = [{"rank": 1, "platform": "youtube", "views": 1_000_000, "likes": 50_000, "title": "A"}]
    tt = [{"rank": 1, "platform": "tiktok", "plays": 2_000_000, "likes": 100_000, "shares": 5_000, "title": "B"}]
    merged = tr.merge_trends(yt, tt)
    assert len(merged) == 2
    assert merged[0]["combined_rank"] == 1


def test_top_hashtags_across_platforms():
    yt_tags = [{"tag": "#fitness", "count": 5}, {"tag": "#gym", "count": 3}]
    tt_tags = [{"tag": "#fitness", "video_count": 10}, {"tag": "#fyp", "video_count": 20}]
    merged = tr.top_hashtags_across_platforms(yt_tags, tt_tags, limit=5)
    # #fyp has 20 total, #fitness has 15 (5 YT + 10 TT), so #fyp ranks first
    assert merged[0]["tag"] == "#fyp"
    # #fitness should appear in merged result with correct counts
    fitness = next(m for m in merged if m["tag"] == "#fitness")
    assert fitness["youtube_count"] == 5
    assert fitness["tiktok_count"] == 10
    assert fitness["total"] == 15


def test_content_gap_analysis():
    yt_tags = [{"tag": "#mrbeast"}, {"tag": "#shorts"}]
    tt_tags = [{"tag": "#fyp"}, {"tag": "#shorts"}]
    gaps = tr.content_gap_analysis(yt_tags, tt_tags)
    assert "youtube_only" in gaps
    assert "tiktok_only" in gaps
    assert "cross_platform_opportunities" in gaps
    yt_only_tags = [t["tag"].lower().lstrip("#") for t in gaps["youtube_only"]]
    assert "mrbeast" in yt_only_tags


def test_niche_affinity():
    videos = [
        {"title": "Best gym workout", "hashtags": ["#gym"], "description": ""},
        {"title": "Cooking pasta recipe", "hashtags": ["#food"], "description": ""},
    ]
    result = tr.niche_affinity(videos, ["gym", "fitness"])
    assert len(result) == 1
    assert result[0]["title"] == "Best gym workout"


# ── account ───────────────────────────────────────────────────────────────────

def test_posting_schedule_tiktok():
    sched = ac.posting_schedule("tiktok", timezone_offset=0)
    assert "schedule" in sched
    assert "Mon" in sched["schedule"]
    assert len(sched["schedule"]["Mon"]) > 0


def test_posting_schedule_tz_adjusted():
    sched = ac.posting_schedule("tiktok", timezone_offset=-5)
    assert sched["timezone_offset_hours"] == -5


def test_hashtag_strategy():
    strategy = ac.hashtag_strategy("tiktok", "fitness", ["#workout", "#gym"])
    assert "suggested_tags" in strategy
    assert "#fyp" in strategy["suggested_tags"]
    assert "#workout" in strategy["suggested_tags"]


def test_bio_template():
    bio = ac.bio_template("tiktok", "fitness", "daily workouts", "Free plan in bio")
    assert "bio" in bio
    assert "fitness" in bio["bio"].lower()
    assert bio["char_count"] <= bio["limit"] + 50  # some slack


def test_profile_audit_checklist():
    checklist = ac.profile_audit_checklist("youtube")
    assert len(checklist) > 5
    items = [c["item"] for c in checklist]
    assert "Channel banner" in items


def test_content_calendar():
    cal = ac.content_calendar("tiktok", "fitness", posts_per_week=3)
    assert len(cal) == 3
    assert "day" in cal[0]
    assert "content_idea" in cal[0]


# ── themepage ─────────────────────────────────────────────────────────────────

def test_niche_research_list():
    niches = tp.niche_research()
    assert isinstance(niches, list)
    assert len(niches) >= 5
    keys = [n["key"] for n in niches]
    assert "finance" in keys


def test_niche_research_specific():
    info = tp.niche_research("finance")
    assert info["name"] == "Personal Finance / Investing"
    assert "monetization" in info
    assert len(info["monetization"]) > 0


def test_niche_research_fuzzy():
    info = tp.niche_research("crypto")
    assert "error" not in info
    assert "Crypto" in info["name"]


def test_niche_research_not_found():
    info = tp.niche_research("xyznonexistent")
    assert "error" in info
    assert "available" in info


def test_theme_page_playbook():
    pb = tp.theme_page_playbook("fitness", "tiktok")
    assert "playbook" in pb
    assert "phase_1_setup" in pb["playbook"]
    assert "phase_5_monetization" in pb["playbook"]
    assert pb["platform"] == "tiktok"


def test_converting_guide():
    guide = tp.converting_guide()
    assert "conversion_funnels" in guide
    assert len(guide["conversion_funnels"]) >= 3
    names = [f["name"] for f in guide["conversion_funnels"]]
    assert "Affiliate Funnel" in names
    assert "DM Funnel" in names


def test_account_selling_guide():
    guide = tp.account_selling_guide()
    assert "valuation" in guide
    assert "marketplaces" in guide
    assert len(guide["marketplaces"]) >= 3
