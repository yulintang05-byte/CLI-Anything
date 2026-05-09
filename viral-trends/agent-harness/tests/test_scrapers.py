"""Unit tests for scrapers — mocks yt-dlp subprocess to avoid network calls."""
import json
import pytest
from unittest.mock import patch, MagicMock

from cli_anything.viral_trends import youtube_scraper as yt
from cli_anything.viral_trends import tiktok_scraper as tt


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

YT_PLAYLIST_RESPONSE = {
    "entries": [
        {
            "id": "abc123",
            "title": "Best #workout tips #fitness",
            "channel": "FitChannel",
            "view_count": 500000,
            "duration": 600,
            "tags": ["gym", "fitness"],
            "description": "Top #gym moves for #gains",
            "thumbnail": "https://example.com/thumb.jpg",
        },
        {
            "id": "def456",
            "title": "#motivation daily grind",
            "channel": "MotiveCo",
            "view_count": 300000,
            "duration": 300,
            "tags": ["motivation"],
            "description": "Stay motivated #hustle #grind",
            "thumbnail": "https://example.com/thumb2.jpg",
        },
    ]
}

TT_PLAYLIST_RESPONSE = {
    "entries": [
        {
            "id": "tt001",
            "title": "Amazing #fitness #gym routine",
            "uploader": "@fitguru",
            "like_count": 150000,
            "view_count": 2000000,
            "track": "Levitating",
            "artist": "Dua Lipa",
            "description": "#fitness #gym #gains",
            "url": "https://www.tiktok.com/@fitguru/video/tt001",
        },
        {
            "id": "tt002",
            "title": "#gym day #fitness vibes",
            "uploader": "@gymlife",
            "like_count": 90000,
            "view_count": 1200000,
            "track": "As It Was",
            "artist": "Harry Styles",
            "description": "#gym #fitness #workout",
            "url": "https://www.tiktok.com/@gymlife/video/tt002",
        },
    ]
}


def _mock_run(response_dict):
    """Return a mock subprocess.run that outputs JSON."""
    mock = MagicMock()
    mock.returncode = 0
    mock.stdout = json.dumps(response_dict)
    mock.stderr = ""
    return mock


# ---------------------------------------------------------------------------
# YouTube scraper tests
# ---------------------------------------------------------------------------

class TestYouTubeScraper:

    @patch("subprocess.run")
    def test_fetch_trending_returns_list(self, mock_run):
        mock_run.return_value = _mock_run(YT_PLAYLIST_RESPONSE)
        results = yt.fetch_trending(category="general", limit=5)
        assert isinstance(results, list)
        assert len(results) == 2

    @patch("subprocess.run")
    def test_fetch_trending_has_required_keys(self, mock_run):
        mock_run.return_value = _mock_run(YT_PLAYLIST_RESPONSE)
        results = yt.fetch_trending()
        for item in results:
            for key in ("id", "title", "channel", "views", "hashtags", "url"):
                assert key in item, f"Missing key: {key}"

    @patch("subprocess.run")
    def test_fetch_trending_extracts_hashtags(self, mock_run):
        mock_run.return_value = _mock_run(YT_PLAYLIST_RESPONSE)
        results = yt.fetch_trending()
        # First video has #workout, #fitness in title and #gym, #gains in desc
        first_tags = results[0]["hashtags"]
        assert "fitness" in first_tags or "workout" in first_tags

    @patch("subprocess.run")
    def test_fetch_trending_ytdlp_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="rate limited", stdout="")
        with pytest.raises(RuntimeError, match="YouTube scrape failed"):
            yt.fetch_trending()

    @patch("subprocess.run")
    def test_top_hashtags_ranked(self, mock_run):
        mock_run.return_value = _mock_run(YT_PLAYLIST_RESPONSE)
        tags = yt.top_hashtags_from_trending()
        assert isinstance(tags, list)
        assert all("hashtag" in t and "frequency" in t for t in tags)
        # Verify sorted descending
        freqs = [t["frequency"] for t in tags]
        assert freqs == sorted(freqs, reverse=True)

    @patch("subprocess.run")
    def test_fetch_trending_skips_none_entries(self, mock_run):
        response = {"entries": [None, YT_PLAYLIST_RESPONSE["entries"][0]]}
        mock_run.return_value = _mock_run(response)
        results = yt.fetch_trending()
        assert len(results) == 1


# ---------------------------------------------------------------------------
# TikTok scraper tests
# ---------------------------------------------------------------------------

class TestTikTokScraper:

    @patch("subprocess.run")
    def test_fetch_hashtag_videos_returns_list(self, mock_run):
        mock_run.return_value = _mock_run(TT_PLAYLIST_RESPONSE)
        results = tt.fetch_hashtag_videos("fitness", limit=5)
        assert isinstance(results, list)
        assert len(results) == 2

    @patch("subprocess.run")
    def test_fetch_hashtag_videos_has_required_keys(self, mock_run):
        mock_run.return_value = _mock_run(TT_PLAYLIST_RESPONSE)
        results = tt.fetch_hashtag_videos("fitness")
        for item in results:
            for key in ("id", "title", "author", "likes", "plays", "hashtags", "music", "url"):
                assert key in item, f"Missing key: {key}"

    @patch("subprocess.run")
    def test_fetch_hashtag_extracts_music(self, mock_run):
        mock_run.return_value = _mock_run(TT_PLAYLIST_RESPONSE)
        results = tt.fetch_hashtag_videos("fitness")
        assert results[0]["music"] == "Levitating"
        assert results[0]["music_author"] == "Dua Lipa"

    @patch("subprocess.run")
    def test_fetch_hashtag_extracts_tags(self, mock_run):
        mock_run.return_value = _mock_run(TT_PLAYLIST_RESPONSE)
        results = tt.fetch_hashtag_videos("fitness")
        assert "fitness" in results[0]["hashtags"]
        assert "gym" in results[0]["hashtags"]

    @patch("subprocess.run")
    def test_fetch_hashtag_ytdlp_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="blocked", stdout="")
        with pytest.raises(RuntimeError, match="TikTok hashtag scrape failed"):
            tt.fetch_hashtag_videos("fitness")

    @patch("subprocess.run")
    def test_aggregate_hashtags_ranked(self, mock_run):
        mock_run.return_value = _mock_run(TT_PLAYLIST_RESPONSE)
        videos = tt.fetch_hashtag_videos("fitness")
        tags = tt.aggregate_hashtags(videos)
        assert isinstance(tags, list)
        freqs = [t["frequency"] for t in tags]
        assert freqs == sorted(freqs, reverse=True)

    @patch("subprocess.run")
    def test_fetch_trending_sounds(self, mock_run):
        mock_run.return_value = _mock_run(TT_PLAYLIST_RESPONSE)
        videos = tt.fetch_hashtag_videos("fitness")
        sounds = tt.fetch_trending_sounds_from_videos(videos)
        # Both videos have different tracks
        assert len(sounds) == 2
        track_names = [s["music"] for s in sounds]
        assert "Levitating" in track_names

    def test_fetch_trending_sounds_filters_original(self):
        videos = [
            {"music": "original sound", "music_author": "", "hashtags": []},
            {"music": "Hot Song", "music_author": "Artist X", "hashtags": []},
        ]
        sounds = tt.fetch_trending_sounds_from_videos(videos)
        assert all(s["music"] != "original sound" for s in sounds)

    def test_aggregate_hashtags_empty(self):
        tags = tt.aggregate_hashtags([])
        assert tags == []

    def test_fetch_trending_sounds_deduplicates(self):
        videos = [
            {"music": "Hot Song", "music_author": "Artist X", "hashtags": []},
            {"music": "Hot Song", "music_author": "Artist X", "hashtags": []},
            {"music": "Other Song", "music_author": "Artist Y", "hashtags": []},
        ]
        sounds = tt.fetch_trending_sounds_from_videos(videos)
        hot = [s for s in sounds if s["music"] == "Hot Song"]
        assert len(hot) == 1
        assert hot[0]["frequency"] == 2
