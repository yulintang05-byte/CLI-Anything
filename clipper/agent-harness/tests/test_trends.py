"""Unit tests for trend snapshot suggestions."""
import datetime as dt
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.clipper.core import trends


@pytest.fixture
def snap():
    return trends.load_snapshot("2026-11-11", today=dt.date(2026, 11, 12))


def test_latest_snapshot_exists():
    assert "2026-11-11" in trends.list_snapshots()


def test_staleness(snap):
    assert snap["age_days"] == 1 and not snap["stale"]
    old = trends.load_snapshot("2026-11-11", today=dt.date(2026, 12, 1))
    assert old["stale"]


def test_unknown_snapshot():
    with pytest.raises(ValueError):
        trends.load_snapshot("1999-01-01")


def test_shorts_tags_include_shorts_and_respect_limit(snap):
    tags = trends.suggest_hashtags(snap, "youtube_shorts", "gaming")
    assert tags[0] == "#shorts"
    assert len(tags) == trends.TAG_LIMITS["youtube_shorts"]


def test_tiktok_gaming_tags_on_niche(snap):
    tags = trends.suggest_hashtags(snap, "tiktok", "gaming")
    assert tags[0] == "#stormarena"  # highest growth gaming tag
    assert "#skincarecommunity" not in tags
    assert len(tags) == len(set(tags)) <= 5


def test_unknown_niche_falls_back_to_default(snap):
    assert trends.suggest_hashtags(snap, "tiktok", "underwater-basket") == ["#fyp", "#viral"]


def test_bad_platform(snap):
    with pytest.raises(ValueError):
        trends.suggest_hashtags(snap, "myspace")


def test_sounds_mood_first(snap):
    sounds = trends.suggest_sounds(snap, "tiktok", "holiday")
    assert sounds[0]["mood"] == "holiday"


def test_caption_hook_first(snap):
    out = trends.build_caption("He did NOT see that coming", "tiktok", snap, "gaming")
    assert out["caption"].startswith("He did NOT see that coming\nFollow for part 2\n#")
    assert out["snapshot_date"] == "2026-11-11"
    out2 = trends.build_caption("x", "tiktok", snap, cta="")
    assert out2["caption"] == "x\n#fyp #viral"
