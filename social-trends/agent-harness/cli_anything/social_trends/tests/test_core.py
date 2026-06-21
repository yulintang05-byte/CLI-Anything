"""Unit tests for social-trends core modules — no external API calls required."""

import pytest
from cli_anything.social_trends.core import hashtags as ht
from cli_anything.social_trends.core import account as acc
from cli_anything.social_trends.core import theme_pages as tp
from cli_anything.social_trends.core import tiktok as tt
from cli_anything.social_trends.utils import social_backend as backend


# ─────────────────────────────────────────────────────────────────────
# Hashtag scoring
# ─────────────────────────────────────────────────────────────────────

class TestHashtagScoring:
    def test_perfect_set_scores_high(self):
        tags = ["#fyp", "#foryou", "#fitness", "#workout", "#gym", "#health"]
        result = ht.score_hashtag_set(tags, platform="tiktok")
        assert result["score"] >= 75
        assert result["grade"] in ("A", "B")

    def test_empty_set_scores_low(self):
        result = ht.score_hashtag_set([], platform="tiktok")
        assert result["score"] <= 60

    def test_too_many_hashtags_penalized(self):
        tags = [f"#tag{i}" for i in range(30)]
        result = ht.score_hashtag_set(tags, platform="tiktok")
        assert any("Too many" in issue for issue in result["issues"])

    def test_shadowban_tags_penalized(self):
        tags = ["#fyp", "#followback", "#like4like"]
        result = ht.score_hashtag_set(tags, platform="tiktok")
        assert result["score"] < 80
        assert any("Shadowban" in issue for issue in result["issues"])

    def test_no_broad_tags_penalized(self):
        tags = ["#gymmotivation", "#deadlift", "#squat"]
        result = ht.score_hashtag_set(tags, platform="tiktok")
        assert any("broad" in issue.lower() for issue in result["issues"])

    def test_grade_boundaries(self):
        assert ht._grade(95) == "A"
        assert ht._grade(80) == "B"
        assert ht._grade(65) == "C"
        assert ht._grade(50) == "D"
        assert ht._grade(30) == "F"

    def test_normalize_strips_hash(self):
        assert ht._normalize("#Fitness") == "fitness"
        assert ht._normalize("fitness") == "fitness"

    def test_build_optimal_set_respects_count(self):
        niche = ["#bodybuilding", "#deadlift", "#gains"]
        viral = ["#fyp", "#foryou", "#viral"]
        result = ht.build_optimal_set(niche, viral, platform="tiktok", count=5)
        assert len(result) <= 5

    def test_build_optimal_set_includes_broad_tags(self):
        niche = ["#cooking"]
        viral = ["#fyp", "#foryou", "#viral"]
        result = ht.build_optimal_set(niche, viral, count=6)
        broad_found = any(t in ("#fyp", "#foryou", "#viral") for t in result)
        assert broad_found

    def test_suggest_caption_hashtags_relevance(self):
        caption = "My morning workout routine for building muscle"
        tags = ["#fyp", "#workout", "#muscle", "#cooking", "#gaming"]
        result = ht.suggest_caption_hashtags(caption, tags, platform="tiktok")
        # workout and muscle should rank higher than cooking and gaming
        workout_idx = next((i for i, t in enumerate(result) if "workout" in t), 999)
        cooking_idx = next((i for i, t in enumerate(result) if "cooking" in t), 999)
        assert workout_idx < cooking_idx

    def test_youtube_optimal_count_is_higher(self):
        tags = ["#tag1"] * 20
        result_yt = ht.score_hashtag_set(tags[:8], platform="youtube")
        result_tt = ht.score_hashtag_set(tags[:8], platform="tiktok")
        # 8 tags: fine for YouTube, too many for TikTok
        yt_issues = [i for i in result_yt["issues"] if "Too many" in i]
        tt_issues = [i for i in result_tt["issues"] if "Too many" in i]
        # YouTube allows more tags before penalty
        assert len(yt_issues) <= len(tt_issues)


# ─────────────────────────────────────────────────────────────────────
# Account scoring
# ─────────────────────────────────────────────────────────────────────

class TestAccountScoring:
    def _base_profile(self, **kwargs):
        defaults = dict(
            platform="tiktok",
            username="testuser",
            display_name="Test User | Fitness",
            bio="Daily fitness tips to help you reach your goals. Free guide below 👇",
            has_profile_photo=True,
            has_link=True,
            follower_count=5000,
            following_count=200,
            post_count=50,
            niche="fitness",
        )
        defaults.update(kwargs)
        return acc.score_profile(**defaults)

    def test_complete_profile_scores_high(self):
        result = self._base_profile()
        assert result["score"] >= 75

    def test_missing_bio_critical(self):
        result = self._base_profile(bio="")
        critical = [r for r in result["recommendations"] if r["priority"] == "critical"]
        assert any("bio" in r["area"] for r in critical)

    def test_missing_photo_critical(self):
        result = self._base_profile(has_profile_photo=False)
        critical = [r for r in result["recommendations"] if r["priority"] == "critical"]
        assert any("photo" in r["area"] for r in critical)

    def test_no_link_penalized(self):
        result = self._base_profile(has_link=False)
        assert any(r["area"] == "link" for r in result["recommendations"])

    def test_few_posts_flagged(self):
        result = self._base_profile(post_count=5)
        assert any("content" in r["area"] for r in result["recommendations"])

    def test_grade_returned(self):
        result = self._base_profile()
        assert result["grade"] in ("A", "B", "C", "D", "F")

    def test_quick_wins_only_high_priority(self):
        result = self._base_profile(bio="", has_profile_photo=False, has_link=False)
        for win in result["quick_wins"]:
            assert win["priority"] in ("critical", "high")

    def test_platform_stored_in_result(self):
        for platform in ("tiktok", "youtube", "instagram"):
            result = self._base_profile(platform=platform)
            assert result["platform"] == platform

    def test_bad_ratio_flagged(self):
        result = self._base_profile(follower_count=100, following_count=1000)
        issues = [r["area"] for r in result["recommendations"]]
        assert "ratio" in issues

    def test_posting_schedule_tiktok(self):
        result = acc.posting_schedule("tiktok", timezone_offset=0)
        assert "best_times_local" in result
        assert "frequency" in result
        assert result["frequency"]["unit"] == "day"

    def test_posting_schedule_youtube(self):
        result = acc.posting_schedule("youtube", timezone_offset=-5)
        assert result["frequency"]["unit"] == "week"
        assert len(result["best_times_local"]) > 0

    def test_posting_schedule_tz_adjusted(self):
        utc_result = acc.posting_schedule("tiktok", timezone_offset=0)
        est_result = acc.posting_schedule("tiktok", timezone_offset=-5)
        assert utc_result["best_times_local"] != est_result["best_times_local"]

    def test_tips_returned_for_all_platforms(self):
        for platform in ("tiktok", "youtube", "instagram"):
            result = acc.posting_schedule(platform, timezone_offset=0)
            assert len(result["tips"]) > 0


# ─────────────────────────────────────────────────────────────────────
# Theme Pages
# ─────────────────────────────────────────────────────────────────────

class TestThemePages:
    def test_all_niches_returned(self):
        data = tp.niche_overview()
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_specific_niche_returned(self):
        data = tp.niche_overview("fitness_health")
        assert isinstance(data, dict)
        assert "monetization" in data
        assert "top_hashtags" in data

    def test_unknown_niche_returns_error(self):
        data = tp.niche_overview("unicorn_farming")
        assert "error" in data

    def test_roadmap_phases(self):
        roadmap = tp.theme_page_roadmap("motivation_mindset", current_followers=0)
        assert roadmap["current_phase"] == 0
        assert len(roadmap["all_milestones"]) == 4

    def test_roadmap_phase_detection_mid(self):
        roadmap = tp.theme_page_roadmap("luxury_lifestyle", current_followers=50000)
        assert roadmap["current_phase"] == 2

    def test_roadmap_phase_detection_advanced(self):
        roadmap = tp.theme_page_roadmap("luxury_lifestyle", current_followers=500000)
        assert roadmap["current_phase"] == 3

    def test_monetization_guide_all(self):
        data = tp.monetization_guide()
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_monetization_guide_specific(self):
        data = tp.monetization_guide("affiliate")
        assert isinstance(data, dict)
        assert "how_to_get" in data

    def test_conversion_tips_all_platforms(self):
        for platform in ("tiktok", "youtube", "instagram"):
            tips = tp.conversion_optimization_tips(platform)
            assert len(tips) >= 3
            for tip in tips:
                assert "tactic" in tip
                assert "description" in tip

    def test_niche_has_required_fields(self):
        for niche_data in tp.niche_overview():
            assert "niche" in niche_data
            assert "difficulty" in niche_data
            assert "monetization" in niche_data
            assert "top_hashtags" in niche_data


# ─────────────────────────────────────────────────────────────────────
# TikTok client (curated fallbacks — no real API calls)
# ─────────────────────────────────────────────────────────────────────

class TestTikTokClient:
    def setup_method(self):
        self.client = tt.TikTokTrendsClient()

    def test_curated_hashtags_returned(self):
        tags = self.client._curated_hashtags(niche="fitness", count=10)
        assert len(tags) <= 10
        assert all("hashtag" in t for t in tags)

    def test_curated_hashtags_general(self):
        tags = self.client._curated_hashtags(niche=None, count=5)
        assert len(tags) > 0

    def test_curated_sounds_returned(self):
        sounds = self.client._curated_sounds(count=2)
        assert isinstance(sounds, list)

    def test_niche_hashtags_fitness(self):
        tags = self.client.niche_hashtags("fitness")
        assert len(tags) > 0
        assert all(t["hashtag"].startswith("#") for t in tags)

    def test_niche_hashtags_unknown_falls_to_general(self):
        tags = self.client.niche_hashtags("unknown_niche_xyz")
        assert len(tags) > 0

    def test_available_niches_nonempty(self):
        niches = self.client.available_niches()
        assert "fitness" in niches
        assert "music" in niches

    def test_trending_hashtags_returns_list(self):
        tags = self.client.trending_hashtags(niche="beauty", count=10)
        assert isinstance(tags, list)
        assert len(tags) > 0

    def test_trending_sounds_returns_list(self):
        sounds = self.client.trending_sounds(count=5)
        assert isinstance(sounds, list)


# ─────────────────────────────────────────────────────────────────────
# Backend configuration
# ─────────────────────────────────────────────────────────────────────

class TestSocialBackend:
    def test_config_status_returns_dict(self):
        status = backend.config_status()
        assert "youtube_api_key_set" in status
        assert "tiktok_session_set" in status
        assert "region" in status

    def test_region_default(self):
        region = backend.get_region()
        assert isinstance(region, str)
        assert len(region) >= 2

    def test_tz_offset_default(self):
        offset = backend.get_timezone_offset()
        assert isinstance(offset, int)
        assert -12 <= offset <= 14
