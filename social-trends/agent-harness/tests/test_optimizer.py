import pytest

from cli_anything.social_trends.core.account_optimizer import (
    NICHE_HASHTAG_SETS,
    OPTIMAL_TIMES,
    audit_account_profile,
    generate_content_pillars,
    get_hashtag_strategy,
    get_optimal_posting_times,
)


class TestGetHashtagStrategy:
    def test_tiktok_fitness_returns_hashtags(self):
        result = get_hashtag_strategy("tiktok", "fitness")
        assert "recommended_hashtags" in result
        assert isinstance(result["recommended_hashtags"], list)
        assert len(result["recommended_hashtags"]) > 0
        assert all(h.startswith("#") for h in result["recommended_hashtags"])

    def test_tiktok_recommended_count_is_small(self):
        result = get_hashtag_strategy("tiktok", "fitness")
        assert len(result["recommended_hashtags"]) <= 10

    def test_instagram_recommended_count_up_to_20(self):
        result = get_hashtag_strategy("instagram", "beauty")
        assert len(result["recommended_hashtags"]) <= 20

    def test_youtube_recommended_count_is_small(self):
        result = get_hashtag_strategy("youtube", "tech")
        assert len(result["recommended_hashtags"]) <= 10

    def test_returns_all_niche_tags(self):
        result = get_hashtag_strategy("tiktok", "gaming")
        assert "all_niche_tags" in result

    def test_unknown_niche_returns_empty_niche_tags(self):
        result = get_hashtag_strategy("tiktok", "underwater_basket_weaving")
        assert isinstance(result["recommended_hashtags"], list)

    def test_partial_niche_match(self):
        result = get_hashtag_strategy("tiktok", "fit")
        assert "recommended_hashtags" in result

    @pytest.mark.parametrize("platform", ["tiktok", "instagram", "youtube"])
    def test_all_platforms_return_valid_structure(self, platform):
        result = get_hashtag_strategy(platform, "food")
        assert "platform" in result
        assert result["platform"] == platform
        assert "recommended_hashtags" in result
        assert "best_practice" in result


class TestGetOptimalPostingTimes:
    def test_returns_all_seven_days(self):
        result = get_optimal_posting_times("tiktok")
        assert "full_week" in result
        assert len(result["full_week"]) == 7

    def test_today_key_is_present(self):
        result = get_optimal_posting_times("instagram")
        assert "today" in result
        assert "day" in result["today"]
        assert "best_times" in result["today"]

    def test_times_are_hhmm_format(self):
        result = get_optimal_posting_times("tiktok")
        for day, times in result["full_week"].items():
            for t in times:
                assert len(t) == 5
                assert t[2] == ":"

    def test_unknown_platform_falls_back_to_tiktok(self):
        result = get_optimal_posting_times("snapchat")
        assert "full_week" in result
        assert len(result["full_week"]) == 7

    def test_timezone_note_included(self):
        result = get_optimal_posting_times("youtube", timezone="PST")
        assert "PST" in result["timezone_note"]


class TestAuditAccountProfile:
    def test_returns_all_checklist_sections(self):
        result = audit_account_profile("tiktok", "myaccount")
        checklist = result["checklist"]
        assert "profile_basics" in checklist
        assert "content_strategy" in checklist
        assert "growth_tactics" in checklist
        assert "monetization_readiness" in checklist

    def test_each_item_has_priority(self):
        result = audit_account_profile("instagram", "test_user")
        for section, items in result["checklist"].items():
            for item in items:
                assert "item" in item
                assert "priority" in item
                assert item["priority"] in ("HIGH", "MEDIUM", "LOW")

    def test_returns_username_and_platform(self):
        result = audit_account_profile("youtube", "channel123")
        assert result["platform"] == "youtube"
        assert result["username"] == "channel123"

    def test_scoring_guide_present(self):
        result = audit_account_profile("tiktok", "x")
        assert "scoring_guide" in result


class TestGenerateContentPillars:
    def test_returns_5_pillars_for_known_niche(self):
        result = generate_content_pillars("fitness", "tiktok")
        assert len(result["content_pillars"]) == 5

    def test_returns_pillars_for_unknown_niche(self):
        result = generate_content_pillars("quantum_physics", "youtube")
        assert len(result["content_pillars"]) == 5

    def test_content_mix_adds_to_100(self):
        result = generate_content_pillars("food", "instagram")
        mix = result["content_mix"]
        total = sum(int(v.replace("%", "")) for v in mix.values())
        assert total == 100

    def test_posting_frequency_present(self):
        result = generate_content_pillars("lifestyle", "tiktok")
        assert "recommended_frequency" in result
        assert result["recommended_frequency"]

    def test_monthly_total_consistent(self):
        result = generate_content_pillars("business", "tiktok")
        pillars = result["content_pillars"]
        per_pillar = result["ideas_per_pillar_per_month"]
        assert result["total_monthly_content"] == len(pillars) * per_pillar


class TestNicheHashtagSets:
    def test_all_known_niches_have_required_keys(self):
        required = {"mega", "niche", "platform", "engagement"}
        for niche, tags in NICHE_HASHTAG_SETS.items():
            assert required.issubset(set(tags.keys())), f"Missing keys for niche: {niche}"

    def test_all_hashtags_start_with_hash(self):
        for niche, categories in NICHE_HASHTAG_SETS.items():
            for cat, tags in categories.items():
                for tag in tags:
                    assert tag.startswith("#"), f"Tag {tag!r} in {niche}/{cat} missing #"
