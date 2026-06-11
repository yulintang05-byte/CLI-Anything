"""Unit tests for youtube_scraper.py — all using synthetic data."""
import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from social_trends.agent_harness.utils.youtube_scraper import (
    _parse_view_count,
    extract_hashtags_from_videos,
    fetch_trending_videos,
    fetch_music_trends,
)

# ---------------------------------------------------------------------------
# _parse_view_count
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("1.2M views", 1_200_000),
    ("500K views", 500_000),
    ("1B views", 1_000_000_000),
    ("100 views", 100),
    ("0 views", 0),
    ("2.5k", 2_500),
    ("10,000 views", 10_000),
    ("", 0),
])
def test_parse_view_count(text, expected):
    assert _parse_view_count(text) == expected


# ---------------------------------------------------------------------------
# extract_hashtags_from_videos
# ---------------------------------------------------------------------------

def _make_video(vid_id, title, tags=None, desc=""):
    return {
        "id": vid_id, "title": title,
        "tags": tags or [],
        "description": desc,
        "views": 100_000,
        "likes": 5_000,
    }

def test_extract_hashtags_returns_sorted():
    videos = [
        _make_video("v1", "Fitness #gym #workout", tags=["gym", "fitness"]),
        _make_video("v2", "Gym gains", tags=["gym", "gains"]),
        _make_video("v3", "Workout time", tags=["workout"]),
    ]
    result = extract_hashtags_from_videos(videos)
    assert isinstance(result, list)
    assert all("hashtag" in r for r in result)
    # 'gym' appears in 2 tag lists → should be near top
    hashtags = [r["hashtag"] for r in result]
    assert "#gym" in hashtags
    # Sorted by frequency descending
    freqs = [r["frequency"] for r in result]
    assert freqs == sorted(freqs, reverse=True)


def test_extract_hashtags_deduplicates():
    videos = [_make_video("v1", "#music #music #music", tags=["music"])]
    result = extract_hashtags_from_videos(videos)
    music_entries = [r for r in result if r["hashtag"] == "#music"]
    assert len(music_entries) == 1


def test_extract_hashtags_empty():
    assert extract_hashtags_from_videos([]) == []


# ---------------------------------------------------------------------------
# fetch_trending_videos — API path (mocked)
# ---------------------------------------------------------------------------

_MOCK_API_RESPONSE = {
    "items": [
        {
            "id": "abc123",
            "snippet": {
                "title": "Test Video",
                "channelTitle": "Test Channel",
                "publishedAt": "2024-01-01T00:00:00Z",
                "tags": ["trending", "viral"],
                "description": "Great video #trending",
                "thumbnails": {"high": {"url": "https://img.youtube.com/abc"}},
            },
            "statistics": {
                "viewCount": "1500000",
                "likeCount": "75000",
                "commentCount": "3000",
            },
        }
    ]
}

@patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake_key"})
@patch("social_trends.agent_harness.utils.youtube_scraper._get",
       return_value=_MOCK_API_RESPONSE)
def test_fetch_trending_videos_api(mock_get):
    videos = fetch_trending_videos(region="US", max_results=5)
    assert len(videos) == 1
    v = videos[0]
    assert v["id"] == "abc123"
    assert v["title"] == "Test Video"
    assert v["views"] == 1_500_000
    assert v["likes"] == 75_000
    assert v["source"] == "api"
    assert v["url"] == "https://youtu.be/abc123"


@patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake_key"})
@patch("social_trends.agent_harness.utils.youtube_scraper._get",
       return_value={"items": []})
def test_fetch_trending_videos_api_empty(mock_get):
    videos = fetch_trending_videos(region="US", max_results=5)
    assert videos == []


# ---------------------------------------------------------------------------
# fetch_music_trends
# ---------------------------------------------------------------------------

@patch.dict(os.environ, {"YOUTUBE_API_KEY": "fake_key"})
@patch("social_trends.agent_harness.utils.youtube_scraper._get",
       return_value={
           "items": [{
               "id": "m1",
               "snippet": {
                   "title": "Artist - Song Name",
                   "channelTitle": "VEVO",
                   "publishedAt": "2024-01-02T00:00:00Z",
                   "tags": [],
                   "description": "",
                   "thumbnails": {},
               },
               "statistics": {"viewCount": "5000000", "likeCount": "200000", "commentCount": "5000"},
           }]
       })
def test_fetch_music_trends_splits_artist_track(mock_get):
    music = fetch_music_trends(region="US", max_results=5)
    assert len(music) == 1
    assert music[0]["artist"] == "Artist"
    assert music[0]["track"] == "Song Name"


# ---------------------------------------------------------------------------
# Scrape-mode fallback
# ---------------------------------------------------------------------------

@patch.dict(os.environ, {}, clear=True)  # no API key
@patch("social_trends.agent_harness.utils.youtube_scraper.requests.get")
def test_fetch_trending_videos_scrape_fallback(mock_req):
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.text = (
        'var ytInitialData = {};</script>'
        '"videoId":"xyz789"something"title":{"runs":[{"text":"Scrape Video"}]}'
    )
    mock_resp.headers = {"content-type": "text/html"}
    mock_req.return_value = mock_resp

    videos = fetch_trending_videos(region="US", max_results=5)
    assert isinstance(videos, list)
