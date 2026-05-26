"""Tests for social media CLI harness."""

import json
import sys
import os
import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_media.social_cli import cli
from cli_anything.social_media.core import tiktok as tt_mod
from cli_anything.social_media.core import account_optimizer as opt_mod
from cli_anything.social_media.core import theme_pages as theme_mod


# ---------------------------------------------------------------------------
# TikTok trends
# ---------------------------------------------------------------------------

class TestTikTokTrends:
    def test_fetch_general(self):
        result = tt_mod.fetch_trending(niche="general", region="US")
        assert result.platform == "tiktok"
        assert len(result.trending_hashtags) > 0
        assert len(result.trending_sounds) > 0
        assert result.fetched_at

    def test_fetch_finance_niche(self):
        result = tt_mod.fetch_trending(niche="finance", region="US")
        hashtags = [h.hashtag for h in result.trending_hashtags]
        assert "#moneytok" in hashtags or "#investing" in hashtags

    def test_to_dict_serializable(self):
        result = tt_mod.fetch_trending(niche="fitness")
        d = result.to_dict()
        dumped = json.dumps(d)  # must not raise
        assert "trending_hashtags" in json.loads(dumped)

    def test_insights_non_empty(self):
        result = tt_mod.fetch_trending(niche="food")
        assert len(result.insights) >= 3

    def test_viral_content_types(self):
        result = tt_mod.fetch_trending()
        assert len(result.viral_content_types) >= 5

    def test_all_niches(self):
        for niche in ["general", "lifestyle", "finance", "fitness", "food"]:
            result = tt_mod.fetch_trending(niche=niche)
            assert result.platform == "tiktok"
            assert len(result.trending_hashtags) > 0


# ---------------------------------------------------------------------------
# Account optimizer
# ---------------------------------------------------------------------------

class TestAccountOptimizer:
    def test_audit_zero_checks(self):
        audit = opt_mod.audit_profile("tiktok", "testuser", 500)
        assert audit.score >= 0
        assert audit.score <= 100
        assert len(audit.warnings) > 0
        assert isinstance(audit.fixes, list)

    def test_audit_all_checks_passed(self):
        checks = {k: True for k, _, _ in opt_mod._TIKTOK_AUDIT_RULES}
        audit = opt_mod.audit_profile("tiktok", "perfect", 50000, checks)
        assert audit.score == 100
        assert len(audit.passed) == len(opt_mod._TIKTOK_AUDIT_RULES)

    def test_audit_youtube(self):
        audit = opt_mod.audit_profile("youtube", "mychannel", 1200)
        assert audit.platform == "youtube"
        assert isinstance(audit.priority_fixes, list)

    def test_playbook_launch_phase(self):
        playbook = opt_mod.build_growth_playbook("tiktok", 0)
        assert playbook.current_phase == "launch"
        assert len(playbook.daily_actions) >= 3

    def test_playbook_growth_phase(self):
        playbook = opt_mod.build_growth_playbook("tiktok", 5000)
        assert playbook.current_phase == "growth"

    def test_playbook_scale_phase(self):
        playbook = opt_mod.build_growth_playbook("tiktok", 50000)
        assert playbook.current_phase == "scale"

    def test_calendar_structure(self):
        cal = opt_mod.build_content_calendar("tiktok", "finance", 3)
        assert len(cal.week) == 7
        for day in cal.week:
            assert "date" in day
            assert "posts" in day
            assert len(day["posts"]) == 3

    def test_optimize_all(self):
        accounts = [
            {"platform": "tiktok", "username": "page1", "followers": 1000, "niche": "finance"},
            {"platform": "youtube", "username": "chan1", "followers": 500, "niche": "fitness"},
        ]
        results = opt_mod.optimize_all_accounts(accounts)
        assert len(results) == 2
        for r in results:
            assert "audit" in r
            assert "growth_playbook" in r
            assert "top_priority" in r

    def test_to_dict_serializable(self):
        audit = opt_mod.audit_profile("tiktok", "user", 100)
        json.dumps(audit.to_dict())  # must not raise
        playbook = opt_mod.build_growth_playbook("instagram", 5000)
        json.dumps(playbook.to_dict())
        cal = opt_mod.build_content_calendar("tiktok")
        json.dumps(cal.to_dict())


# ---------------------------------------------------------------------------
# Theme pages
# ---------------------------------------------------------------------------

class TestThemePages:
    def test_blueprint_motivation(self):
        bp = theme_mod.get_blueprint("motivation")
        assert bp.niche == "motivation"
        assert len(bp.page_name_ideas) > 0
        assert len(bp.monetization_stack) >= 3
        assert len(bp.legal_notes) >= 3

    def test_blueprint_all_niches(self):
        for niche in theme_mod.list_niches():
            bp = theme_mod.get_blueprint(niche)
            assert bp.niche == niche

    def test_conversion_strategy(self):
        cs = theme_mod.get_conversion_strategy("theme_page", "finance", 5000)
        assert len(cs.traffic_sources) >= 3
        assert len(cs.email_sequence) >= 5
        assert len(cs.funnel_stages) >= 5

    def test_to_dict_serializable(self):
        bp = theme_mod.get_blueprint("fitness")
        json.dumps(bp.to_dict())
        cs = theme_mod.get_conversion_strategy("theme_page", "fitness")
        json.dumps(cs.to_dict())

    def test_list_niches(self):
        niches = theme_mod.list_niches()
        assert len(niches) >= 4
        assert "finance" in niches


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_tiktok_trends_cli(self):
        result = self.runner.invoke(cli, ["--json", "trends", "tiktok", "--niche", "finance"])
        assert result.exit_code == 0
        # Strip any leading status lines to find the JSON blob
        json_text = "\n".join(
            line for line in result.output.splitlines()
            if line.startswith("{") or (json_text_started := True) and False
        )
        # Simpler: find first '{' in output
        idx = result.output.find("{")
        data = json.loads(result.output[idx:])
        assert data["platform"] == "tiktok"
        assert "trending_hashtags" in data

    def test_optimize_audit_cli(self):
        result = self.runner.invoke(cli, [
            "--json", "optimize", "audit",
            "--platform", "tiktok",
            "--username", "testuser",
            "--followers", "5000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "score" in data

    def test_theme_blueprint_cli(self):
        result = self.runner.invoke(cli, ["--json", "theme", "blueprint", "--niche", "finance"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "monetization_stack" in data

    def test_theme_niches_cli(self):
        result = self.runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "available_niches" in data

    def test_optimize_playbook_cli(self):
        result = self.runner.invoke(cli, [
            "--json", "optimize", "playbook",
            "--platform", "tiktok",
            "--followers", "3000",
            "--niche", "fitness",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "current_phase" in data
        assert data["current_phase"] == "growth"

    def test_optimize_calendar_cli(self):
        result = self.runner.invoke(cli, [
            "--json", "optimize", "calendar",
            "--platform", "tiktok",
            "--niche", "finance",
            "--posts-per-day", "2",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["week"]) == 7

    def test_optimize_all_cli(self, tmp_path):
        config = tmp_path / "accounts.json"
        accounts = [
            {"platform": "tiktok", "username": "page1", "followers": 1000, "niche": "finance"},
        ]
        config.write_text(json.dumps(accounts))
        result = self.runner.invoke(cli, ["--json", "optimize", "all", "--config", str(config)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_theme_convert_cli(self):
        result = self.runner.invoke(cli, [
            "--json", "theme", "convert",
            "--niche", "motivation",
            "--followers", "10000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "conversion_funnel" in data or "funnel_stages" in data

    def test_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "trends" in result.output
