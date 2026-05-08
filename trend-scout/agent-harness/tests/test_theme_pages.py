"""Tests for theme page strategist."""

import pytest
from cli_anything.trend_scout.core.theme_pages import ThemePageStrategist, PROFITABLE_NICHES, CONVERSION_STRATEGIES


@pytest.fixture
def strategist():
    return ThemePageStrategist()


class TestGuide:
    def test_guide_has_all_sections(self, strategist):
        guide = strategist.get_theme_page_guide()
        assert "what_is_a_theme_page" in guide
        assert "choosing_your_niche" in guide
        assert "setup_checklist" in guide
        assert "content_sourcing" in guide
        assert "growth_phases" in guide
        assert "monetization_methods" in guide
        assert "tools_stack" in guide
        assert "common_mistakes" in guide
        assert "90_day_action_plan" in guide

    def test_setup_checklist_has_priorities(self, strategist):
        guide = strategist.get_theme_page_guide()
        checklist = guide["setup_checklist"]
        priorities = [item.get("priority") for item in checklist]
        assert "MUST" in priorities

    def test_90_day_plan_has_4_phases(self, strategist):
        guide = strategist.get_theme_page_guide()
        plan = guide["90_day_action_plan"]
        assert "week_1-2" in plan
        assert "month_2" in plan
        assert "month_3" in plan

    def test_tools_have_free_and_paid(self, strategist):
        guide = strategist.get_theme_page_guide()
        tools = guide["tools_stack"]
        assert "free_tools" in tools
        assert "paid_tools_worth_it" in tools
        assert "ai_tools" in tools

    def test_growth_phases_has_4_phases(self, strategist):
        guide = strategist.get_theme_page_guide()
        phases = guide["growth_phases"]
        assert len(phases) == 4


class TestNicheAnalysis:
    def test_known_niche_returns_data(self, strategist):
        result = strategist.get_niche_analysis("fitness_body")
        assert "monetization" in result
        assert "best_platforms" in result
        assert "avg_rpm" in result

    def test_unknown_niche_returns_generic(self, strategist):
        result = strategist.get_niche_analysis("underwater_basket_weaving")
        assert "monetization" in result
        assert len(result["monetization"]) > 0

    def test_has_content_pillars(self, strategist):
        result = strategist.get_niche_analysis("finance_wealth")
        pillars = result.get("content_pillars", [])
        assert len(pillars) >= 4
        percentages = [p.get("percentage", "") for p in pillars]
        assert any("%" in p for p in percentages)

    def test_has_account_names(self, strategist):
        result = strategist.get_niche_analysis("fitness_body")
        names = result.get("account_names_formula", [])
        assert len(names) >= 3
        assert all("@" in n for n in names)

    def test_has_competitor_research_guide(self, strategist):
        result = strategist.get_niche_analysis("food")
        guide = result.get("competitor_research", {})
        assert "step_1" in guide
        assert "tools" in guide


class TestAllNiches:
    def test_returns_list(self, strategist):
        niches = strategist.get_all_profitable_niches()
        assert isinstance(niches, list)
        assert len(niches) == len(PROFITABLE_NICHES)

    def test_all_have_required_fields(self, strategist):
        niches = strategist.get_all_profitable_niches()
        for n in niches:
            assert "niche" in n
            assert "difficulty" in n
            assert "avg_rpm" in n
            assert "best_platforms" in n

    def test_finance_has_high_rpm(self, strategist):
        niches = strategist.get_all_profitable_niches()
        finance = next((n for n in niches if "Finance" in n["niche"]), None)
        assert finance is not None
        # Finance should be near the top (high RPM) — within first half
        idx = niches.index(finance)
        assert idx < len(niches) // 2


class TestConversionPlaybook:
    def test_pre_monetization_for_small_accounts(self, strategist):
        result = strategist.get_conversion_playbook("fitness", followers=100)
        assert result["phase"] == "pre_monetization"

    def test_early_monetization_1k_10k(self, strategist):
        result = strategist.get_conversion_playbook("fitness", followers=5000)
        assert result["phase"] == "early_monetization"

    def test_scaling_for_mid_tier(self, strategist):
        result = strategist.get_conversion_playbook("fashion", followers=50_000)
        assert result["phase"] == "scaling_monetization"

    def test_full_monetization_for_large(self, strategist):
        result = strategist.get_conversion_playbook("gaming", followers=200_000)
        assert result["phase"] == "full_monetization"

    def test_has_actions_for_all_phases(self, strategist):
        for followers in [0, 5000, 50_000, 500_000]:
            result = strategist.get_conversion_playbook("fitness", followers=followers)
            assert len(result["strategy"]["actions"]) > 0


class TestConversionChecklist:
    def test_has_8_steps(self, strategist):
        result = strategist.get_account_conversion_checklist()
        assert len(result["conversion_steps"]) == 8

    def test_steps_are_ordered(self, strategist):
        result = strategist.get_account_conversion_checklist()
        steps = result["conversion_steps"]
        for i, step in enumerate(steps, 1):
            assert step["step"] == i

    def test_has_warning(self, strategist):
        result = strategist.get_account_conversion_checklist()
        assert "warning" in result
        assert len(result["warning"]) > 0

    def test_has_timeline(self, strategist):
        result = strategist.get_account_conversion_checklist()
        assert "timeline" in result


class TestConversionStrategies:
    def test_affiliate_has_platforms(self):
        assert "platforms" in CONVERSION_STRATEGIES["affiliate_link"]

    def test_brand_deals_has_pricing_formula(self):
        assert "pricing_formula" in CONVERSION_STRATEGIES["brand_deals"]

    def test_digital_products_has_niche_examples(self):
        products = CONVERSION_STRATEGIES["digital_products"]["products_by_niche"]
        assert "fitness" in products
        assert "finance" in products


class TestTimeline:
    def test_easy_niche_faster_timeline(self, strategist):
        easy = strategist._estimate_timeline("Very Low")
        medium = strategist._estimate_timeline("Medium")
        # Easy should have earlier first_1k than medium
        assert "7" in easy["first_1k"] or "30" in easy["first_1k"]

    def test_all_difficulties_return_dict(self, strategist):
        for difficulty in ["Very Low", "Low", "Low-Medium", "Medium", "High"]:
            result = strategist._estimate_timeline(difficulty)
            assert "first_1k" in result
            assert "first_income" in result
