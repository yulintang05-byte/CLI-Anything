"""Unit tests for cli-anything-social-media core modules (no network, no API)."""

import sys
import os
import json
import pytest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Make imports work from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from cli_anything.social_media.core import trends as trends_mod
from cli_anything.social_media.core import hashtags as hashtags_mod
from cli_anything.social_media.core import music as music_mod
from cli_anything.social_media.core import theme_page as theme_mod
from cli_anything.social_media.core import account_optimizer as acct_mod
from cli_anything.social_media.core import scheduler as sched_mod


# ── trends ────────────────────────────────────────────────────────────────────

class TestViralityScore:
    def test_zero_views_returns_zero(self):
        assert trends_mod.compute_virality_score(0, 0, 0) == 0.0

    def test_high_views_high_score(self):
        score = trends_mod.compute_virality_score(10_000_000, 500_000, 50_000)
        assert score > 50

    def test_score_bounded_0_100(self):
        score = trends_mod.compute_virality_score(999_999_999, 999_999_999, 999_999_999)
        assert 0 <= score <= 100

    def test_engagement_contributes_to_score(self):
        low_eng = trends_mod.compute_virality_score(1_000_000, 100, 10)
        high_eng = trends_mod.compute_virality_score(1_000_000, 100_000, 10_000)
        assert high_eng > low_eng


class TestAggregation:
    def _make_yt_video(self, title="Test", views=100_000, likes=5_000, tags=None):
        return {
            "id": "abc123", "title": title, "channel": "TestChannel",
            "views": views, "likes": likes, "comments": 500,
            "published": datetime.now(timezone.utc).isoformat(),
            "tags": tags or ["fitness", "workout"],
            "description": "Test description",
            "url": "https://youtube.com/watch?v=abc123",
            "thumbnail": "", "duration": "PT5M",
        }

    def _make_tt_hashtag(self, tag="fitness", views=1_000_000):
        return {"hashtag": f"#{tag}", "view_count": views, "video_count": 50_000, "is_trending": True, "source": "test"}

    def test_aggregate_returns_dict(self):
        report = trends_mod.aggregate_trends(
            yt_videos=[self._make_yt_video()],
            yt_hashtags=[{"hashtag": "#fitness", "score": 5, "total_views": 1_000_000}],
            yt_music=[self._make_yt_video("Song", 5_000_000)],
            tt_hashtags=[self._make_tt_hashtag()],
            tt_sounds=[{"title": "Beat", "author": "DJ", "video_count": 100_000, "duration": 15, "is_original": False}],
            tt_videos=[],
        )
        assert "generated_at" in report
        assert "top_viral" in report
        assert "youtube" in report
        assert "tiktok" in report
        assert "insight" in report

    def test_cross_platform_tags_detected(self):
        report = trends_mod.aggregate_trends(
            yt_videos=[self._make_yt_video(tags=["fitness"])],
            yt_hashtags=[{"hashtag": "#fitness", "score": 3, "total_views": 500_000}],
            yt_music=[],
            tt_hashtags=[{"hashtag": "#fitness", "view_count": 5_000_000, "video_count": 100_000, "is_trending": True, "source": "test"}],
            tt_sounds=[],
            tt_videos=[],
        )
        assert "fitness" in report["cross_platform_hashtags"]


# ── hashtags ──────────────────────────────────────────────────────────────────

class TestHashtagGeneration:
    def test_generates_for_known_niche(self):
        result = hashtags_mod.generate_hashtag_set("fitness", "instagram")
        assert "flat" in result
        assert "copy_paste" in result
        assert "count" in result
        assert result["count"] > 0

    def test_all_tags_have_hash_prefix(self):
        result = hashtags_mod.generate_hashtag_set("fashion", "tiktok")
        for tag in result["flat"]:
            assert tag.startswith("#"), f"Tag missing # prefix: {tag}"

    def test_count_within_platform_limits(self):
        result_ig = hashtags_mod.generate_hashtag_set("food", "instagram")
        result_yt = hashtags_mod.generate_hashtag_set("food", "youtube")
        result_tt = hashtags_mod.generate_hashtag_set("food", "tiktok")
        assert result_ig["count"] <= 30
        assert result_yt["count"] <= 20
        assert result_tt["count"] <= 20

    def test_custom_tags_included(self):
        result = hashtags_mod.generate_hashtag_set("fitness", "instagram", custom_tags=["mygym"])
        assert "#mygym" in result["flat"]

    def test_unknown_niche_uses_general(self):
        result = hashtags_mod.generate_hashtag_set("unknownniche12345", "instagram")
        assert result["count"] > 0

    def test_no_duplicate_tags(self):
        result = hashtags_mod.generate_hashtag_set("fitness", "instagram")
        assert len(result["flat"]) == len(set(result["flat"]))


class TestHashtagAnalysis:
    def test_analyze_empty_set(self):
        result = hashtags_mod.analyze_hashtag_set([], "fitness")
        assert result["tag_count"] == 0

    def test_over_30_tags_triggers_advice(self):
        many_tags = [f"#tag{i}" for i in range(35)]
        result = hashtags_mod.analyze_hashtag_set(many_tags)
        advice_text = " ".join(result["advice"]).lower()
        assert "30" in advice_text or "reduce" in advice_text

    def test_diversity_score_range(self):
        tags = ["#fitness", "#workout", "#gym", "#health", "#fitnessmotivation"]
        result = hashtags_mod.analyze_hashtag_set(tags, "fitness")
        assert 0 <= result["diversity_score"] <= 100


class TestHashtagExtraction:
    def test_extract_from_caption(self):
        caption = "Love this workout! #fitness #gym #health everyday"
        tags = hashtags_mod.extract_hashtags(caption)
        assert "#fitness" in tags
        assert "#gym" in tags
        assert "#health" in tags

    def test_empty_text_returns_empty(self):
        assert hashtags_mod.extract_hashtags("no hashtags here") == []


class TestHashtagScoring:
    def test_score_in_range(self):
        score = hashtags_mod.score_hashtag("fitness", "instagram", "fitness")
        assert 0 <= score <= 100

    def test_tiktok_fyp_gets_high_score(self):
        score = hashtags_mod.score_hashtag("fyp", "tiktok")
        assert score > 50

    def test_niche_tags_score_higher_in_niche(self):
        fitness_score = hashtags_mod.score_hashtag("workout", "instagram", "fitness")
        assert fitness_score > 0


# ── music ─────────────────────────────────────────────────────────────────────

class TestMusicReport:
    def _sample_yt_track(self):
        return {"title": "Summer Hit", "channel": "MusicChannel", "views": 5_000_000,
                "likes": 200_000, "url": "https://youtube.com/watch?v=xyz", "tags": ["pop", "summer"]}

    def _sample_tt_sound(self):
        return {"title": "Viral Beat", "author": "DJ Someone", "video_count": 500_000,
                "duration": 15, "is_original": False}

    def test_report_has_required_keys(self):
        report = music_mod.format_music_report([self._sample_yt_track()], [self._sample_tt_sound()])
        assert "youtube_trending_music" in report
        assert "tiktok_trending_sounds" in report
        assert "creator_tips" in report
        assert "generated_at" in report

    def test_tips_are_non_empty(self):
        report = music_mod.format_music_report([], [])
        assert isinstance(report["creator_tips"], list)
        assert len(report["creator_tips"]) > 0

    def test_sound_strategy_populated_for_known_type(self):
        report = music_mod.format_music_report([], [], content_type="dance")
        assert report["sound_strategy"] != {}

    def test_available_content_types_non_empty(self):
        types = music_mod.available_content_types()
        assert len(types) > 0
        assert "dance" in types


# ── theme_page ────────────────────────────────────────────────────────────────

class TestNicheSuggestions:
    def test_returns_correct_count(self):
        result = theme_mod.suggest_niches(["fitness"], max_suggestions=3)
        assert len(result) <= 3

    def test_all_fields_present(self):
        result = theme_mod.suggest_niches(["finance"])
        for n in result:
            assert "niche" in n
            assert "monetization" in n
            assert "difficulty" in n
            assert "monthly_growth_rate" in n

    def test_fitness_interest_returns_fitness(self):
        result = theme_mod.suggest_niches(["fitness"], max_suggestions=5)
        niches = [r["niche"] for r in result]
        assert "fitness" in niches

    def test_no_interests_still_returns_results(self):
        result = theme_mod.suggest_niches([])
        assert len(result) > 0


class TestContentCalendar:
    def test_calendar_length(self):
        cal = theme_mod.generate_content_calendar("fitness", days=14)
        assert len(cal) == 14

    def test_all_days_have_posts(self):
        cal = theme_mod.generate_content_calendar("finance", days=7, posts_per_day={"tiktok": 2})
        for day in cal:
            assert len(day["posts"]) > 0

    def test_posting_times_are_strings(self):
        cal = theme_mod.generate_content_calendar("fitness", days=3)
        for day in cal:
            for post in day["posts"]:
                assert isinstance(post["posting_time"], str)


class TestMonetizationRoadmap:
    def test_includes_phases(self):
        result = theme_mod.monetization_roadmap("fitness", 0)
        assert "phases" in result
        assert len(result["phases"]) > 0

    def test_includes_affiliate_programs(self):
        result = theme_mod.monetization_roadmap("personal finance", 5_000)
        assert "affiliate_programs" in result
        assert len(result["affiliate_programs"]) > 0

    def test_includes_brand_template(self):
        result = theme_mod.monetization_roadmap("fitness", 10_000)
        assert "brand_outreach_template" in result
        assert "Subject:" in result["brand_outreach_template"]

    def test_100k_phase_present_for_large_account(self):
        result = theme_mod.monetization_roadmap("finance", 100_000)
        phases_text = " ".join(p["phase"] for p in result["phases"])
        assert "100K" in phases_text


class TestThemePageGuide:
    def test_guide_structure(self):
        guide = theme_mod.theme_page_guide()
        assert "overview" in guide
        assert "phases" in guide
        assert "monetization_methods" in guide
        assert "content_sourcing" in guide
        assert "conversion_checklist" in guide

    def test_conversion_checklist_non_empty(self):
        guide = theme_mod.theme_page_guide()
        assert len(guide["conversion_checklist"]) >= 5


# ── account_optimizer ─────────────────────────────────────────────────────────

class TestBioAnalysis:
    def test_empty_bio_low_score(self):
        result = acct_mod.analyze_bio("", "instagram", "fitness")
        assert result["score"] < 30

    def test_good_bio_higher_score(self):
        bio = "💪 Fitness tips & workouts | Build your dream body | Free plan ↓"
        result = acct_mod.analyze_bio(bio, "instagram", "fitness")
        assert result["score"] > 50

    def test_improved_bio_provided(self):
        result = acct_mod.analyze_bio("just a person", "instagram", "fitness")
        assert "improved_bio" in result
        assert len(result["improved_bio"]) > 0

    def test_suggestions_list_is_list(self):
        result = acct_mod.analyze_bio("hi", "tiktok", "food")
        assert isinstance(result["suggestions"], list)


class TestEngagementAnalysis:
    def test_engagement_rate_calculated(self):
        result = acct_mod.engagement_rate_analysis(10_000, 500, 50, platform="instagram")
        assert "engagement_rate" in result
        assert result["engagement_rate"] > 0

    def test_zero_followers_returns_error(self):
        result = acct_mod.engagement_rate_analysis(0, 100, 10)
        assert "error" in result

    def test_tier_classification(self):
        result = acct_mod.engagement_rate_analysis(100_000, 10_000, 1_000, platform="instagram")
        assert result["tier"] in ("poor", "average", "good", "great", "viral")


class TestPostingSchedule:
    def test_schedule_has_correct_structure(self):
        result = acct_mod.optimize_posting_schedule("instagram", "fitness", posts_per_week=5)
        assert "schedule" in result
        assert "general_advice" in result
        assert len(result["schedule"]) == 5

    def test_tiktok_schedule_advice_mentions_tiktok(self):
        result = acct_mod.optimize_posting_schedule("tiktok", "fitness")
        advice_text = " ".join(result["general_advice"]).lower()
        assert "tiktok" in advice_text


class TestProfileSaveLoad:
    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(acct_mod, "_PROFILES_PATH", tmp_path)
        profile = acct_mod.AccountProfile(
            platform="tiktok", handle="testuser", niche="fitness",
            followers=5000, bio="Test bio",
        )
        acct_mod.save_profile(profile)
        loaded = acct_mod.load_profile("tiktok", "testuser")
        assert loaded is not None
        assert loaded.followers == 5000
        assert loaded.bio == "Test bio"

    def test_load_nonexistent_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.setattr(acct_mod, "_PROFILES_PATH", tmp_path)
        result = acct_mod.load_profile("instagram", "doesnotexist")
        assert result is None


class TestFullAudit:
    def test_audit_returns_all_sections(self):
        profile = acct_mod.AccountProfile(
            platform="instagram", handle="testuser", niche="fitness",
            followers=10_000, avg_likes=300, avg_comments=30, bio="Fitness enthusiast",
        )
        result = acct_mod.full_account_audit(profile)
        assert "overall_score" in result
        assert "bio_analysis" in result
        assert "engagement_analysis" in result
        assert "posting_schedule" in result
        assert "growth_hacks" in result
        assert "quick_wins" in result

    def test_overall_score_in_range(self):
        profile = acct_mod.AccountProfile(
            platform="tiktok", handle="test", niche="finance",
            followers=50_000, avg_likes=2_000, avg_views=100_000,
        )
        result = acct_mod.full_account_audit(profile)
        assert 0 <= result["overall_score"] <= 100


# ── scheduler ─────────────────────────────────────────────────────────────────

class TestScheduler:
    def test_add_and_list_post(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sched_mod, "_SCHEDULE_PATH", tmp_path / "schedule.json")
        post = sched_mod.add_post(
            platform="tiktok", content_type="video",
            caption="Test post #fitness", scheduled_time="2024-12-01T18:00:00",
            hashtags=["#fitness", "#gym"],
        )
        assert post.id
        assert post.status == "scheduled"

        posts = sched_mod.list_posts()
        assert len(posts) == 1
        assert posts[0].caption == "Test post #fitness"

    def test_cancel_post(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sched_mod, "_SCHEDULE_PATH", tmp_path / "schedule.json")
        post = sched_mod.add_post(
            platform="instagram", content_type="reel",
            caption="Test", scheduled_time="2024-12-02T12:00:00",
        )
        ok = sched_mod.cancel_post(post.id)
        assert ok
        posts = sched_mod.list_posts(status="cancelled")
        assert len(posts) == 1

    def test_mark_posted(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sched_mod, "_SCHEDULE_PATH", tmp_path / "schedule.json")
        post = sched_mod.add_post(
            platform="youtube", content_type="video",
            caption="My video", scheduled_time="2024-12-03T15:00:00",
        )
        sched_mod.mark_posted(post.id)
        all_posts = sched_mod._load_schedule()
        assert all_posts[0].status == "posted"

    def test_export_csv(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sched_mod, "_SCHEDULE_PATH", tmp_path / "schedule.json")
        sched_mod.add_post("tiktok", "video", "Caption", "2024-12-01T10:00:00")
        out = sched_mod.export_schedule_csv(tmp_path / "out.csv")
        assert out.exists()
        content = out.read_text()
        assert "tiktok" in content

    def test_export_json(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sched_mod, "_SCHEDULE_PATH", tmp_path / "schedule.json")
        sched_mod.add_post("instagram", "reel", "Caption", "2024-12-01T10:00:00")
        out = sched_mod.export_schedule_json(tmp_path / "out.json")
        data = json.loads(out.read_text())
        assert isinstance(data, list)
        assert data[0]["platform"] == "instagram"

    def test_summary_counts(self, tmp_path, monkeypatch):
        monkeypatch.setattr(sched_mod, "_SCHEDULE_PATH", tmp_path / "schedule.json")
        sched_mod.add_post("tiktok", "video", "A", "2024-12-01T10:00:00")
        sched_mod.add_post("instagram", "reel", "B", "2024-12-02T10:00:00")
        s = sched_mod.summary()
        assert s["total_posts"] == 2
        assert "tiktok" in s["by_platform"]
        assert "instagram" in s["by_platform"]
