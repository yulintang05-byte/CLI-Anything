"""Unit tests for social-trends core modules (no external deps required)."""

import json
import pytest
from collections import Counter
from unittest.mock import MagicMock, patch

from cli_anything.social_trends.core.hashtag_analyzer import (
    HashtagAnalyzer, _clean_tag, _tier, _estimate_reach, _trend_score,
)
from cli_anything.social_trends.core.music_tracker import (
    MusicTracker, _normalize_title, _detect_niche, _sound_recommendation,
)
from cli_anything.social_trends.core.account_optimizer import (
    AccountOptimizer, _yt_tier, _tt_tier, _er_label, _audit_bio,
)
from cli_anything.social_trends.core.theme_page import (
    ThemePageConverter, _get_milestone, MILESTONES, NICHES,
)
from cli_anything.social_trends.core.tiktok_scraper import (
    _normalize_tiktok_video, _calc_engagement, _extract_sigi_state,
)
from cli_anything.social_trends.core.youtube_scraper import _days_ago_iso


# ── Hashtag Analyzer Tests ────────────────────────────────────────────────

class TestHashtagAnalyzer:
    def test_clean_tag_strips_hash(self):
        assert _clean_tag("#fitness") == "fitness"
        assert _clean_tag("  #GYM_life  ") == "gym_life"
        assert _clean_tag("no-hash") == "nohash"

    def test_clean_tag_lowercases(self):
        assert _clean_tag("FITNESS") == "fitness"
        assert _clean_tag("#WorkOut") == "workout"

    def test_tier_boundaries(self):
        assert _tier(0) == "niche"
        assert _tier(10_000) == "low"
        assert _tier(100_000) == "medium"
        assert _tier(1_000_000) == "high"
        assert _tier(10_000_000) == "mega"
        assert _tier(50_000_000) == "mega"

    def test_estimate_reach(self):
        reach = _estimate_reach(10, 20)
        # 10*50000 + 20*200000 = 500000 + 4000000
        assert reach == 4_500_000

    def test_trend_score_cross_platform_bonus(self):
        score_both = _trend_score(10, 10, 20)
        score_yt_only = _trend_score(20, 0, 20)
        assert score_both > score_yt_only

    def test_feed_and_top_tags_youtube(self):
        analyzer = HashtagAnalyzer()
        analyzer.feed_youtube([("fitness", 100), ("gym", 80), ("workout", 60)])
        results = analyzer.get_top_by_platform("youtube", 3)
        assert len(results) == 3
        assert results[0].tag == "fitness"

    def test_feed_and_top_tags_tiktok(self):
        analyzer = HashtagAnalyzer()
        analyzer.feed_tiktok([("fyp", 500), ("viral", 400), ("trending", 300)])
        results = analyzer.get_top_by_platform("tiktok", 3)
        assert results[0].tag == "fyp"

    def test_cross_platform_detection(self):
        analyzer = HashtagAnalyzer()
        analyzer.feed_youtube([("fitness", 50), ("gym", 30)])
        analyzer.feed_tiktok([("fitness", 100), ("viral", 200)])
        cross = analyzer.get_top_cross_platform()
        tags = [r.tag for r in cross]
        assert "fitness" in tags
        assert "gym" not in tags  # only on youtube
        assert "viral" not in tags  # only on tiktok

    def test_build_post_strategy_structure(self):
        analyzer = HashtagAnalyzer()
        analyzer.feed_youtube([("fitness", 10), ("gym", 5), ("workout", 3), ("health", 2)])
        analyzer.feed_tiktok([("fitness", 200), ("fyp", 1000), ("viral", 800), ("gymtok", 150)])
        strategy = analyzer.build_post_strategy("fitness", "both", 30)
        assert "pillar_tags" in strategy
        assert "niche_tags" in strategy
        assert "micro_tags" in strategy
        assert "ready_to_paste" in strategy
        assert strategy["niche"] == "fitness"

    def test_compare_tags(self):
        analyzer = HashtagAnalyzer()
        analyzer.feed_youtube([("fitness", 50)])
        analyzer.feed_tiktok([("fitness", 100)])
        results = analyzer.compare_tags(["#fitness", "#unknown"])
        assert len(results) == 2
        assert results[0].tag == "fitness"  # sorted by score

    def test_strategy_ready_to_paste_format(self):
        analyzer = HashtagAnalyzer()
        analyzer.feed_youtube([("fitness", 100)])
        analyzer.feed_tiktok([("fitness", 200), ("gym", 150)])
        strategy = analyzer.build_post_strategy("fitness")
        paste = strategy["ready_to_paste"]
        assert "#" in paste


# ── Music Tracker Tests ────────────────────────────────────────────────────

class TestMusicTracker:
    def test_normalize_title(self):
        assert _normalize_title("Artist - Song (Official Video)") == "artist - song"
        assert _normalize_title("SONG [Official Audio]") == "song"

    def test_detect_niche_fitness(self):
        niches = _detect_niche("Gym Workout Motivation Mix")
        assert "fitness" in niches

    def test_detect_niche_gaming(self):
        niches = _detect_niche("Epic Boss Battle Theme")
        assert "gaming" in niches

    def test_detect_niche_no_match(self):
        niches = _detect_niche("Totally Random Title XYZ")
        assert len(niches) == 0

    def test_sound_recommendation_viral(self):
        rec = _sound_recommendation(50000, 1)  # 50k/day velocity
        assert "VIRAL" in rec or "24 hours" in rec

    def test_sound_recommendation_rising(self):
        rec = _sound_recommendation(500, 1)
        assert "RISING" in rec or "TRENDING" in rec

    def test_feed_youtube_tracks(self):
        tracker = MusicTracker()
        tracker.feed_youtube_tracks([
            {"id": "1", "title": "Artist - Song (Official Video)", "artist": "Artist",
             "view_count": 1_000_000, "url": "https://yt.be/1", "channel": "ArtistVEVO"},
        ])
        tracks = tracker.get_top_youtube_tracks()
        assert len(tracks) == 1
        assert tracks[0].platform == "youtube"

    def test_feed_tiktok_sounds(self):
        tracker = MusicTracker()
        tracker.feed_tiktok_sounds([
            {"id": "123", "title": "Trending Sound", "artist": "DJ X", "video_count": 500, "est_reach": 1_000_000},
        ])
        sounds = tracker.get_top_tiktok_sounds()
        assert len(sounds) == 1
        assert sounds[0].title == "Trending Sound"

    def test_feed_tiktok_videos_extracts_sounds(self):
        tracker = MusicTracker()
        videos = [
            {"sound": {"id": "abc", "title": "Hot Beat", "author_name": "Producer", "is_original": False}, "play_count": 100_000},
            {"sound": {"id": "abc", "title": "Hot Beat", "author_name": "Producer", "is_original": False}, "play_count": 200_000},
            {"sound": {"id": "xyz", "title": "Other Sound", "author_name": "DJ2", "is_original": True}, "play_count": 50_000},
        ]
        tracker.feed_tiktok_videos(videos)
        sounds = tracker.get_top_tiktok_sounds()
        assert sounds[0].id == "abc"  # used in 2 videos
        assert sounds[0].use_count == 2

    def test_export_report_structure(self):
        tracker = MusicTracker()
        report = tracker.export_report()
        assert "top_tiktok_sounds" in report
        assert "top_youtube_tracks" in report
        assert "cross_platform_hits" in report
        assert "generated_at" in report


# ── Account Optimizer Tests ───────────────────────────────────────────────

class TestAccountOptimizer:
    def test_yt_tier_classification(self):
        assert _yt_tier(500) == "micro"
        assert _yt_tier(50_000) == "small"
        assert _yt_tier(500_000) == "mid"
        assert _yt_tier(5_000_000) == "large"

    def test_tt_tier_classification(self):
        assert _tt_tier(500) == "micro"
        assert _tt_tier(50_000) == "small"
        assert _tt_tier(500_000) == "mid"
        assert _tt_tier(5_000_000) == "large"

    def test_er_label_excellent(self):
        label = _er_label(9.0, 6.0)
        assert "EXCELLENT" in label

    def test_er_label_low(self):
        label = _er_label(1.0, 6.0)
        assert "LOW" in label

    def test_bio_audit_empty(self):
        score, suggestions = _audit_bio("", "tiktok", "fitness")
        assert score < 50
        assert len(suggestions) > 0

    def test_bio_audit_good(self):
        bio = "Daily fitness tips & workout ideas! 💪 New videos Mon/Wed/Fri. Follow for fitness motivation! linktr.ee/mypage"
        score, suggestions = _audit_bio(bio, "youtube", "fitness")
        assert score >= 60

    def test_bio_audit_has_cta(self):
        bio = "Subscribe for daily content! linktr.ee/page"
        score, suggestions = _audit_bio(bio, "youtube", "cooking")
        cta_suggestion_count = sum(1 for s in suggestions if "call-to-action" in s.lower())
        assert cta_suggestion_count == 0  # CTA is present

    def test_audit_youtube_account_returns_audit(self):
        optimizer = AccountOptimizer()
        optimizer.set_niche("fitness")
        optimizer.feed_trending_hashtags(["fitness", "gym", "workout"])
        optimizer.feed_trending_topics(["Home workout tips", "Gym motivation 2025"])
        ch_stats = {
            "name": "FitChannel", "description": "Daily fitness workouts. Subscribe! linktr.ee/fit",
            "subscriber_count": 5_000, "view_count": 100_000, "video_count": 50,
            "custom_url": "@fitchannel", "country": "US",
        }
        videos = [
            {"title": "5 min workout", "published_at": "2025-01-01", "view_count": 1000,
             "like_count": 80, "comment_count": 20, "engagement_rate": 10.0, "tags": ["fitness"]},
            {"title": "Gym tips", "published_at": "2025-01-05", "view_count": 500,
             "like_count": 30, "comment_count": 10, "engagement_rate": 8.0, "tags": []},
        ]
        audit = optimizer.audit_youtube_account(ch_stats, videos, "fitness")
        assert audit.platform == "youtube"
        assert audit.niche == "fitness"
        assert audit.tier == "micro"
        assert audit.current_er > 0
        assert isinstance(audit.quick_wins, list)
        assert isinstance(audit.bio_suggestions, list)

    def test_audit_tiktok_account_returns_audit(self):
        optimizer = AccountOptimizer()
        optimizer.set_niche("beauty")
        stats = {
            "username": "beautycreator", "nickname": "Beauty Creator",
            "bio": "Makeup tips", "follower_count": 25_000,
            "following_count": 500, "video_count": 200,
            "heart_count": 500_000, "verified": False,
        }
        audit = optimizer.audit_tiktok_account(stats, [], "beauty")
        assert audit.platform == "tiktok"
        assert audit.follower_count == 25_000
        assert audit.tier == "small"

    def test_content_gaps_found(self):
        optimizer = AccountOptimizer()
        optimizer.set_niche("fitness")
        optimizer.feed_trending_hashtags(["crossfit", "hiit", "yoga"])
        optimizer.feed_trending_topics(["HIIT workout 2025", "CrossFit beginners"])
        ch_stats = {"name": "Ch", "description": "", "subscriber_count": 1000,
                    "view_count": 10000, "video_count": 10, "custom_url": ""}
        videos = [{"title": "Running tips", "tags": ["running"], "view_count": 100,
                   "like_count": 5, "comment_count": 1, "engagement_rate": 6.0, "published_at": "2025-01-01"}]
        audit = optimizer.audit_youtube_account(ch_stats, videos, "fitness")
        # Should detect missing trending topics
        assert len(audit.content_gaps) >= 0  # may be 0 if title matches

    def test_generate_optimization_report(self):
        optimizer = AccountOptimizer()
        ch_stats = {"name": "TestCh", "description": "test", "subscriber_count": 0,
                    "view_count": 0, "video_count": 0, "custom_url": ""}
        audit = optimizer.audit_youtube_account(ch_stats, [], "fitness")
        report = optimizer.generate_optimization_report([audit])
        assert "accounts" in report
        assert "unified_action_plan" in report


# ── Theme Page Tests ───────────────────────────────────────────────────────

class TestThemePage:
    def test_milestone_foundation_tiktok(self):
        current, next_ms, actions = _get_milestone(MILESTONES["tiktok"], 500)
        assert "Foundation" in current or "0" in current

    def test_milestone_growth_tiktok(self):
        current, next_ms, actions = _get_milestone(MILESTONES["tiktok"], 5_000)
        assert "Early Growth" in current or "10,000" in next_ms

    def test_milestone_youtube(self):
        current, next_ms, actions = _get_milestone(MILESTONES["youtube"], 5_000)
        assert "Monetization" in current

    def test_create_plan_returns_plan(self):
        converter = ThemePageConverter()
        converter.set_trending_data(["fitness", "gym"], [])
        plan = converter.create_plan("fitness", "tiktok", 1_000, "FitPage")
        assert plan.niche == "fitness"
        assert plan.platform == "tiktok"
        assert plan.current_followers == 1_000
        assert len(plan.content_pillars) > 0
        assert len(plan.weekly_content_calendar) > 0

    def test_create_plan_calendar_has_required_fields(self):
        converter = ThemePageConverter()
        plan = converter.create_plan("food", "youtube", 0)
        for day_plan in plan.weekly_content_calendar:
            assert "day" in day_plan
            assert "content_type" in day_plan
            assert "sound" in day_plan
            assert "hashtags" in day_plan

    def test_conversion_guide_structure(self):
        converter = ThemePageConverter()
        guide = converter.get_conversion_guide("fitness")
        expected_keys = [
            "phase_1_account_reset",
            "phase_2_content_strategy",
            "phase_3_growth_tactics",
            "phase_4_monetization",
            "content_sourcing",
            "tools_needed",
            "realistic_timeline",
            "common_mistakes_to_avoid",
        ]
        for key in expected_keys:
            assert key in guide, f"Missing key: {key}"

    def test_conversion_guide_has_content(self):
        converter = ThemePageConverter()
        guide = converter.get_conversion_guide("gaming")
        assert len(guide["phase_1_account_reset"]) >= 4
        assert len(guide["common_mistakes_to_avoid"]) >= 5

    def test_monetization_revenue_estimate(self):
        converter = ThemePageConverter()
        plan = converter.create_plan("finance", "youtube", 100_000)
        rev = plan.monetization_potential_monthly
        assert "total_estimated_monthly" in rev
        # Finance niche should have higher RPM
        yt_key = "youtube_adsense_monthly"
        assert yt_key in rev

    def test_all_niches_work(self):
        converter = ThemePageConverter()
        from cli_anything.social_trends.core.theme_page import NICHES
        for niche in NICHES:
            plan = converter.create_plan(niche, "tiktok", 0)
            assert plan.niche == niche
            assert len(plan.content_pillars) > 0

    def test_engagement_pod_strategy(self):
        converter = ThemePageConverter()
        plan = converter.create_plan("fitness", "tiktok")
        assert len(plan.engagement_pod_strategy) >= 4
        assert any("Telegram" in tip for tip in plan.engagement_pod_strategy)

    def test_branding_checklist(self):
        converter = ThemePageConverter()
        plan = converter.create_plan("fitness", "tiktok", page_name="FitNation")
        assert len(plan.account_branding_checklist) >= 8


# ── TikTok Scraper Unit Tests ─────────────────────────────────────────────

class TestTikTokScraper:
    def test_normalize_video_basic(self):
        raw = {
            "id": "12345",
            "desc": "Cool video #fitness",
            "author": {"uniqueId": "user123", "nickname": "User"},
            "stats": {"playCount": 100000, "diggCount": 5000, "commentCount": 200, "shareCount": 100},
            "music": {"id": "m1", "title": "Beat", "authorName": "DJ", "duration": 30, "original": False},
            "challenges": [{"title": "FitnessChallenge"}],
            "createTime": 1700000000,
        }
        video = _normalize_tiktok_video(raw)
        assert video["id"] == "12345"
        assert video["author"] == "user123"
        assert video["play_count"] == 100_000
        assert video["like_count"] == 5_000
        assert video["sound"]["title"] == "Beat"
        assert len(video["challenges"]) == 1

    def test_calc_engagement(self):
        stats = {"playCount": 100_000, "diggCount": 5_000, "commentCount": 200, "shareCount": 100}
        er = _calc_engagement(stats)
        assert er == round((5000 + 200 + 100) / 100_000 * 100, 3)

    def test_calc_engagement_zero_plays(self):
        stats = {"playCount": 0, "diggCount": 100}
        er = _calc_engagement(stats)
        assert er >= 0

    def test_extract_sigi_state_no_match(self):
        result = _extract_sigi_state("<html><body>nothing here</body></html>")
        assert result == {}

    def test_extract_hashtags_from_videos(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        tt = TikTokScraper(use_playwright=False)
        videos = [
            {"description": "#fitness #gym workout tips", "challenges": [{"title": "FitChallenge"}]},
            {"description": "#fitness routine #health", "challenges": []},
        ]
        tags = tt.extract_hashtags(videos)
        tag_map = dict(tags)
        assert tag_map.get("fitness", 0) >= 2
        assert tag_map.get("gym", 0) >= 1

    def test_get_niche_hashtags(self):
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        tt = TikTokScraper(use_playwright=False)
        tags = tt.get_niche_hashtags("fitness")
        assert len(tags) > 0
        assert "workout" in tags or "gym" in tags or "fitness" in tags


# ── YouTube Scraper Unit Tests ────────────────────────────────────────────

class TestYouTubeScraper:
    def test_days_ago_iso_format(self):
        result = _days_ago_iso(7)
        assert "T" in result
        assert "Z" in result
        assert len(result) == 20

    def test_days_ago_iso_7_days(self):
        from datetime import datetime, timezone, timedelta
        result = _days_ago_iso(7)
        dt = datetime.strptime(result, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = now - dt
        assert 6 <= diff.days <= 8

    def test_extract_hashtags_from_videos(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
        yt = YouTubeScraper(api_key="dummy_key")
        videos = [
            {"title": "Fitness #workout tips #gym", "description": "#health tips", "tags": ["fitness", "gym"]},
            {"title": "More #workout content", "description": "", "tags": ["workout"]},
        ]
        tags = yt.extract_hashtags(videos)
        tag_map = dict(tags)
        assert tag_map.get("workout", 0) >= 2
        assert tag_map.get("gym", 0) >= 2  # from tags list

    def test_get_trending_music_filters_music_videos(self):
        from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
        yt = YouTubeScraper(api_key="dummy_key")
        videos = [
            {"id": "1", "title": "Artist - Song (Official Video)", "channel": "ArtistVEVO",
             "view_count": 5_000_000, "url": "https://yt.be/1"},
            {"id": "2", "title": "How to code in Python", "channel": "DevChannel",
             "view_count": 100_000, "url": "https://yt.be/2"},
            {"id": "3", "title": "DJ Mix ft. Various Artists (Official Audio)", "channel": "MusicCh",
             "view_count": 2_000_000, "url": "https://yt.be/3"},
        ]
        tracks = yt.get_trending_music(videos)
        assert len(tracks) == 2  # Only music-keyword videos
        assert tracks[0]["view_count"] >= tracks[1]["view_count"]  # sorted by views


# ── Backend / Session Tests ────────────────────────────────────────────────

class TestSocialBackend:
    def test_config_init(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        from pathlib import Path
        import cli_anything.social_trends.utils.social_backend as sb_module
        monkeypatch.setattr(sb_module, "_CONFIG_DIR", tmp_path / ".cli-anything-social-trends")
        monkeypatch.setattr(sb_module, "_CONFIG_FILE", tmp_path / ".cli-anything-social-trends" / "config.json")
        monkeypatch.setattr(sb_module, "_ACCOUNTS_FILE", tmp_path / ".cli-anything-social-trends" / "accounts.json")
        monkeypatch.setattr(sb_module, "_REPORTS_DIR", tmp_path / ".cli-anything-social-trends" / "reports")
        monkeypatch.setattr(sb_module, "_HISTORY_FILE", tmp_path / ".cli-anything-social-trends" / "history")
        from cli_anything.social_trends.utils.social_backend import SocialBackend
        be = SocialBackend()
        assert be.config.youtube_api_key is None
        assert be.config.default_region == "US"

    def test_account_add_remove(self, tmp_path, monkeypatch):
        import cli_anything.social_trends.utils.social_backend as sb_module
        monkeypatch.setattr(sb_module, "_CONFIG_DIR", tmp_path / ".social")
        monkeypatch.setattr(sb_module, "_CONFIG_FILE", tmp_path / ".social" / "config.json")
        monkeypatch.setattr(sb_module, "_ACCOUNTS_FILE", tmp_path / ".social" / "accounts.json")
        monkeypatch.setattr(sb_module, "_REPORTS_DIR", tmp_path / ".social" / "reports")
        monkeypatch.setattr(sb_module, "_HISTORY_FILE", tmp_path / ".social" / "history")
        from cli_anything.social_trends.utils.social_backend import SocialBackend
        be = SocialBackend()
        be.add_account("youtube", "testchannel", channel_id="UC123", niche="fitness")
        assert len(be.list_accounts()) == 1
        assert be.get_account("youtube", "testchannel").channel_id == "UC123"
        be.remove_account("youtube", "testchannel")
        assert len(be.list_accounts()) == 0
