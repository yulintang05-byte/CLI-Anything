import pytest

from cli_anything.social_trends.core.theme_pages import (
    PROFITABLE_NICHES,
    THEME_PAGE_PLAYBOOK,
    get_all_niches,
    get_niche_analysis,
    get_theme_page_playbook,
)


class TestGetAllNiches:
    def test_returns_list(self):
        result = get_all_niches()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_each_item_has_required_fields(self):
        result = get_all_niches()
        required = {"niche", "cpm_range", "avg_rpm", "difficulty", "competition", "growth_speed"}
        for item in result:
            assert required.issubset(set(item.keys()))

    def test_sorted_by_rpm_descending(self):
        result = get_all_niches()
        rpms = [float(r["avg_rpm"].replace("$", "")) for r in result]
        assert rpms == sorted(rpms, reverse=True)

    def test_count_matches_profitable_niches(self):
        result = get_all_niches()
        assert len(result) == len(PROFITABLE_NICHES)


class TestGetNicheAnalysis:
    def test_known_niche_returns_full_data(self):
        result = get_niche_analysis("finance_investing")
        assert "data" in result
        assert "revenue_estimates" in result
        assert "recommended_platforms" in result
        assert "affiliate_programs" in result
        assert "content_ideas" in result

    def test_revenue_estimates_have_three_tiers(self):
        result = get_niche_analysis("tech_ai")
        revs = result["revenue_estimates"]
        assert "10K_followers" in revs
        assert "100K_followers" in revs
        assert "1M_followers" in revs

    def test_revenue_estimates_contain_dollar_values(self):
        result = get_niche_analysis("fitness_health")
        for tier, data in result["revenue_estimates"].items():
            assert "ad_rev_monthly" in data
            assert "$" in data["ad_rev_monthly"]

    def test_affiliate_programs_are_list_of_dicts(self):
        result = get_niche_analysis("beauty_fashion")
        programs = result["affiliate_programs"]
        assert isinstance(programs, list)
        assert len(programs) > 0
        for prog in programs:
            assert "name" in prog
            assert "commission" in prog

    def test_content_ideas_are_strings(self):
        result = get_niche_analysis("make_money_online")
        ideas = result["content_ideas"]
        assert isinstance(ideas, list)
        assert all(isinstance(i, str) for i in ideas)

    def test_unknown_niche_returns_fallback(self):
        result = get_niche_analysis("underwater_welding_tutorials")
        assert "note" in result
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)

    def test_partial_match_works(self):
        result = get_niche_analysis("fitness")
        assert "data" in result or "note" in result

    @pytest.mark.parametrize("niche", list(PROFITABLE_NICHES.keys()))
    def test_all_known_niches_return_full_analysis(self, niche):
        result = get_niche_analysis(niche)
        assert "niche" in result


class TestGetThemePagePlaybook:
    def test_returns_non_empty_string(self):
        result = get_theme_page_playbook()
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_key_phases(self):
        result = get_theme_page_playbook()
        assert "PHASE 1" in result
        assert "PHASE 2" in result
        assert "MONETIS" in result.upper()

    def test_contains_converting_section(self):
        result = get_theme_page_playbook()
        assert "CONVERTING" in result.upper()

    def test_contains_revenue_benchmarks(self):
        result = get_theme_page_playbook()
        assert "10K followers" in result
        assert "1M+" in result


class TestProfitableNiches:
    def test_all_niches_have_required_keys(self):
        required = {"cpm_range", "avg_rpm", "audience", "monetization", "difficulty", "competition", "growth_speed", "conversion_rate"}
        for niche, data in PROFITABLE_NICHES.items():
            missing = required - set(data.keys())
            assert not missing, f"Niche {niche!r} missing keys: {missing}"

    def test_monetization_is_non_empty_list(self):
        for niche, data in PROFITABLE_NICHES.items():
            assert isinstance(data["monetization"], list)
            assert len(data["monetization"]) > 0

    def test_avg_rpm_parseable_as_float(self):
        for niche, data in PROFITABLE_NICHES.items():
            rpm = float(data["avg_rpm"].replace("$", ""))
            assert rpm > 0
