"""Tests for hashtag analysis module."""

import pytest
from cli_anything.social_trends.core.hashtags import (
    classify_hashtag_by_volume,
    score_hashtag_set,
    generate_hashtag_strategy,
    extract_hashtags_from_text,
    deduplicate_and_rank,
    suggest_caption_hashtags,
    PLATFORM_HASHTAG_LIMITS,
)


class TestClassifyHashtagByVolume:
    def test_nano_tier(self):
        assert classify_hashtag_by_volume(50_000) == "nano"

    def test_micro_tier(self):
        assert classify_hashtag_by_volume(250_000) == "micro"

    def test_mid_tier(self):
        assert classify_hashtag_by_volume(1_000_000) == "mid"

    def test_macro_tier(self):
        assert classify_hashtag_by_volume(5_000_000) == "macro"

    def test_mega_tier(self):
        assert classify_hashtag_by_volume(50_000_000) == "mega"

    def test_zero_is_nano(self):
        assert classify_hashtag_by_volume(0) == "nano"


class TestScoreHashtagSet:
    def test_empty_set(self):
        result = score_hashtag_set([], {})
        assert result["quality_score"] == 0

    def test_single_nano_tag(self):
        result = score_hashtag_set(["#myfitness"], {"myfitness": 10_000})
        assert result["tier_distribution"].get("nano", 0) == 1

    def test_mixed_tiers_score_higher(self):
        # nano(<100K) + micro(100K-500K) + mid(500K-2M) = full ideal coverage → max diversity
        counts = {"fitnesslife": 10_000, "fitnesshack": 200_000, "fitness": 1_000_000}
        result = score_hashtag_set(["#fitnesslife", "#fitnesshack", "#fitness"], counts)
        assert result["quality_score"] >= 60

    def test_all_mega_penalized(self):
        counts = {t: 50_000_000 for t in ["fitness", "gym", "workout", "health"]}
        result = score_hashtag_set(["#fitness", "#gym", "#workout", "#health"], counts)
        assert result["quality_score"] < 80

    def test_strips_hash_prefix(self):
        result = score_hashtag_set(["#fitness"], {"fitness": 100_000})
        assert result["hashtags"][0]["hashtag"] == "#fitness"

    def test_recommendation_present(self):
        result = score_hashtag_set(["#fitness"], {"fitness": 1_000_000})
        assert isinstance(result["recommendation"], str)
        assert len(result["recommendation"]) > 0


class TestGenerateHashtagStrategy:
    def test_tiktok_strategy_returns_correct_keys(self):
        result = generate_hashtag_strategy("fitness", "tiktok")
        assert "strategy_tags" in result
        assert "all_suggestions" in result
        assert "platform_note" in result

    def test_strategy_respects_optimal_count(self):
        for platform in PLATFORM_HASHTAG_LIMITS:
            optimal = PLATFORM_HASHTAG_LIMITS[platform]["optimal"]
            result = generate_hashtag_strategy("cooking", platform)
            assert len(result["strategy_tags"]) <= optimal

    def test_instagram_strategy(self):
        result = generate_hashtag_strategy("travel", "instagram")
        assert result["platform"] == "instagram"
        assert result["optimal_count"] == 8

    def test_trending_tags_used_when_provided(self):
        result = generate_hashtag_strategy(
            "finance",
            "tiktok",
            trending_tags=["#investing101", "#moneyhack", "#stockmarket"],
        )
        tags = result["strategy_tags"]
        has_trending = any("investing" in t or "moneyhack" in t or "stockmarket" in t for t in tags)
        assert has_trending

    def test_posting_tip_present(self):
        result = generate_hashtag_strategy("pets", "instagram")
        assert "posting_tip" in result
        assert "instagram" in result["posting_tip"]


class TestExtractHashtagsFromText:
    def test_basic_extraction(self):
        tags = extract_hashtags_from_text("Love this #fitness #workout #gym life")
        assert "fitness" in tags
        assert "workout" in tags
        assert "gym" in tags

    def test_no_hashtags(self):
        assert extract_hashtags_from_text("Just a normal caption") == []

    def test_mixed_content(self):
        tags = extract_hashtags_from_text("Day 1 #myjourney starts #now! 💪 #goals")
        assert "myjourney" in tags
        assert "now" in tags
        assert "goals" in tags

    def test_trailing_punctuation_stripped(self):
        tags = extract_hashtags_from_text("#fitness. #gym,")
        assert "fitness" in tags
        assert "gym" in tags


class TestDeduplicateAndRank:
    def test_single_list(self):
        result = deduplicate_and_rank([["#fitness", "#gym"]])
        assert len(result) == 2
        assert result[0]["frequency"] == 1

    def test_overlapping_lists(self):
        result = deduplicate_and_rank([["#fitness", "#gym"], ["#fitness", "#yoga"]])
        fitness = next(r for r in result if r["hashtag"] == "#fitness")
        assert fitness["frequency"] == 2

    def test_case_insensitive(self):
        result = deduplicate_and_rank([["#Fitness"], ["#FITNESS"]])
        assert result[0]["frequency"] == 2

    def test_sorted_by_frequency_desc(self):
        result = deduplicate_and_rank([
            ["#a", "#b", "#a"],
            ["#a"],
        ])
        assert result[0]["hashtag"] == "#a"
        assert result[0]["frequency"] >= 2

    def test_empty_input(self):
        assert deduplicate_and_rank([]) == []
        assert deduplicate_and_rank([[]]) == []


class TestSuggestCaptionHashtags:
    def test_detects_missing_hashtags(self):
        result = suggest_caption_hashtags("Great workout today!", platform="tiktok")
        assert result["current_count"] == 0
        assert result["status"] == "add_more"

    def test_detects_existing_hashtags(self):
        caption = "Loving this #fitness #gym #workout vibe today!"
        result = suggest_caption_hashtags(caption, platform="instagram")
        assert result["current_count"] == 3

    def test_platform_note_present(self):
        result = suggest_caption_hashtags("Hello #world", platform="tiktok")
        assert "platform_note" in result
        assert len(result["platform_note"]) > 0

    def test_good_status_when_enough_tags(self):
        tags = " ".join(f"#tag{i}" for i in range(10))
        result = suggest_caption_hashtags(f"Caption {tags}", platform="instagram")
        assert result["status"] == "good"

    def test_suggestions_from_extra_niche_tags(self):
        result = suggest_caption_hashtags(
            "My post",
            platform="tiktok",
            extra_niche_tags=["#fitlife", "#gymrat", "#gains"],
        )
        assert len(result["suggested_additions"]) > 0
