"""Unit tests for the trends module (offline)."""
import pytest

from cli_anything.clipper.core import trends
from cli_anything.clipper.core.session import Session
from cli_anything.clipper.core import project as proj_mod


def test_extract_hashtags_counts_case_insensitive():
    c = trends.extract_hashtags(["Wow #Shorts #fyp", "again #shorts"])
    assert c["#shorts"] == 2 and c["#fyp"] == 1


@pytest.mark.parametrize("platform", list(trends.PLATFORM_LIMITS))
def test_suggest_respects_platform_limit(platform):
    s = trends.suggest(platform, "finance")
    assert 0 < len(s["hashtags"]) <= trends.PLATFORM_LIMITS[platform]
    assert len(set(s["hashtags"])) == len(s["hashtags"])


def test_suggest_shorts_leads_with_shorts_tag():
    assert trends.suggest("shorts", "gaming")["hashtags"][0] == "#shorts"


def test_suggest_prefers_trending_niche_tag():
    s = trends.suggest("tiktok", "finance", limit=10)
    assert "#personalfinance" in s["hashtags"]


def test_suggest_rejects_unknown():
    with pytest.raises(ValueError):
        trends.suggest("myspace")
    with pytest.raises(ValueError):
        trends.suggest("tiktok", "knitting-noir")


def test_apply_writes_metadata_and_is_undoable():
    sess = Session()
    proj_mod.new_project(sess, name="t")
    r = trends.apply_to_project(sess, "tiktok", "pets", caption="Wait for it")
    meta = sess.get_project()["metadata"]["social"]["tiktok"]
    assert meta["caption"].startswith("Wait for it #")
    assert meta["hashtags"] == r["hashtags"]
    assert "sound" in meta
    sess.undo()
    assert "social" not in sess.get_project()["metadata"]
