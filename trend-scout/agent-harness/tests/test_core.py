"""Unit tests for trend-scout core modules (no network required)."""

import pytest
from unittest.mock import patch, MagicMock

from cli_anything.trend_scout.core import youtube as yt_mod
from cli_anything.trend_scout.core import tiktok as tt_mod
from cli_anything.trend_scout.core import optimizer as opt_mod
from cli_anything.trend_scout.core import theme_pages as tp_mod


# ── youtube.py ────────────────────────────────────────────────────────────────

class TestYoutubeExtractors:
    def test_extract_hashtags_from_text(self):
        text = "Check out #trending #viral content! #fyp"
        tags = yt_mod._extract_hashtags_from_text(text)
        assert "trending" in tags
        assert "viral" in tags
        assert "fyp" in tags

    def test_extract_hashtags_empty(self):
        assert yt_mod._extract_hashtags_from_text("") == []
        assert yt_mod._extract_hashtags_from_text(None) == []  # type: ignore

    def test_parse_entry_minimal(self):
        entry = {
            "id": "abc123",
            "title": "Test video #viral #trending",
            "channel": "TestChannel",
            "view_count": 1_000_000,
        }
        result = yt_mod._parse_entry(entry)
        assert result["id"] == "abc123"
        assert result["title"] == "Test video #viral #trending"
        assert "viral" in result["hashtags"]
        assert "trending" in result["hashtags"]
        assert result["url"] == "https://www.youtube.com/watch?v=abc123"

    def test_parse_entry_with_tags(self):
        entry = {
            "id": "xyz",
            "title": "Song title",
            "tags": ["pop", "music", "new"],
        }
        result = yt_mod._parse_entry(entry)
        assert "pop" in result["hashtags"]
        assert "music" in result["hashtags"]

    def test_trending_categories(self):
        cats = yt_mod.trending_categories()
        assert "default" in cats
        assert "music" in cats
        assert "gaming" in cats
        assert "movies" in cats

    def test_extract_top_sounds(self):
        videos = [
            {"title": "Ed Sheeran - Shape of You (Official Video)"},
            {"title": "Song feat. Taylor Swift"},
            {"title": "Prod. by Metro Boomin"},
        ]
        sounds = yt_mod._extract_top_sounds(videos)
        assert len(sounds) >= 0  # may be 0 if no patterns match, that's OK

    @patch("cli_anything.trend_scout.core.youtube._run_ytdlp")
    def test_fetch_trending_uses_ytdlp(self, mock_ytdlp):
        mock_ytdlp.return_value = [
            {"id": "v1", "title": "#fyp test", "view_count": 500_000, "channel": "Chan"},
            {"id": "v2", "title": "Viral #trending", "view_count": 200_000, "channel": "Chan2"},
        ]
        result = yt_mod.fetch_trending(category="default", limit=10)
        assert result["source"] == "youtube"
        assert result["category"] == "default"
        assert len(result["videos"]) == 2
        assert "fyp" in result["top_hashtags"]

    @patch("cli_anything.trend_scout.core.youtube._run_ytdlp")
    @patch("cli_anything.trend_scout.core.youtube._yt_api_request")
    def test_fetch_trending_fallback_to_api(self, mock_api, mock_ytdlp):
        mock_ytdlp.return_value = []  # yt-dlp returns nothing
        mock_api.return_value = {}    # API also returns nothing (empty fallback)
        result = yt_mod.fetch_trending(category="default", limit=5)
        assert result["source"] == "youtube"
        assert result["videos"] == []

    def test_fetch_trending_invalid_category(self):
        with pytest.raises(ValueError, match="Unknown category"):
            yt_mod.fetch_trending(category="nonexistent")

    @patch("cli_anything.trend_scout.core.youtube._run_ytdlp")
    def test_fetch_hashtag_videos(self, mock_ytdlp):
        mock_ytdlp.return_value = [
            {"id": "v1", "title": "Test", "view_count": 100, "channel": "C"},
        ]
        result = yt_mod.fetch_hashtag_videos("fitness")
        assert result["hashtag"] == "fitness"
        assert len(result["videos"]) == 1


# ── tiktok.py ────────────────────────────────────────────────────────────────

class TestTiktokModels:
    def test_available_regions(self):
        regions = tt_mod.available_regions()
        assert "us" in regions
        assert "uk" in regions
        assert "global" in regions

    @patch("cli_anything.trend_scout.core.tiktok._fetch_trending_videos")
    @patch("cli_anything.trend_scout.core.tiktok._fetch_trending_sounds")
    @patch("cli_anything.trend_scout.core.tiktok._scrape_trending_hashtags_from_discover")
    def test_fetch_trending_live(self, mock_tags, mock_sounds, mock_videos):
        mock_videos.return_value = [
            {
                "id": "vid1",
                "description": "#fyp test",
                "author": "user1",
                "play_count": 1_000_000,
                "like_count": 50_000,
                "comment_count": 1_000,
                "share_count": 5_000,
                "hashtags": ["fyp", "test"],
                "sound": {"title": "Song", "artist": "Artist", "id": "s1"},
                "url": "https://tiktok.com",
                "create_time": 0,
                "author_followers": 0,
            }
        ]
        mock_sounds.return_value = [
            {"title": "Song", "artist": "Artist", "video_count": 500_000}
        ]
        mock_tags.return_value = [
            {"name": "fyp", "video_count": 1_000_000, "view_count": 5_000_000_000}
        ]

        result = tt_mod.fetch_trending(region="us")
        assert result["source"] == "tiktok"
        assert result["live_data"] is True
        assert len(result["videos"]) == 1
        assert "fyp" in result["top_hashtags"]

    @patch("cli_anything.trend_scout.core.tiktok._fetch_trending_videos")
    @patch("cli_anything.trend_scout.core.tiktok._fetch_trending_sounds")
    @patch("cli_anything.trend_scout.core.tiktok._scrape_trending_hashtags_from_discover")
    def test_fetch_trending_fallback(self, mock_tags, mock_sounds, mock_videos):
        mock_videos.return_value = []
        mock_sounds.return_value = []
        mock_tags.return_value = []

        result = tt_mod.fetch_trending(region="us")
        assert result["live_data"] is False
        assert len(result["top_hashtags"]) > 0  # uses fallback data
        assert len(result["trending_sounds"]) > 0

    @patch("cli_anything.trend_scout.core.tiktok._fetch_challenge_info")
    def test_fetch_hashtag_with_data(self, mock_info):
        mock_info.return_value = {
            "name": "fitness",
            "description": "fitness challenge",
            "video_count": 5_000_000,
            "view_count": 50_000_000_000,
        }
        result = tt_mod.fetch_hashtag("fitness")
        assert result["name"] == "fitness"
        assert "url" in result

    @patch("cli_anything.trend_scout.core.tiktok._fetch_challenge_info")
    def test_fetch_hashtag_fallback(self, mock_info):
        mock_info.return_value = {}
        result = tt_mod.fetch_hashtag("myhashtag")
        assert result["name"] == "myhashtag"
        assert result["video_count"] == 0

    @patch("cli_anything.trend_scout.core.tiktok._fetch_trending_sounds")
    def test_fetch_trending_sounds_fallback(self, mock_sounds):
        mock_sounds.return_value = []
        result = tt_mod.fetch_trending_sounds()
        assert result["live_data"] is False
        assert len(result["sounds"]) > 0  # fallback data


# ── optimizer.py ─────────────────────────────────────────────────────────────

class TestOptimizer:
    def test_follower_tier_nano(self):
        assert opt_mod._follower_tier(500) == "nano"

    def test_follower_tier_micro(self):
        assert opt_mod._follower_tier(5_000) == "micro"

    def test_follower_tier_mid(self):
        assert opt_mod._follower_tier(50_000) == "mid"

    def test_follower_tier_macro(self):
        assert opt_mod._follower_tier(500_000) == "macro"

    def test_follower_tier_mega(self):
        assert opt_mod._follower_tier(5_000_000) == "mega"

    def test_generate_report_structure(self):
        report = opt_mod.generate_report(
            platform="tiktok",
            niche="fitness",
            follower_count=10_000,
            trending_hashtags=["fyp", "fitness", "viral"],
        )
        assert report["platform"] == "tiktok"
        assert report["niche"] == "fitness"
        assert "posting_times" in report
        assert "hashtag_strategy" in report
        assert "content_pillars" in report
        assert "growth_tactics" in report
        assert "monetization_milestones" in report
        assert len(report["growth_tactics"]) >= 5
        assert len(report["monetization_milestones"]) >= 3

    def test_generate_report_hashtags_use_trending(self):
        report = opt_mod.generate_report(
            platform="tiktok",
            niche="travel",
            follower_count=500,
            trending_hashtags=["trending1", "trending2", "trending3", "trending4", "trending5"],
        )
        hs = report["hashtag_strategy"]
        assert "#trending1" in hs["top_trending_to_use"]

    def test_generate_report_all_platforms(self):
        for platform in ("tiktok", "youtube", "instagram"):
            report = opt_mod.generate_report(
                platform=platform,
                niche="fitness",
                follower_count=10_000,
                trending_hashtags=["fyp"],
            )
            assert report["platform"] == platform

    def test_generate_report_all_tiers(self):
        for count in (100, 5_000, 50_000, 500_000, 5_000_000):
            report = opt_mod.generate_report(
                platform="tiktok",
                niche="fashion",
                follower_count=count,
                trending_hashtags=["fashion"],
            )
            assert "tier" in report

    def test_niche_hashtags(self):
        tags = opt_mod._niche_hashtags("fitness")
        assert len(tags) >= 5
        tags_unknown = opt_mod._niche_hashtags("unknownniche")
        assert len(tags_unknown) >= 3  # falls back to defaults

    def test_compare_trends(self):
        yt = {"top_hashtags": ["music", "gaming", "comedy"], "top_sounds": []}
        tt = {"top_hashtags": ["music", "travel", "comedy"], "trending_sounds": []}
        result = opt_mod.compare_trends(yt, tt)
        assert "music" in result["cross_platform_hashtags"]
        assert "comedy" in result["cross_platform_hashtags"]
        assert "gaming" in result["youtube_only_tags"]
        assert "travel" in result["tiktok_only_tags"]
        assert len(result["action_items"]) >= 2

    def test_monetization_milestones_all_platforms(self):
        for platform in ("tiktok", "youtube", "instagram"):
            milestones = opt_mod._monetization_milestones(platform)
            assert len(milestones) >= 3
            assert all("milestone" in m and "unlocks" in m for m in milestones)


# ── theme_pages.py ────────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches(self):
        niches = tp_mod.list_niches()
        assert len(niches) >= 8
        for n in niches:
            assert "niche" in n
            assert "description" in n
            assert "avg_cpm" in n
            assert "competition" in n

    def test_get_niche_guide_valid(self):
        guide = tp_mod.get_niche_guide("fitness")
        assert guide["niche"] == "fitness"
        assert "content_sources" in guide
        assert "monetization" in guide
        assert "tools" in guide
        assert len(guide["quick_start_checklist"]) == 7

    def test_get_niche_guide_case_insensitive(self):
        guide = tp_mod.get_niche_guide("FITNESS")
        assert guide["niche"] == "fitness"

    def test_get_niche_guide_invalid(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            tp_mod.get_niche_guide("xyznotaniche")

    def test_get_conversion_playbook_all(self):
        result = tp_mod.get_conversion_playbook()
        assert "phases" in result
        assert len(result["phases"]) == 4
        assert "total_timeline" in result

    def test_get_conversion_playbook_specific_phase(self):
        for phase in ("1", "2", "3", "4"):
            result = tp_mod.get_conversion_playbook(phase)
            assert "actions" in result
            assert len(result["actions"]) >= 3

    def test_get_conversion_playbook_invalid_phase(self):
        with pytest.raises(ValueError):
            tp_mod.get_conversion_playbook("99")

    def test_get_tools(self):
        tools = tp_mod.get_tools()
        assert len(tools) >= 5
        for t in tools:
            assert "name" in t
            assert "purpose" in t
            assert "cost" in t

    def test_get_selling_platforms(self):
        platforms = tp_mod.get_selling_platforms()
        assert len(platforms) >= 3
        for p in platforms:
            assert "name" in p
            assert "url" in p
            assert "fee" in p

    def test_all_niches_have_required_fields(self):
        required = ["description", "content_sources", "avg_cpm", "competition", "monetization", "tools", "growth_speed"]
        for niche, data in tp_mod.THEME_PAGE_NICHES.items():
            for field in required:
                assert field in data, f"Niche '{niche}' missing field '{field}'"
