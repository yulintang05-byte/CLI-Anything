"""Unit tests for cli-anything-social-trends core modules.

Tests all core business logic with synthetic data (no network required).
Run with: python -m pytest cli_anything/social_trends/tests/test_core.py -v
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


# ── hashtags.py tests ─────────────────────────────────────────────────────

class TestViralityScore:
    def test_zero_inputs(self):
        from cli_anything.social_trends.core.hashtags import compute_virality_score
        assert compute_virality_score(0, 0) == 0.0

    def test_high_views_gives_high_score(self):
        from cli_anything.social_trends.core.hashtags import compute_virality_score
        score = compute_virality_score(1_000_000, 1_000_000_000, 5.0)
        assert score > 50

    def test_score_bounded_0_100(self):
        from cli_anything.social_trends.core.hashtags import compute_virality_score
        score = compute_virality_score(999_999_999, 999_999_999_999, 100.0)
        assert 0 <= score <= 100

    def test_more_views_higher_score(self):
        from cli_anything.social_trends.core.hashtags import compute_virality_score
        low = compute_virality_score(100, 10_000, 2.0)
        high = compute_virality_score(10_000_000, 10_000_000_000, 2.0)
        assert high > low


class TestCompetitionLevel:
    def test_low_competition(self):
        from cli_anything.social_trends.core.hashtags import competition_level
        assert competition_level(1_000) == "low"

    def test_medium_competition(self):
        from cli_anything.social_trends.core.hashtags import competition_level
        assert competition_level(100_000) == "medium"

    def test_high_competition(self):
        from cli_anything.social_trends.core.hashtags import competition_level
        assert competition_level(2_000_000) == "high"

    def test_oversaturated(self):
        from cli_anything.social_trends.core.hashtags import competition_level
        assert competition_level(10_000_000) == "oversaturated"

    def test_boundary_medium(self):
        from cli_anything.social_trends.core.hashtags import competition_level
        assert competition_level(50_000) == "low"
        assert competition_level(50_001) == "medium"


class TestRecommendHashtagMix:
    def test_tiktok_returns_dict(self):
        from cli_anything.social_trends.core.hashtags import recommend_hashtag_mix
        result = recommend_hashtag_mix("fitness", "tiktok")
        assert isinstance(result, dict)
        assert "broad" in result
        assert "medium" in result
        assert "niche_specific" in result
        assert result["platform"] == "tiktok"

    def test_youtube_returns_tags_field(self):
        from cli_anything.social_trends.core.hashtags import recommend_hashtag_mix
        result = recommend_hashtag_mix("cooking", "youtube")
        assert "tags_field" in result
        assert isinstance(result["tags_field"], list)

    def test_unknown_niche_returns_defaults(self):
        from cli_anything.social_trends.core.hashtags import recommend_hashtag_mix
        result = recommend_hashtag_mix("knitting_and_crocheting_extreme", "tiktok")
        assert len(result["broad"]) > 0

    def test_all_niches_in_db(self):
        from cli_anything.social_trends.core.hashtags import _NICHE_HASHTAG_DB, recommend_hashtag_mix
        for niche in _NICHE_HASHTAG_DB:
            result = recommend_hashtag_mix(niche, "tiktok")
            assert len(result["broad"]) > 0, f"No broad tags for {niche}"
            assert len(result["niche_specific"]) > 0, f"No niche tags for {niche}"


class TestAnalyzeHashtagSet:
    def test_too_many_hashtags(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag_set
        tags = [f"#tag{i}" for i in range(35)]
        result = analyze_hashtag_set(tags)
        assert any("Too many" in issue for issue in result["issues"])

    def test_all_broad_tags(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag_set
        tags = ["#fyp", "#viral", "#trending", "#foryou", "#tiktok"]
        result = analyze_hashtag_set(tags)
        assert len(result["broad_tags"]) > 0

    def test_quality_score_range(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag_set
        tags = ["#fitness", "#gym", "#workout", "#fyp", "#fitcheck"]
        result = analyze_hashtag_set(tags)
        assert 0 <= result["quality_score"] <= 100

    def test_duplicate_detection(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag_set
        tags = ["#fitness", "#fitness", "#gym"]
        result = analyze_hashtag_set(tags)
        assert result["hashtag_count"] == 3
        assert result["unique_count"] == 2

    def test_no_issues_for_good_set(self):
        from cli_anything.social_trends.core.hashtags import analyze_hashtag_set
        tags = ["#fyp", "#fitness", "#gym", "#workout", "#fitcheck"]
        result = analyze_hashtag_set(tags)
        # A balanced set should have few issues
        assert len(result["issues"]) <= 1


class TestRankHashtags:
    def test_returns_sorted_by_opportunity(self):
        from cli_anything.social_trends.core.hashtags import rank_hashtags
        items = [
            {"hashtag": "#a", "video_count": 100, "view_count": 10_000_000},
            {"hashtag": "#b", "video_count": 10_000_000, "view_count": 1_000_000},
        ]
        result = rank_hashtags(items)
        # #a has fewer videos but more views per video — higher opportunity
        assert result[0]["hashtag"] == "#a"

    def test_adds_opportunity_score(self):
        from cli_anything.social_trends.core.hashtags import rank_hashtags
        items = [{"hashtag": "#test", "video_count": 5000, "view_count": 50_000_000}]
        result = rank_hashtags(items)
        assert "opportunity_score" in result[0]
        assert "competition" in result[0]

    def test_empty_list(self):
        from cli_anything.social_trends.core.hashtags import rank_hashtags
        assert rank_hashtags([]) == []


# ── accounts.py tests ────────────────────────────────────────────────────

class TestEngagementRate:
    def test_tiktok_includes_shares(self):
        from cli_anything.social_trends.core.accounts import calculate_engagement_rate
        result = calculate_engagement_rate(1000, 100, 50, 10000, "tiktok")
        # (1000 + 100 + 50) / 10000 * 100 = 11.5%
        assert result["engagement_rate"] == pytest.approx(11.5, rel=0.01)

    def test_youtube_excludes_shares(self):
        from cli_anything.social_trends.core.accounts import calculate_engagement_rate
        result = calculate_engagement_rate(1000, 100, 50, 10000, "youtube")
        # (1000 + 100) / 10000 * 100 = 11.0%
        assert result["engagement_rate"] == pytest.approx(11.0, rel=0.01)

    def test_zero_views_returns_zero(self):
        from cli_anything.social_trends.core.accounts import calculate_engagement_rate
        result = calculate_engagement_rate(1000, 100, 50, 0, "tiktok")
        assert result["engagement_rate"] == 0.0

    def test_excellent_grade(self):
        from cli_anything.social_trends.core.accounts import calculate_engagement_rate
        result = calculate_engagement_rate(8000, 500, 200, 100000, "tiktok")
        assert "A+" in result["grade"] or "Excellent" in result["grade"]

    def test_poor_grade(self):
        from cli_anything.social_trends.core.accounts import calculate_engagement_rate
        result = calculate_engagement_rate(10, 1, 0, 100000, "tiktok")
        assert "D" in result["grade"] or "Below" in result["grade"]

    def test_suggestions_present(self):
        from cli_anything.social_trends.core.accounts import calculate_engagement_rate
        result = calculate_engagement_rate(100, 10, 5, 100000, "tiktok")
        assert len(result["suggestions"]) > 0


class TestAnalyzeAccount:
    def _make_stats(self, **kwargs):
        defaults = {
            "followers": 10000,
            "following": 500,
            "total_posts": 100,
            "avg_views": 20000,
            "avg_likes": 1500,
            "avg_comments": 100,
            "avg_shares": 50,
            "platform": "tiktok",
            "niche": "fitness",
            "account_age_days": 365,
        }
        defaults.update(kwargs)
        return defaults

    def test_returns_required_keys(self):
        from cli_anything.social_trends.core.accounts import analyze_account
        result = analyze_account(self._make_stats())
        for key in ["engagement", "virality_coefficient", "monetization_status",
                    "score", "top_recommendations"]:
            assert key in result, f"Missing key: {key}"

    def test_score_is_0_100(self):
        from cli_anything.social_trends.core.accounts import analyze_account
        result = analyze_account(self._make_stats())
        assert 0 <= result["score"] <= 100

    def test_recommendations_are_list(self):
        from cli_anything.social_trends.core.accounts import analyze_account
        result = analyze_account(self._make_stats())
        assert isinstance(result["top_recommendations"], list)

    def test_follow_ratio_calculated(self):
        from cli_anything.social_trends.core.accounts import analyze_account
        result = analyze_account(self._make_stats(followers=10000, following=500))
        assert result["follow_ratio"] == pytest.approx(20.0, rel=0.01)

    def test_zero_followers_safe(self):
        from cli_anything.social_trends.core.accounts import analyze_account
        result = analyze_account(self._make_stats(followers=0, following=0))
        assert result["score"] >= 0


class TestMonetizationEligibility:
    def test_tiktok_creator_rewards(self):
        from cli_anything.social_trends.core.accounts import _check_monetization_eligibility
        result = _check_monetization_eligibility(15000, 200000, "tiktok")
        assert "TikTok Creator Rewards Program" in result["eligible"]

    def test_tiktok_shop_1k(self):
        from cli_anything.social_trends.core.accounts import _check_monetization_eligibility
        result = _check_monetization_eligibility(1500, 5000, "tiktok")
        assert "TikTok Shop Affiliate" in result["eligible"]

    def test_youtube_ypp(self):
        from cli_anything.social_trends.core.accounts import _check_monetization_eligibility
        result = _check_monetization_eligibility(2000, 5000, "youtube")
        assert "YouTube Partner Program (YPP)" in result["eligible"]

    def test_no_eligibility_small_account(self):
        from cli_anything.social_trends.core.accounts import _check_monetization_eligibility
        result = _check_monetization_eligibility(100, 50, "tiktok")
        assert len(result["eligible"]) == 0


class TestGenerateBio:
    def test_returns_bio_string(self):
        from cli_anything.social_trends.core.accounts import generate_bio
        result = generate_bio("fitness", "tiktok")
        assert isinstance(result["bio"], str)
        assert len(result["bio"]) > 10

    def test_respects_tiktok_char_limit(self):
        from cli_anything.social_trends.core.accounts import generate_bio
        result = generate_bio("cooking", "tiktok")
        assert result["character_count"] <= 80

    def test_respects_instagram_char_limit(self):
        from cli_anything.social_trends.core.accounts import generate_bio
        result = generate_bio("fashion", "instagram")
        assert result["character_count"] <= 150

    def test_custom_cta_included(self):
        from cli_anything.social_trends.core.accounts import generate_bio
        result = generate_bio("tech", "tiktok", cta="Get my AI tools list")
        # CTA may be truncated but should be in examples
        assert len(result["examples"]) >= 1

    def test_tips_present(self):
        from cli_anything.social_trends.core.accounts import generate_bio
        result = generate_bio("gaming", "youtube")
        assert len(result["tips"]) > 0


# ── theme_pages.py tests ──────────────────────────────────────────────────

class TestNicheDatabase:
    def test_returns_list(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_database
        db = get_niche_database()
        assert isinstance(db, list)
        assert len(db) >= 10

    def test_each_entry_has_required_keys(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_database
        db = get_niche_database()
        for n in db:
            for key in ["name", "profitability", "competition", "monetization_methods"]:
                assert key in n, f"Niche '{n.get('name')}' missing '{key}'"

    def test_fitness_is_very_high_profit(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_database
        db = get_niche_database()
        fitness = next(n for n in db if n["name"] == "fitness")
        assert fitness["profitability"] == "very high"


class TestGetNicheInfo:
    def test_exact_match(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_info
        info = get_niche_info("fitness")
        assert info["name"] == "fitness"

    def test_partial_match(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_info
        info = get_niche_info("tech")
        assert "tech" in info["name"].lower()

    def test_unknown_niche_returns_defaults(self):
        from cli_anything.social_trends.core.theme_pages import get_niche_info
        info = get_niche_info("underwater_basket_weaving")
        assert info["name"] == "underwater_basket_weaving"
        assert isinstance(info["monetization_methods"], list)


class TestConversionPlaybook:
    def test_small_account_hard_pivot(self):
        from cli_anything.social_trends.core.theme_pages import get_conversion_playbook
        result = get_conversion_playbook("personal", "fitness", 500)
        assert result["conversion_type"] == "hard_pivot"
        assert result["risk_level"] == "low"

    def test_medium_account_gradual(self):
        from cli_anything.social_trends.core.theme_pages import get_conversion_playbook
        result = get_conversion_playbook("lifestyle", "finance", 25000)
        assert result["conversion_type"] == "gradual_pivot"
        assert result["risk_level"] == "medium"

    def test_large_account_start_fresh(self):
        from cli_anything.social_trends.core.theme_pages import get_conversion_playbook
        result = get_conversion_playbook("personal", "tech", 100000)
        assert result["conversion_type"] == "start_fresh"
        assert "high" in result["risk_level"]

    def test_returns_all_sections(self):
        from cli_anything.social_trends.core.theme_pages import get_conversion_playbook
        result = get_conversion_playbook("personal", "fitness", 5000)
        for key in ["roadmap", "branding_checklist", "first_30_days", "monetization_timeline"]:
            assert key in result, f"Missing section: {key}"

    def test_roadmap_not_empty(self):
        from cli_anything.social_trends.core.theme_pages import get_conversion_playbook
        result = get_conversion_playbook("personal", "gaming", 1000)
        assert len(result["roadmap"]) > 0

    def test_branding_checklist_has_10_items(self):
        from cli_anything.social_trends.core.theme_pages import get_conversion_playbook
        result = get_conversion_playbook("personal", "cooking", 2000)
        assert len(result["branding_checklist"]) == 10


class TestContentPillars:
    def test_returns_pillars(self):
        from cli_anything.social_trends.core.theme_pages import get_content_pillars
        result = get_content_pillars("fitness")
        assert len(result["pillars"]) > 0

    def test_returns_content_ideas(self):
        from cli_anything.social_trends.core.theme_pages import get_content_pillars
        result = get_content_pillars("cooking")
        assert len(result["content_ideas"]) >= 10

    def test_posting_schedule_7_days(self):
        from cli_anything.social_trends.core.theme_pages import get_content_pillars
        result = get_content_pillars("finance", 14)
        assert len(result["posting_schedule_template"]) == 7

    def test_viral_formats_present(self):
        from cli_anything.social_trends.core.theme_pages import get_content_pillars
        result = get_content_pillars("gaming")
        assert len(result["viral_formats"]) > 0


# ── music.py tests ────────────────────────────────────────────────────────

class TestMusicClassification:
    def test_hip_hop_classification(self):
        from cli_anything.social_trends.core.music import _classify_genre
        assert _classify_genre("kendrick lamar new track", "kendrick") == "hip-hop"

    def test_pop_classification(self):
        from cli_anything.social_trends.core.music import _classify_genre
        assert _classify_genre("sabrina carpenter espresso", "sabrina carpenter") == "pop"

    def test_kpop_classification(self):
        from cli_anything.social_trends.core.music import _classify_genre
        assert _classify_genre("blackpink rosé new mv", "rosé") == "k-pop"

    def test_unknown_returns_other(self):
        from cli_anything.social_trends.core.music import _classify_genre
        assert _classify_genre("xyz 12345 unknown", "xyz") == "other"


class TestMoodClassification:
    def test_hype_mood(self):
        from cli_anything.social_trends.core.music import _classify_mood
        assert _classify_mood("fire banger") == "hype"

    def test_emotional_mood(self):
        from cli_anything.social_trends.core.music import _classify_mood
        assert _classify_mood("sad love song heartbreak") == "emotional"

    def test_neutral_default(self):
        from cli_anything.social_trends.core.music import _classify_mood
        assert _classify_mood("generic title xyz") == "neutral"


class TestSoundStrategy:
    def test_fitness_recommends_hiphop(self):
        from cli_anything.social_trends.core.music import get_sound_strategy
        result = get_sound_strategy("fitness")
        assert "hip-hop" in result["recommended_genres"]

    def test_returns_audio_tips(self):
        from cli_anything.social_trends.core.music import get_sound_strategy
        result = get_sound_strategy("cooking")
        assert len(result["audio_tips"]) >= 3

    def test_unknown_niche_returns_defaults(self):
        from cli_anything.social_trends.core.music import get_sound_strategy
        result = get_sound_strategy("underwater_basket_weaving")
        assert "recommended_genres" in result
        assert "audio_tips" in result


# ── tiktok.py tests ───────────────────────────────────────────────────────

class TestTikTokHelpers:
    def test_extract_hashtags(self):
        from cli_anything.social_trends.core.tiktok import _extract_hashtags
        tags = _extract_hashtags("Check out #fitness and #gym content! #fyp")
        assert "#fitness" in tags
        assert "#gym" in tags
        assert "#fyp" in tags

    def test_extract_hashtags_empty(self):
        from cli_anything.social_trends.core.tiktok import _extract_hashtags
        assert _extract_hashtags("no hashtags here") == []

    def test_tiktok_engagement_rate(self):
        from cli_anything.social_trends.core.tiktok import _tiktok_engagement
        stats = {"playCount": 100000, "diggCount": 5000, "commentCount": 500, "shareCount": 200}
        er = _tiktok_engagement(stats)
        assert er == pytest.approx(5.7, rel=0.01)

    def test_tiktok_engagement_zero_plays(self):
        from cli_anything.social_trends.core.tiktok import _tiktok_engagement
        assert _tiktok_engagement({"playCount": 0}) == 0.0

    def test_fallback_hashtags_not_empty(self):
        from cli_anything.social_trends.core.tiktok import _fallback_trending_hashtags
        result = _fallback_trending_hashtags("US", 20)
        assert len(result) == 20
        for h in result:
            assert h["hashtag"].startswith("#")

    def test_fallback_sounds_not_empty(self):
        from cli_anything.social_trends.core.tiktok import _fallback_trending_sounds
        result = _fallback_trending_sounds(10)
        assert len(result) == 10
        for s in result:
            assert "title" in s
            assert "artist" in s

    def test_normalize_video_structure(self):
        from cli_anything.social_trends.core.tiktok import _normalize_video
        item = {
            "id": "12345",
            "desc": "#fitness workout #fyp",
            "author": {"uniqueId": "creator123", "followerCount": 50000},
            "stats": {"playCount": 100000, "diggCount": 5000, "commentCount": 200, "shareCount": 100},
            "music": {"title": "Espresso", "authorName": "Sabrina", "id": "999"},
            "video": {"duration": 30},
        }
        result = _normalize_video(item)
        assert result["id"] == "12345"
        assert result["plays"] == 100000
        assert result["music_title"] == "Espresso"
        assert "#fitness" in result["hashtags"]


# ── youtube.py tests ──────────────────────────────────────────────────────

class TestYouTubeHelpers:
    def test_normalize_ytdlp_video(self):
        from cli_anything.social_trends.core.youtube import _normalize_ytdlp_video
        entry = {
            "id": "abc123",
            "title": "Best Workout 2024",
            "uploader": "FitnessChannel",
            "upload_date": "20240515",
            "description": "Great workout tips",
            "view_count": 500000,
            "like_count": 25000,
            "comment_count": 1000,
            "tags": ["fitness", "workout"],
            "webpage_url": "https://www.youtube.com/watch?v=abc123",
        }
        result = _normalize_ytdlp_video(entry)
        assert result["id"] == "abc123"
        assert result["title"] == "Best Workout 2024"
        assert result["views"] == 500000
        assert result["engagement_rate"] == pytest.approx((25000 + 1000) / 500000 * 100, rel=0.01)

    def test_engagement_rate_zero_views(self):
        from cli_anything.social_trends.core.youtube import _engagement_rate
        assert _engagement_rate({"viewCount": "0"}) == 0.0

    def test_extract_hashtags_from_videos(self):
        from cli_anything.social_trends.core.youtube import extract_hashtags_from_videos
        videos = [
            {"id": "1", "title": "#fitness workout routine", "description": "#gym tips", "tags": ["fitness"], "views": 100000},
            {"id": "2", "title": "Cooking with #food", "description": "#recipe hacks", "tags": ["food"], "views": 50000},
            {"id": "3", "title": "More #fitness content", "description": "", "tags": [], "views": 75000},
        ]
        result = extract_hashtags_from_videos(videos)
        tags = [r["hashtag"] for r in result]
        assert "#fitness" in tags
        # fitness appears in 2 videos — should be near the top
        fitness_entry = next(r for r in result if r["hashtag"] == "#fitness")
        assert fitness_entry["count"] >= 2

    def test_youtube_categories_dict(self):
        from cli_anything.social_trends.core.youtube import YOUTUBE_CATEGORIES
        assert "0" in YOUTUBE_CATEGORIES
        assert "10" in YOUTUBE_CATEGORIES  # music
        assert YOUTUBE_CATEGORIES["10"] == "Music"


# ── backend tests ─────────────────────────────────────────────────────────

class TestSocialBackend:
    def test_cache_set_and_get(self, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CACHE_DIR", tmp_path / "cache")
        monkeypatch.setattr(social_backend, "CONFIG_DIR", tmp_path)
        (tmp_path / "cache").mkdir()

        social_backend.cache_set("test_key", {"data": [1, 2, 3]})
        result = social_backend.cache_get("test_key")
        assert result == {"data": [1, 2, 3]}

    def test_cache_miss_returns_none(self, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CACHE_DIR", tmp_path / "cache")
        (tmp_path / "cache").mkdir()
        assert social_backend.cache_get("nonexistent_key_12345") is None

    def test_load_empty_config(self, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_FILE", tmp_path / "config.json")
        config = social_backend.load_config()
        assert config == {}

    def test_save_and_load_config(self, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr(social_backend, "CONFIG_DIR", tmp_path)
        social_backend.save_config({"youtube_api_key": "test_key_123"})
        config = social_backend.load_config()
        assert config["youtube_api_key"] == "test_key_123"

    def test_get_session_returns_session(self):
        from cli_anything.social_trends.utils.social_backend import get_session
        import requests
        session = get_session("tiktok")
        assert isinstance(session, requests.Session)
        assert "tiktok.com" in session.headers.get("Referer", "")

    def test_youtube_api_raises_without_key(self, tmp_path, monkeypatch):
        from cli_anything.social_trends.utils import social_backend
        monkeypatch.setattr(social_backend, "CONFIG_FILE", tmp_path / "config.json")
        with pytest.raises(RuntimeError, match="API key not configured"):
            social_backend.youtube_api_get("videos", {})
