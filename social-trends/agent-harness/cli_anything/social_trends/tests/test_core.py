"""Unit tests — all HTTP calls mocked, no real API keys needed."""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from cli_anything.social_trends.core import optimizer, theme_page
from cli_anything.social_trends.core.tiktok import (
    extract_top_hashtags,
    get_trending_hashtags_unofficial,
    get_trending_sounds_unofficial,
    get_trending_videos_unofficial,
    _normalize_official,
)
from cli_anything.social_trends.core.youtube import (
    extract_top_hashtags as yt_extract_hashtags,
    _extract_hashtags,
)


# ── TikTok unit tests ────────────────────────────────────────────────────────

class TestTikTokScraper(unittest.TestCase):
    def _mock_fyp_response(self):
        return {
            "itemList": [
                {
                    "id": "111",
                    "desc": "#viral #trending something cool",
                    "author": {"uniqueId": "creator1"},
                    "stats": {"diggCount": 5000, "commentCount": 200, "shareCount": 100, "playCount": 100000},
                    "music": {"id": "m1", "title": "Hit Song", "authorName": "Artist A", "original": False, "duration": 30},
                },
                {
                    "id": "222",
                    "desc": "#fyp #viral new clip",
                    "author": {"uniqueId": "creator2"},
                    "stats": {"diggCount": 2000, "commentCount": 50, "shareCount": 30, "playCount": 40000},
                    "music": {"id": "m1", "title": "Hit Song", "authorName": "Artist A", "original": False, "duration": 30},
                },
                {
                    "id": "333",
                    "desc": "#dance only vibes",
                    "author": {"uniqueId": "creator3"},
                    "stats": {"diggCount": 8000, "commentCount": 300, "shareCount": 200, "playCount": 200000},
                    "music": {"id": "m2", "title": "Dance Track", "authorName": "Artist B", "original": False, "duration": 15},
                },
            ]
        }

    def _mock_discover_response(self):
        return {
            "challengeList": [
                {
                    "challengeInfo": {
                        "challenge": {"title": "viral"},
                        "statsV2": {"videoCount": "10000", "viewCount": "500000000"},
                    }
                },
                {
                    "challengeInfo": {
                        "challenge": {"title": "fyp"},
                        "statsV2": {"videoCount": "8000", "viewCount": "300000000"},
                    }
                },
            ]
        }

    @patch("cli_anything.social_trends.core.tiktok._http_get_json")
    def test_trending_videos_unofficial(self, mock_get):
        mock_get.return_value = self._mock_fyp_response()
        videos = get_trending_videos_unofficial(count=3)
        self.assertEqual(len(videos), 3)
        # Sorted by view_count descending
        self.assertGreaterEqual(videos[0]["view_count"], videos[1]["view_count"])

    @patch("cli_anything.social_trends.core.tiktok._http_get_json")
    def test_trending_sounds_deduplication(self, mock_get):
        mock_get.return_value = self._mock_fyp_response()
        sounds = get_trending_sounds_unofficial(count=10)
        # m1 appears twice → video_count=2, m2 once → video_count=1
        ids = {s["music_id"]: s["video_count"] for s in sounds}
        self.assertEqual(ids.get("m1"), 2)
        self.assertEqual(ids.get("m2"), 1)

    @patch("cli_anything.social_trends.core.tiktok._http_get_json")
    def test_trending_hashtags_unofficial(self, mock_get):
        mock_get.return_value = self._mock_discover_response()
        tags = get_trending_hashtags_unofficial(count=10)
        self.assertEqual(tags[0]["hashtag"], "#viral")
        self.assertGreater(tags[0]["view_count"], tags[1]["view_count"])

    def test_extract_top_hashtags(self):
        videos = [
            {"hashtags": ["#viral", "#trending", "#viral"]},
            {"hashtags": ["#viral", "#fyp"]},
        ]
        top = extract_top_hashtags(videos, top_n=5)
        self.assertEqual(top[0]["hashtag"], "#viral")
        self.assertEqual(top[0]["count"], 3)

    def test_normalize_official(self):
        raw = [
            {
                "id": "999",
                "username": "user1",
                "video_description": "test",
                "hashtag_names": ["dance", "fyp"],
                "like_count": 100,
                "comment_count": 10,
                "share_count": 5,
                "view_count": 10000,
                "music_id": "abc",
                "create_time": "1700000000",
            }
        ]
        result = _normalize_official(raw)
        self.assertEqual(result[0]["hashtags"], ["#dance", "#fyp"])
        self.assertEqual(result[0]["source"], "official_api")

    @patch("cli_anything.social_trends.core.tiktok._http_get_json")
    def test_empty_fyp_response(self, mock_get):
        mock_get.return_value = {"itemList": []}
        videos = get_trending_videos_unofficial()
        self.assertEqual(videos, [])


# ── YouTube unit tests ───────────────────────────────────────────────────────

class TestYouTubeScraper(unittest.TestCase):
    def test_extract_hashtags_from_text(self):
        text = "Check out #viral content #MusicMonday #trending2025 today"
        tags = _extract_hashtags(text)
        self.assertIn("#viral", tags)
        self.assertIn("#MusicMonday", tags)
        self.assertIn("#trending2025", tags)

    def test_extract_top_hashtags_aggregation(self):
        videos = [
            {"hashtags": ["#tutorial", "#coding"], "tags": ["python", "learn"]},
            {"hashtags": ["#tutorial", "#coding"], "tags": ["python"]},
            {"hashtags": ["#viral"], "tags": []},
        ]
        top = yt_extract_hashtags(videos, top_n=5)
        # #tutorial and #coding should be top
        top_hashtags = [t["hashtag"] for t in top]
        self.assertIn("#tutorial", top_hashtags)
        self.assertIn("#coding", top_hashtags)

    def test_no_api_key_raises(self):
        import os
        old = os.environ.pop("YOUTUBE_API_KEY", None)
        try:
            from cli_anything.social_trends.core.youtube import _api_key
            with self.assertRaises(RuntimeError):
                _api_key()
        finally:
            if old:
                os.environ["YOUTUBE_API_KEY"] = old


# ── Optimizer unit tests ─────────────────────────────────────────────────────

class TestOptimizer(unittest.TestCase):
    def test_engagement_rate_calculation(self):
        rate = optimizer.engagement_rate(1000, 100, 50, 10000)
        # (1000 + 200 + 150) / 10000 * 100 = 13.5
        self.assertAlmostEqual(rate, 13.5, places=2)

    def test_engagement_rate_zero_views(self):
        self.assertEqual(optimizer.engagement_rate(100, 10, 5, 0), 0.0)

    def test_score_trending_videos_sorted(self):
        videos = [
            {"view_count": 1000, "like_count": 10, "comment_count": 1, "share_count": 0},
            {"view_count": 1000, "like_count": 500, "comment_count": 50, "share_count": 25},
        ]
        scored = optimizer.score_trending_videos(videos)
        self.assertGreater(scored[0]["engagement_rate"], scored[1]["engagement_rate"])

    def test_build_hashtag_set_respects_limit(self):
        trending = [{"hashtag": f"#trend{i}"} for i in range(50)]
        niche = ["#myniche", "#custom"]
        result = optimizer.build_hashtag_set(trending, niche, "tiktok")
        self.assertLessEqual(len(result), 5)  # TikTok limit = 5

    def test_build_hashtag_set_deduplication(self):
        trending = [{"hashtag": "#viral"}, {"hashtag": "#fyp"}]
        niche = ["viral", "dance"]
        result = optimizer.build_hashtag_set(trending, niche, "instagram")
        self.assertEqual(len(result), len(set(result)))

    def test_best_posting_times_returns_platform(self):
        result = optimizer.get_best_posting_times("tiktok")
        self.assertEqual(result["platform"], "tiktok")
        self.assertIn("best_hours_utc", result)
        self.assertIn("cadence", result)

    def test_get_profile_checklist_not_empty(self):
        for p in ["tiktok", "youtube", "instagram"]:
            items = optimizer.get_profile_checklist(p)
            self.assertIsInstance(items, list)
            self.assertGreater(len(items), 0)

    def test_generate_caption_hooks(self):
        hooks = optimizer.generate_caption_hooks("fitness", count=3)
        self.assertEqual(len(hooks), 3)
        for h in hooks:
            self.assertIn("fitness", h)


# ── Theme page unit tests ────────────────────────────────────────────────────

class TestThemePage(unittest.TestCase):
    def test_niches_structure(self):
        for niche in theme_page.NICHES:
            self.assertIn("niche", niche)
            self.assertIn("monetization", niche)
            self.assertIn("avg_cpm", niche)

    def test_growth_playbook_phases(self):
        phases = theme_page.GROWTH_PLAYBOOK
        self.assertGreaterEqual(len(phases), 4)
        for p in phases:
            self.assertIn("phase", p)
            self.assertIn("tactics", p)
            self.assertIsInstance(p["tactics"], list)

    def test_monetization_methods_structure(self):
        for m in theme_page.MONETIZATION_METHODS:
            self.assertIn("method", m)
            self.assertIn("earnings", m)

    def test_get_niche_recommendations_keyword(self):
        results = theme_page.get_niche_recommendations(["fitness"])
        self.assertTrue(any("Fitness" in n["niche"] for n in results))

    def test_get_niche_recommendations_fallback(self):
        results = theme_page.get_niche_recommendations(["xyzunknown999"])
        self.assertGreater(len(results), 0)

    def test_get_full_playbook_keys(self):
        playbook = theme_page.get_full_playbook()
        self.assertIn("niches", playbook)
        self.assertIn("growth_playbook", playbook)
        self.assertIn("monetization_methods", playbook)
        self.assertIn("content_sourcing", playbook)

    def test_content_sourcing_has_license(self):
        for source in theme_page.CONTENT_SOURCING:
            self.assertIn("license", source)
            self.assertIn("url", source)


if __name__ == "__main__":
    unittest.main()
