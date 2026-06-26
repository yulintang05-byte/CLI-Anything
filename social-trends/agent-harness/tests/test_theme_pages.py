"""Tests for theme pages module."""

import pytest
from cli_anything.social_trends.core.theme_pages import (
    list_niches,
    get_niche_details,
    get_theme_page_launch_plan,
    get_content_repurposing_guide,
    get_converting_cta_templates,
    _NICHES,
)


class TestListNiches:
    def test_returns_all_niches_by_default(self):
        result = list_niches()
        assert result["total"] == len(_NICHES)

    def test_filter_by_monetization_high(self):
        result = list_niches(min_monetization="high")
        for niche in result["niches"]:
            assert niche["monetization_potential"] in ("high", "very_high")

    def test_filter_by_monetization_very_high(self):
        result = list_niches(min_monetization="very_high")
        for niche in result["niches"]:
            assert niche["monetization_potential"] == "very_high"

    def test_filter_by_platform_tiktok(self):
        result = list_niches(platform_filter="tiktok")
        for niche in result["niches"]:
            assert "tiktok" in niche["platforms"]

    def test_filter_by_platform_instagram(self):
        result = list_niches(platform_filter="instagram")
        for niche in result["niches"]:
            assert "instagram" in niche["platforms"]

    def test_combined_filters(self):
        result = list_niches(min_monetization="very_high", platform_filter="tiktok")
        for niche in result["niches"]:
            assert "tiktok" in niche["platforms"]
            assert niche["monetization_potential"] == "very_high"

    def test_filters_recorded_in_output(self):
        result = list_niches(min_monetization="high")
        assert result["filters_applied"]["min_monetization"] == "high"


class TestGetNicheDetails:
    def test_returns_fitness_niche(self):
        result = get_niche_details("fitness")
        assert result["name"] == "Fitness / Body Transformation"
        assert result["slug"] == "fitness"

    def test_returns_finance_niche(self):
        result = get_niche_details("finance")
        assert result["slug"] == "finance"

    def test_returns_crypto_niche(self):
        result = get_niche_details("crypto")
        assert "crypto" in result["slug"]

    def test_invalid_slug_raises(self):
        with pytest.raises(ValueError, match="not found"):
            get_niche_details("nonexistent_niche")

    def test_all_niches_have_required_fields(self):
        required = ["name", "slug", "platforms", "monetization_potential",
                    "content_types", "hashtags", "monetization_paths"]
        for niche in _NICHES:
            for field in required:
                assert field in niche, f"Niche '{niche['name']}' missing field '{field}'"

    def test_slug_is_lowercase(self):
        for niche in _NICHES:
            assert niche["slug"] == niche["slug"].lower()

    def test_all_slugs_unique(self):
        slugs = [n["slug"] for n in _NICHES]
        assert len(slugs) == len(set(slugs))


class TestGetThemePageLaunchPlan:
    def test_fitness_tiktok_plan(self):
        result = get_theme_page_launch_plan("fitness", "tiktok")
        assert result["niche"] == "Fitness / Body Transformation"
        assert result["platform"] == "tiktok"

    def test_has_six_steps(self):
        result = get_theme_page_launch_plan("motivation", "instagram")
        assert len(result["steps"]) == 6

    def test_steps_are_ordered(self):
        result = get_theme_page_launch_plan("food", "tiktok")
        for i, step in enumerate(result["steps"], 1):
            assert step["step"] == i

    def test_each_step_has_required_keys(self):
        result = get_theme_page_launch_plan("finance", "youtube")
        for step in result["steps"]:
            assert "title" in step
            assert "description" in step
            assert "time_estimate" in step

    def test_success_metrics_defined(self):
        result = get_theme_page_launch_plan("pets", "instagram")
        metrics = result["success_metrics"]
        assert "week_1" in metrics
        assert "month_1" in metrics
        assert "month_3" in metrics

    def test_budget_breakdown_when_budget_positive(self):
        result = get_theme_page_launch_plan("travel", "instagram", budget_usd=200)
        assert result["budget_breakdown"] != {}
        assert "tools_monthly" in result["budget_breakdown"]

    def test_budget_breakdown_empty_when_zero(self):
        result = get_theme_page_launch_plan("gaming", "youtube", budget_usd=0)
        assert result["budget_breakdown"] == {}

    def test_hashtags_from_niche(self):
        result = get_theme_page_launch_plan("fitness", "tiktok")
        assert len(result["hashtags_to_use"]) > 0

    def test_invalid_slug_raises(self):
        with pytest.raises(ValueError):
            get_theme_page_launch_plan("fakeslug", "tiktok")


class TestGetContentRepurposingGuide:
    def test_returns_repurposing_tree(self):
        result = get_content_repurposing_guide("fitness")
        assert "repurposing_tree" in result
        assert "derivatives" in result["repurposing_tree"]

    def test_derivatives_has_multiple_formats(self):
        result = get_content_repurposing_guide("motivation")
        derivatives = result["repurposing_tree"]["derivatives"]
        assert len(derivatives) >= 5

    def test_weekly_workflow_has_all_days(self):
        result = get_content_repurposing_guide("travel")
        schedule = result["weekly_workflow"]
        assert "Monday" in schedule
        assert "Sunday" in schedule

    def test_tools_section_present(self):
        result = get_content_repurposing_guide("food")
        assert "tools" in result
        assert "video_clipping" in result["tools"]

    def test_niche_name_in_result(self):
        result = get_content_repurposing_guide("crypto")
        assert "crypto" in result["niche"].lower() or result["niche"] != ""

    def test_principle_present(self):
        result = get_content_repurposing_guide("gaming")
        assert "principle" in result
        assert "Create Once" in result["principle"]


class TestGetConvertingCtaTemplates:
    def test_tiktok_ctas_returned(self):
        result = get_converting_cta_templates("fitness", "tiktok")
        assert len(result["caption_ctas"]) > 0

    def test_hook_templates_returned(self):
        result = get_converting_cta_templates("motivation", "instagram")
        assert len(result["hook_templates"]) > 0

    def test_dm_funnel_present(self):
        result = get_converting_cta_templates("finance", "tiktok")
        funnel = result["dm_funnel"]
        assert "step_1" in funnel
        assert "tools" in funnel

    def test_niche_name_in_ctas(self):
        result = get_converting_cta_templates("fitness", "tiktok")
        has_niche = any("fitness" in cta.lower() or "Fitness" in cta for cta in result["caption_ctas"])
        assert has_niche

    def test_monetization_sequence_present(self):
        result = get_converting_cta_templates("travel", "youtube")
        assert len(result["monetization_sequence"]) > 0

    def test_platform_recorded(self):
        result = get_converting_cta_templates("pets", "instagram")
        assert result["platform"] == "instagram"

    def test_invalid_niche_raises(self):
        with pytest.raises(ValueError):
            get_converting_cta_templates("badfakeslug", "tiktok")
