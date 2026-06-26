"""Tests for TikTok module — unit tests using synthetic data."""

import pytest
from cli_anything.social_trends.core.tiktok import (
    _parse_hashtag_response,
    _parse_music_response,
    _parse_creators_response,
    analyze_niche_hashtags,
    COUNTRY_CODES,
    PERIOD_OPTIONS,
)


class TestParseHashtagResponse:
    def _make_response(self, hashtags):
        return {
            "data": {
                "list": [
                    {
                        "hashtag_name": h,
                        "rank": i + 1,
                        "video_views": (10 - i) * 100_000,
                        "publish_cnt": (10 - i) * 1000,
                        "trend": "up" if i < 5 else "stable",
                        "core_hashtag_list": ["related1", "related2"],
                    }
                    for i, h in enumerate(hashtags)
                ]
            }
        }

    def test_parses_basic_hashtags(self):
        resp = self._make_response(["fitness", "gym", "workout"])
        result = _parse_hashtag_response(resp, "US", 7)
        assert result["total"] == 3
        assert result["hashtags"][0]["hashtag"] == "#fitness"

    def test_adds_hash_prefix(self):
        resp = self._make_response(["crypto"])
        result = _parse_hashtag_response(resp, "US", 7)
        assert result["hashtags"][0]["hashtag"].startswith("#")

    def test_source_and_region(self):
        result = _parse_hashtag_response({"data": {"list": []}}, "GB", 30)
        assert result["source"] == "tiktok_creative_center"
        assert result["region"] == "GB"
        assert result["period_days"] == 30

    def test_empty_response(self):
        result = _parse_hashtag_response({"data": {"list": []}}, "US", 7)
        assert result["total"] == 0

    def test_none_data_response(self):
        result = _parse_hashtag_response({}, "US", 7)
        assert result["total"] == 0

    def test_related_hashtags_capped(self):
        resp = self._make_response(["fitness"])
        resp["data"]["list"][0]["core_hashtag_list"] = [f"tag{i}" for i in range(20)]
        result = _parse_hashtag_response(resp, "US", 7)
        assert len(result["hashtags"][0]["related_hashtags"]) <= 5


class TestParseMusicResponse:
    def _make_music_response(self, tracks):
        return {
            "data": {
                "list": [
                    {
                        "rank": i + 1,
                        "music_name": t["title"],
                        "author": t["artist"],
                        "clip_count": t.get("clips", 10000),
                        "duration": 30,
                        "music_id": f"music_{i}",
                        "cover_url": "https://example.com/cover.jpg",
                        "trend": "up",
                    }
                    for i, t in enumerate(tracks)
                ]
            }
        }

    def test_parses_basic_tracks(self):
        resp = self._make_music_response([
            {"title": "Song A", "artist": "Artist A", "clips": 500_000},
            {"title": "Song B", "artist": "Artist B", "clips": 200_000},
        ])
        result = _parse_music_response(resp, "US", 7)
        assert result["total"] == 2
        assert result["sounds"][0]["title"] == "Song A"
        assert result["sounds"][0]["artist"] == "Artist A"

    def test_clip_count_parsed(self):
        resp = self._make_music_response([{"title": "Hit", "artist": "Pop Star", "clips": 1_000_000}])
        result = _parse_music_response(resp, "US", 7)
        assert result["sounds"][0]["clip_count"] == 1_000_000

    def test_empty_response(self):
        result = _parse_music_response({"data": {"list": []}}, "US", 7)
        assert result["total"] == 0

    def test_source_field(self):
        result = _parse_music_response({}, "US", 7)
        assert result["source"] == "tiktok_creative_center"

    def test_duration_parsed(self):
        resp = self._make_music_response([{"title": "X", "artist": "Y"}])
        result = _parse_music_response(resp, "US", 7)
        assert result["sounds"][0]["duration_sec"] == 30


class TestParseCreatorsResponse:
    def _make_creators_response(self, creators):
        return {
            "data": {
                "list": [
                    {
                        "rank": i + 1,
                        "nick_name": c["nickname"],
                        "follower_cnt": c.get("followers", 10000),
                        "follower_growth_rate": c.get("growth", 5.0),
                        "avg_views": c.get("avg_views", 50000),
                        "category_name": c.get("niche", "Lifestyle"),
                        "bio_description": c.get("bio", "Creator bio"),
                        "unique_id": c["nickname"].replace("@", ""),
                    }
                    for i, c in enumerate(creators)
                ]
            }
        }

    def test_parses_basic_creators(self):
        resp = self._make_creators_response([
            {"nickname": "fitnessguru", "followers": 500_000},
            {"nickname": "travelblogger", "followers": 100_000},
        ])
        result = _parse_creators_response(resp, "US", 7)
        assert result["total"] == 2
        assert result["creators"][0]["nickname"] == "fitnessguru"

    def test_url_constructed(self):
        resp = self._make_creators_response([{"nickname": "testuser"}])
        result = _parse_creators_response(resp, "US", 7)
        assert "tiktok.com/@testuser" in result["creators"][0]["url"]

    def test_empty_response(self):
        result = _parse_creators_response({}, "US", 7)
        assert result["total"] == 0


class TestAnalyzeNicheHashtags:
    def test_filters_relevant_hashtags(self, monkeypatch):
        mock_data = {
            "hashtags": [
                {"hashtag": "#fitness", "video_count": 1000, "post_count": 500, "trend": "up", "related_hashtags": []},
                {"hashtag": "#cooking", "video_count": 800, "post_count": 400, "trend": "stable", "related_hashtags": []},
                {"hashtag": "#gym", "video_count": 600, "post_count": 300, "trend": "up", "related_hashtags": []},
            ]
        }

        from cli_anything.social_trends.core import tiktok as tt_mod
        monkeypatch.setattr(tt_mod, "fetch_trending_hashtags", lambda **kwargs: mock_data)

        result = analyze_niche_hashtags(["fitness", "gym"], region="US", period_days=7)
        niche_tags = [h["hashtag"] for h in result["niche_hashtags"]]
        assert "#fitness" in niche_tags
        assert "#gym" in niche_tags
        assert "#cooking" not in niche_tags

    def test_recommendation_present(self, monkeypatch):
        from cli_anything.social_trends.core import tiktok as tt_mod
        monkeypatch.setattr(tt_mod, "fetch_trending_hashtags", lambda **kwargs: {"hashtags": []})

        result = analyze_niche_hashtags(["travel"], region="US")
        assert "recommendation" in result

    def test_keywords_recorded(self, monkeypatch):
        from cli_anything.social_trends.core import tiktok as tt_mod
        monkeypatch.setattr(tt_mod, "fetch_trending_hashtags", lambda **kwargs: {"hashtags": []})

        result = analyze_niche_hashtags(["food", "cooking"], region="US")
        assert result["niche_keywords"] == ["food", "cooking"]


class TestConstants:
    def test_country_codes_us(self):
        assert COUNTRY_CODES["US"] == "US"

    def test_country_codes_uk_maps_to_gb(self):
        assert COUNTRY_CODES["UK"] == "GB"

    def test_period_options(self):
        assert 7 in PERIOD_OPTIONS
        assert 30 in PERIOD_OPTIONS
        assert 120 in PERIOD_OPTIONS

    def test_country_codes_not_empty(self):
        assert len(COUNTRY_CODES) >= 10
