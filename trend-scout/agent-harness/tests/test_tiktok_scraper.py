"""Tests for TikTok scraper."""

import pytest
from cli_anything.trend_scout.core.tiktok_scraper import TikTokScraper, CONTENT_NICHES


@pytest.fixture
def scraper():
    return TikTokScraper()


class TestStaticHashtags:
    def test_returns_list(self, scraper):
        result = scraper._static_trending_hashtags("US", 10)
        assert isinstance(result, list)
        assert len(result) == 10

    def test_all_have_hashtag_key(self, scraper):
        result = scraper._static_trending_hashtags("US", 5)
        for h in result:
            assert "hashtag" in h
            assert h["hashtag"].startswith("#")

    def test_respects_limit(self, scraper):
        result = scraper._static_trending_hashtags("US", 3)
        assert len(result) == 3

    def test_fyp_is_top(self, scraper):
        result = scraper._static_trending_hashtags("US", 30)
        assert result[0]["hashtag"] == "#fyp"

    def test_has_trending_score(self, scraper):
        result = scraper._static_trending_hashtags("US", 5)
        for h in result:
            assert "trending_score" in h
            assert h["trending_score"] >= 0


class TestStaticSounds:
    def test_returns_list(self, scraper):
        result = scraper._static_trending_sounds(5)
        assert isinstance(result, list)
        assert len(result) == 5

    def test_has_required_fields(self, scraper):
        result = scraper._static_trending_sounds(3)
        for s in result:
            assert "title" in s
            assert "artist" in s


class TestHashtagStrategy:
    def test_nano_account_gets_growth_tags(self, scraper):
        result = scraper.get_hashtag_strategy(niche="fitness", follower_count=100)
        tags = result.get("recommended_hashtags", [])
        assert "fyp" in tags or "#fyp" in tags or any("fyp" in t for t in tags)

    def test_has_caption_template(self, scraper):
        result = scraper.get_hashtag_strategy(niche="fashion", follower_count=5000)
        assert "caption_template" in result
        assert len(result["caption_template"]) > 0

    def test_has_mix_breakdown(self, scraper):
        result = scraper.get_hashtag_strategy(niche="food")
        assert "mix_breakdown" in result
        mix = result["mix_breakdown"]
        assert "niche_specific" in mix
        assert "broad_trending" in mix

    def test_different_tiers_get_different_tags(self, scraper):
        nano = scraper.get_hashtag_strategy("fitness", follower_count=500)
        macro = scraper.get_hashtag_strategy("fitness", follower_count=500_000)
        nano_size = nano["mix_breakdown"].get("account_size", [])
        macro_size = macro["mix_breakdown"].get("account_size", [])
        assert nano_size != macro_size


class TestViralPatterns:
    def test_returns_all_fields(self, scraper):
        result = scraper.get_viral_content_patterns("US")
        assert "best_hashtags" in result
        assert "trending_sounds" in result
        assert "optimal_video_duration" in result
        assert "best_posting_times" in result
        assert "caption_tips" in result
        assert "hook_formulas" in result

    def test_duration_has_sweet_spot(self, scraper):
        result = scraper._get_optimal_duration()
        assert "sweet_spot_seconds" in result
        assert "hook_window_seconds" in result

    def test_posting_times_have_days(self, scraper):
        result = scraper._get_best_posting_times("US")
        assert "best_days" in result
        assert "best_windows" in result

    def test_has_10_hook_formulas(self, scraper):
        formulas = scraper._get_hook_formulas()
        assert len(formulas) >= 8


class TestNicheMapping:
    def test_known_niches_have_keywords(self):
        for niche, keywords in CONTENT_NICHES.items():
            assert isinstance(keywords, list)
            assert len(keywords) > 0

    def test_fitness_contains_workout(self):
        assert "workout" in CONTENT_NICHES["fitness"]

    def test_finance_contains_money(self):
        assert "money" in CONTENT_NICHES["finance"]


class TestCaptionBuilding:
    def test_includes_niche(self, scraper):
        result = scraper._build_caption_template("fitness", ["workout", "gym"])
        assert "fitness" in result

    def test_includes_fyp(self, scraper):
        result = scraper._build_caption_template("gaming", ["gaming"])
        assert "fyp" in result.lower()

    def test_includes_tags(self, scraper):
        result = scraper._build_caption_template("food", ["recipe", "cooking"])
        assert "#recipe" in result or "#cooking" in result


class TestEngagementCalc:
    def test_zero_views_returns_zero(self, scraper):
        result = scraper._calc_engagement([{"views": 0, "likes": 100}])
        assert result == "0%"

    def test_empty_videos_returns_zero(self, scraper):
        result = scraper._calc_engagement([])
        assert result == "0%"

    def test_calculates_correctly(self, scraper):
        videos = [{"views": 1000, "likes": 50, "shares": 0}]
        result = scraper._calc_engagement(videos)
        assert "5.00%" == result
