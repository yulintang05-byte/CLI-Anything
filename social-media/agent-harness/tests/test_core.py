"""
Social media CLI — unit tests (no network required).

Covers: session, hashtags, accounts, theme_pages, output utils.
Run: cd social-media/agent-harness && pytest tests/test_core.py -v
"""
import copy
import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social.core.session import Session
from cli_anything.social.core import hashtags, accounts, theme_pages
from cli_anything.social.utils.output import as_json, as_table, emit


# ─── Session ─────────────────────────────────────────────────────────────────

class TestSession:
    def test_initial_state(self):
        s = Session()
        assert s.state["accounts"] == []
        assert s.state["trends_cache"] == {}

    def test_add_account(self):
        s = Session()
        acct = s.add_account("tiktok", "@creator", "fitness")
        assert acct["platform"] == "tiktok"
        assert acct["handle"] == "@creator"
        assert len(s.get_accounts()) == 1

    def test_add_multiple_accounts(self):
        s = Session()
        s.add_account("tiktok", "@a", "fitness")
        s.add_account("instagram", "@b", "food")
        assert len(s.get_accounts()) == 2
        assert len(s.get_accounts(platform="tiktok")) == 1
        assert len(s.get_accounts(platform="instagram")) == 1

    def test_undo(self):
        s = Session()
        s.add_account("tiktok", "@a")
        assert len(s.get_accounts()) == 1
        s.undo()
        assert len(s.get_accounts()) == 0

    def test_trends_cache(self):
        s = Session()
        s.cache_trends("tiktok", "US", [{"tag": "#viral"}])
        cached = s.get_cached_trends("tiktok", "US")
        assert cached is not None
        assert cached[0]["tag"] == "#viral"

    def test_trends_cache_miss_on_empty(self):
        s = Session()
        assert s.get_cached_trends("youtube", "US") is None

    def test_save_load(self, tmp_path):
        s = Session()
        s.add_account("youtube", "@yt", "tech")
        f = tmp_path / "state.json"
        s.save(f)
        s2 = Session()
        s2.load(f)
        assert len(s2.get_accounts()) == 1
        assert s2.get_accounts()[0]["handle"] == "@yt"


# ─── Hashtags ─────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_research_known_niche(self):
        result = hashtags.research_hashtags("fitness", "tiktok")
        assert result["niche"] == "fitness"
        assert result["platform"] == "tiktok"
        assert len(result["recommended"]) > 0
        assert len(result["all_tags"]) > 0

    def test_research_unknown_niche(self):
        result = hashtags.research_hashtags("beekeeping", "instagram")
        assert result["niche"] == "beekeeping"
        assert len(result["recommended"]) > 0

    def test_research_respects_platform_limits(self):
        tt = hashtags.research_hashtags("food", "tiktok")
        # TikTok max is 5 (+1 for fyp) = 6 at most
        assert len(tt["recommended"]) <= 6

        ig = hashtags.research_hashtags("food", "instagram")
        assert len(ig["recommended"]) <= 30

    def test_all_platforms(self):
        for platform in ["tiktok", "instagram", "youtube", "twitter"]:
            result = hashtags.research_hashtags("fitness", platform)
            assert "recommended" in result

    def test_score_hashtag(self):
        result = hashtags.score_hashtag("#fitness")
        assert result["hashtag"] == "#fitness"
        assert "specificity" in result
        assert "recommendation" in result

    def test_score_hashtag_no_hash(self):
        result = hashtags.score_hashtag("fitness")
        assert result["hashtag"] == "#fitness"

    def test_available_niches(self):
        niches = hashtags.available_niches()
        assert "fitness" in niches
        assert "finance" in niches
        assert len(niches) >= 8

    def test_tips_returned(self):
        result = hashtags.research_hashtags("travel", "tiktok")
        assert isinstance(result["tips"], list)
        assert len(result["tips"]) > 0


# ─── Accounts ────────────────────────────────────────────────────────────────

class TestAccounts:
    def test_optimize_tiktok(self):
        result = accounts.optimize_account("tiktok", "fitness", "growing")
        assert result["platform"] == "tiktok"
        assert "posting_schedule" in result
        assert "bio_optimization" in result
        assert "growth_levers" in result
        assert "engagement_rules" in result
        assert "monetization_path" in result

    def test_optimize_all_platforms(self):
        for platform in ["tiktok", "instagram", "youtube"]:
            result = accounts.optimize_account(platform)
            assert result["platform"] == platform

    def test_optimize_all_stages(self):
        for stage in ["new_account", "growing", "monetized"]:
            result = accounts.optimize_account("tiktok", stage=stage)
            assert result["stage"] == stage
            cr = result["content_ratio"]
            assert sum(cr.values()) == 100

    def test_content_ratio_sums_to_100(self):
        for stage in ["new_account", "growing", "monetized"]:
            r = accounts.optimize_account("instagram", stage=stage)
            assert sum(r["content_ratio"].values()) == 100

    def test_audit_returns_checklist(self):
        result = accounts.audit_account("@testuser", "tiktok")
        assert "checklist" in result
        assert len(result["checklist"]) >= 10
        for item in result["checklist"]:
            assert "item" in item
            assert "question" in item

    def test_growth_levers_structure(self):
        levers = accounts.growth_levers("tiktok")
        assert isinstance(levers, list)
        for lever in levers:
            assert "lever" in lever
            assert "impact" in lever
            assert "tip" in lever

    def test_monetization_milestones(self):
        path = accounts.monetization_path("youtube", "growing")
        assert "milestones" in path
        assert "revenue_streams" in path


# ─── Theme Pages ─────────────────────────────────────────────────────────────

class TestThemePages:
    def test_guide_structure(self):
        guide = theme_pages.theme_page_guide()
        assert "what_is_a_theme_page" in guide
        assert "phase_1_setup" in guide
        assert "phase_2_content_strategy" in guide
        assert "phase_3_growth" in guide
        assert "phase_4_monetization" in guide
        assert "tools_stack" in guide
        assert "common_mistakes" in guide

    def test_guide_with_known_niche(self):
        guide = theme_pages.theme_page_guide("fitness")
        assert guide["selected_niche"] is not None

    def test_guide_with_unknown_niche(self):
        guide = theme_pages.theme_page_guide("beekeeping")
        assert guide["selected_niche"] is not None
        assert "note" in guide["selected_niche"]

    def test_list_niches(self):
        niches = theme_pages.list_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 8
        for n in niches:
            assert "niche" in n
            assert "monetization" in n
            assert "avg_cpm" in n

    def test_content_calendar_has_all_days(self):
        guide = theme_pages.theme_page_guide()
        cal = guide["phase_2_content_strategy"]["content_calendar_template"]
        days = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]
        for d in days:
            assert d in cal

    def test_mistakes_list(self):
        guide = theme_pages.theme_page_guide()
        assert len(guide["common_mistakes"]) >= 5


# ─── Output utils ────────────────────────────────────────────────────────────

class TestOutput:
    def test_as_json(self):
        data = {"key": "value", "num": 42}
        result = as_json(data)
        parsed = json.loads(result)
        assert parsed == data

    def test_as_table_basic(self):
        rows = [{"name": "Alice", "score": 95}, {"name": "Bob", "score": 87}]
        result = as_table(rows, ["name", "score"])
        assert "Alice" in result
        assert "Bob" in result
        assert "name" in result
        assert "score" in result

    def test_as_table_empty(self):
        result = as_table([], ["name"])
        assert "no results" in result.lower()

    def test_emit_json(self):
        data = [{"rank": 1, "tag": "#viral"}]
        result = emit(data, "json")
        assert json.loads(result)[0]["tag"] == "#viral"

    def test_emit_table(self):
        data = [{"rank": 1, "tag": "#viral"}]
        result = emit(data, "table", ["rank", "tag"])
        assert "#viral" in result

    def test_as_table_truncates_long_values(self):
        rows = [{"col": "x" * 100}]
        result = as_table(rows, ["col"], max_col=32)
        assert len(result.split("\n")[3]) < 60  # truncated


# ─── Scraper helpers (no network) ────────────────────────────────────────────

class TestScraperHelpers:
    def test_parse_view_str_k(self):
        from cli_anything.social.core.scraper import _parse_view_str
        assert _parse_view_str("1.5K") == 1500
        assert _parse_view_str("500k") == 500000

    def test_parse_view_str_m(self):
        from cli_anything.social.core.scraper import _parse_view_str
        assert _parse_view_str("2.3M") == 2300000
        assert _parse_view_str("10m") == 10000000

    def test_parse_view_str_b(self):
        from cli_anything.social.core.scraper import _parse_view_str
        assert _parse_view_str("1B") == 1000000000

    def test_parse_view_str_plain(self):
        from cli_anything.social.core.scraper import _parse_view_str
        assert _parse_view_str("12345") == 12345
        assert _parse_view_str("12,345") == 12345

    def test_parse_view_str_invalid(self):
        from cli_anything.social.core.scraper import _parse_view_str
        assert _parse_view_str("views") == 0
        assert _parse_view_str("") == 0

    def test_youtube_categories_defined(self):
        from cli_anything.social.core.scraper import YOUTUBE_CATEGORIES
        assert "music" in YOUTUBE_CATEGORIES
        assert "gaming" in YOUTUBE_CATEGORIES
        assert "all" in YOUTUBE_CATEGORIES
