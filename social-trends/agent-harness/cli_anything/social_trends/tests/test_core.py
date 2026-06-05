"""Unit tests for social-trends core modules (no external API calls)."""

import pytest
from unittest.mock import patch, MagicMock

from cli_anything.social_trends.core.hashtag_analyzer import HashtagAnalyzer
from cli_anything.social_trends.core.account_optimizer import AccountOptimizer, AccountProfile
from cli_anything.social_trends.core.theme_pages import ThemePageGuide, THEME_NICHES


# ── HashtagAnalyzer ────────────────────────────────────────────────────────────

class TestHashtagAnalyzer:
    def setup_method(self):
        self.analyzer = HashtagAnalyzer()

    def test_analyze_returns_dict(self):
        result = self.analyzer.analyze_hashtags(["#fyp", "#fitness", "#gym", "workout"])
        assert isinstance(result, dict)
        assert "analysis" in result
        assert "recommendations" in result

    def test_analyze_empty(self):
        result = self.analyzer.analyze_hashtags([])
        assert "error" in result

    def test_analyze_deduplicates(self):
        result = self.analyzer.analyze_hashtags(["#fyp", "#fyp", "#fyp"])
        tags = [a["hashtag"] for a in result["analysis"]]
        assert tags.count("#fyp") == 1

    def test_build_optimal_set_tiktok(self):
        result = self.analyzer.build_optimal_set(
            platform="tiktok",
            niche="fitness",
            trending_tags=["viral", "trending2024"],
            count=8,
        )
        assert "optimal_set" in result
        assert "copy_ready" in result
        assert result["platform"] == "tiktok"
        assert len(result["optimal_set"]) <= 8

    def test_build_optimal_set_youtube(self):
        result = self.analyzer.build_optimal_set(
            platform="youtube",
            niche="finance",
            trending_tags=[],
            count=5,
        )
        assert result["platform"] == "youtube"
        assert len(result["optimal_set"]) >= 1

    def test_get_niche_tags(self):
        tags = self.analyzer.get_niche_tags("fitness")
        assert all(t.startswith("#") for t in tags)
        assert len(tags) > 0

    def test_list_niches(self):
        niches = self.analyzer.list_niches()
        assert "fitness" in niches
        assert "finance" in niches

    def test_unknown_niche_returns_empty(self):
        tags = self.analyzer.get_niche_tags("unknownniche12345")
        assert tags == []

    def test_score_produces_total_score(self):
        result = self.analyzer.analyze_hashtags(["fyp", "fitness", "workout", "gym", "gains"])
        for item in result["analysis"]:
            assert "total_score" in item
            assert item["total_score"] >= 0

    def test_recommendation_for_too_few_hashtags(self):
        result = self.analyzer.analyze_hashtags(["fyp"])
        recs = result["recommendations"]
        assert any("more hashtags" in r.lower() for r in recs)

    def test_recommendation_for_too_many(self):
        tags = [f"tag{i}" for i in range(35)]
        result = self.analyzer.analyze_hashtags(tags)
        recs = result["recommendations"]
        assert any("spammy" in r.lower() or "too many" in r.lower() for r in recs)


# ── AccountOptimizer ───────────────────────────────────────────────────────────

class TestAccountOptimizer:
    def setup_method(self):
        self.optimizer = AccountOptimizer()

    def _make_profile(self, **kwargs):
        defaults = dict(
            platform="tiktok",
            handle="testuser",
            followers=5000,
            avg_views=3000,
            avg_likes=150,
            avg_comments=20,
            has_profile_photo=True,
            has_bio=True,
            bio_text="Daily fitness tips | Follow for workouts | Free plan below",
            has_link=True,
            posting_days_per_week=4.0,
            uses_hashtags=True,
            avg_hashtag_count=5,
            uses_trending_audio=True,
            has_cta_in_bio=True,
            niche="fitness",
        )
        defaults.update(kwargs)
        return AccountProfile(**defaults)

    def test_score_returns_dict(self):
        profile = self._make_profile()
        result = self.optimizer.score_account(profile)
        assert isinstance(result, dict)
        assert "score" in result
        assert "grade" in result
        assert "checks" in result

    def test_perfect_profile_scores_high(self):
        profile = self._make_profile()
        result = self.optimizer.score_account(profile)
        assert result["percent"] >= 70

    def test_empty_profile_scores_low(self):
        profile = self._make_profile(
            has_bio=False, bio_text="", has_link=False,
            posting_days_per_week=0.5, uses_hashtags=False,
            avg_hashtag_count=0, uses_trending_audio=False,
            has_cta_in_bio=False, niche="",
        )
        result = self.optimizer.score_account(profile)
        assert result["percent"] < 60

    def test_grade_mapping(self):
        profile = self._make_profile()
        result = self.optimizer.score_account(profile)
        assert result["grade"] in ("A", "B", "C", "D", "F")

    def test_top_priorities_are_high_priority(self):
        profile = self._make_profile(has_bio=False, has_link=False, niche="")
        result = self.optimizer.score_account(profile)
        for p in result["top_priorities"]:
            assert p["priority"] == "high"

    def test_engagement_rate_calculation(self):
        profile = self._make_profile(followers=10000, avg_views=5000, avg_likes=200, avg_comments=30)
        result = self.optimizer.score_account(profile)
        assert "engagement_rate" in result
        er_float = float(result["engagement_rate"].rstrip("%"))
        assert er_float >= 0

    def test_growth_plan_structure(self):
        profile = self._make_profile(followers=1000, posting_days_per_week=3.0)
        plan = self.optimizer.growth_plan(profile, goal_followers=10000, weeks=8)
        assert "plan" in plan
        assert len(plan["plan"]) == 8
        assert plan["plan"][0]["week"] == 1

    def test_growth_plan_already_at_goal(self):
        profile = self._make_profile(followers=50000)
        plan = self.optimizer.growth_plan(profile, goal_followers=10000, weeks=8)
        assert "message" in plan

    def test_compare_accounts(self):
        profiles = [
            self._make_profile(handle="a", has_bio=True, niche="fitness"),
            self._make_profile(handle="b", has_bio=False, niche=""),
        ]
        ranked = self.optimizer.compare_accounts(profiles)
        assert ranked[0]["score"] >= ranked[1]["score"]

    def test_youtube_platform_checks(self):
        profile = self._make_profile(platform="youtube")
        result = self.optimizer.score_account(profile)
        check_names = [c["check"] for c in result["checks"]]
        assert any("Engagement" in c for c in check_names)

    def test_follower_tier_labels(self):
        for followers, expected_tier in [
            (500, "<1k"),
            (5000, "1k-10k"),
            (50000, "10k-100k"),
            (500000, "100k-1m"),
            (5000000, ">1m"),
        ]:
            profile = self._make_profile(followers=followers)
            result = self.optimizer.score_account(profile)
            assert result["follower_tier"] == expected_tier


# ── ThemePageGuide ─────────────────────────────────────────────────────────────

class TestThemePageGuide:
    def setup_method(self):
        self.guide = ThemePageGuide()

    def test_get_known_niche(self):
        result = self.guide.get_niche("fitness")
        assert result is not None
        assert "monetization" in result
        assert "hashtags" in result

    def test_get_unknown_niche_returns_none(self):
        result = self.guide.get_niche("doesnotexist")
        assert result is None

    def test_list_niches_returns_list(self):
        niches = self.guide.list_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 5
        assert all("niche" in n for n in niches)

    def test_recommend_niche_returns_ranked_list(self):
        result = self.guide.recommend_niche(["fast_growth", "easy_start"])
        assert isinstance(result, list)
        assert len(result) <= 5

    def test_30_day_plan_has_phases(self):
        plan = self.guide.get_30_day_plan()
        phases = [p["phase"] for p in plan]
        assert "Setup" in phases
        assert "Growth Push" in phases

    def test_content_strategy_structure(self):
        result = self.guide.get_content_strategy("fitness", "tiktok")
        assert "content_mix" in result
        assert "monetization_stack" in result
        assert "pro_tips" in result

    def test_content_strategy_unknown_niche_error(self):
        result = self.guide.get_content_strategy("unknownniche", "tiktok")
        assert "error" in result

    def test_income_calculator_structure(self):
        result = self.guide.income_calculator(50000, 3.5, "tiktok")
        assert "monthly_estimates" in result
        assert "total_potential" in result["monthly_estimates"]
        assert "next_milestone" in result

    def test_income_calculator_nano_creator(self):
        result = self.guide.income_calculator(500, 8.0, "tiktok")
        assert result["followers"] == 500

    def test_income_calculator_mega_creator(self):
        result = self.guide.income_calculator(2_000_000, 1.5, "youtube")
        assert result["followers"] == 2_000_000

    def test_conversion_tactic_affiliate(self):
        result = self.guide.get_conversion_tactic("affiliate_links")
        assert result is not None
        assert "top_programs" in result

    def test_list_conversion_tactics(self):
        tactics = self.guide.list_conversion_tactics()
        names = [t["tactic"] for t in tactics]
        assert "affiliate_links" in names
        assert "digital_products" in names

    def test_all_niches_have_required_keys(self):
        for niche, data in THEME_NICHES.items():
            assert "monetization" in data, f"{niche} missing monetization"
            assert "hashtags" in data, f"{niche} missing hashtags"
            assert "platforms" in data, f"{niche} missing platforms"


# ── YouTube trends (mocked) ────────────────────────────────────────────────────

class TestYouTubeTrends:
    def test_get_trending_videos_parses_response(self):
        from cli_anything.social_trends.core.youtube_trends import YouTubeTrends

        mock_response = {
            "items": [
                {
                    "id": "abc123",
                    "snippet": {
                        "title": "Top 10 Fitness Tips #fitness #workout",
                        "channelTitle": "FitChannel",
                        "publishedAt": "2024-01-01T00:00:00Z",
                        "categoryId": "10",
                        "tags": ["fitness", "workout"],
                        "description": "#gains #motivation",
                        "thumbnails": {},
                    },
                    "statistics": {"viewCount": "1000000", "likeCount": "50000", "commentCount": "2000"},
                }
            ]
        }
        yt = YouTubeTrends(api_key="fake_key")
        with patch("requests.get") as mock_get:
            mock_get.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_response,
                raise_for_status=lambda: None,
            )
            videos = yt.get_trending_videos()
        assert len(videos) == 1
        v = videos[0]
        assert v["id"] == "abc123"
        assert v["views"] == 1_000_000
        assert "fitness" in v["hashtags"] or "gains" in v["hashtags"]

    def test_get_trending_hashtags_ranks_by_score(self):
        from cli_anything.social_trends.core.youtube_trends import YouTubeTrends

        yt = YouTubeTrends(api_key="fake")
        with patch.object(yt, "get_trending_videos") as mock_videos:
            mock_videos.return_value = [
                {"hashtags": ["fitness", "fitness", "gym"], "views": 500000, "likes": 10000},
                {"hashtags": ["fitness", "travel"], "views": 200000, "likes": 5000},
            ]
            hashtags = yt.get_trending_hashtags()
        assert hashtags[0]["hashtag"] == "#fitness"


# ── TikTok trends (mocked) ────────────────────────────────────────────────────

class TestTikTokTrends:
    def test_get_trending_hashtags_from_videos_fallback(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokTrends

        tt = TikTokTrends()
        with patch.object(tt, "get_trending_videos") as mock_videos:
            mock_videos.return_value = [
                {"view_count": 1_000_000, "hashtags": ["fyp", "fitness", "fyp"]},
                {"view_count": 500_000, "hashtags": ["fyp", "gym"]},
            ]
            # Simulate failed discover API → falls back to video extraction
            with patch.object(tt.session, "get", side_effect=Exception("timeout")):
                result = tt.get_trending_hashtags(top_n=5)
        assert any(t["hashtag"] == "#fyp" for t in result)
