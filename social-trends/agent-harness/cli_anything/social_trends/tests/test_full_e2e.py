"""End-to-end CLI integration tests for Social Trends."""

import json
import pytest
from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import cli


@pytest.fixture(autouse=True)
def patch_session(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.session._CONFIG_DIR", tmp_path
    )
    monkeypatch.setattr(
        "cli_anything.social_trends.core.session._CONFIG_FILE", tmp_path / "config.json"
    )
    monkeypatch.setattr(
        "cli_anything.social_trends.core.session._CACHE_FILE", tmp_path / "cache.json"
    )
    # Reset global session between tests
    import cli_anything.social_trends.social_trends_cli as cli_mod
    cli_mod._session = None
    yield
    cli_mod._session = None


def run(*args):
    runner = CliRunner()
    return runner.invoke(cli, ["--json"] + list(args), catch_exceptions=False)


class TestConfigCommands:
    def test_set_key_youtube(self):
        r = run("config", "set-key", "youtube", "AIzaSyABCDEFGHIJKLMNOP")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["success"] is True
        assert data["key"] == "youtube"

    def test_config_show(self):
        run("config", "set-key", "youtube", "AIzaSyABCDEFGHIJKLMNOP")
        r = run("config", "show")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "api_keys" in data

    def test_set_niche(self):
        r = run("config", "set-niche", "fitness", "finance")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "fitness" in data["niches"]

    def test_set_region(self):
        r = run("config", "set-region", "US", "GB")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "US" in data["regions"]


class TestTrendsCommands:
    def test_fetch_youtube_demo(self):
        r = run("trends", "fetch", "--platform", "youtube", "--max", "5")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["platform"] == "youtube"
        assert "videos" in data

    def test_fetch_tiktok_demo(self):
        r = run("trends", "fetch", "--platform", "tiktok", "--max", "5")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["platform"] == "tiktok"
        assert "top_hashtags" in data

    def test_fetch_both(self):
        r = run("trends", "fetch", "--platform", "both")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "youtube" in data
        assert "tiktok" in data
        assert "cross_platform_hashtags" in data

    def test_hashtags_fitness(self):
        r = run("trends", "hashtags", "--niche", "fitness")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["niche"] == "fitness"
        assert len(data["recommended_mix"]) > 5

    def test_hashtags_instagram_platform(self):
        r = run("trends", "hashtags", "--niche", "travel", "--platform", "instagram")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "instagram" in data["sets"]

    def test_music_all(self):
        r = run("trends", "music")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "tracks" in data
        assert len(data["tracks"]) > 0

    def test_music_rising(self):
        r = run("trends", "music", "--type", "rising")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert all(t["trend"] == "rising" for t in data["tracks"])

    def test_viral_patterns(self):
        r = run("trends", "viral-patterns")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "content_formats" in data
        assert "hook_formulas" in data


class TestAccountsCommands:
    def test_add_account(self):
        r = run("accounts", "add", "tiktok", "@fitpage", "fitness",
                "--followers", "5000", "--bio", "Daily fitness tips | DM for coaching")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["success"] is True

    def test_list_accounts_empty(self):
        r = run("accounts", "list")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data == []

    def test_list_after_add(self):
        run("accounts", "add", "tiktok", "@user1", "fitness", "--followers", "1000")
        run("accounts", "add", "instagram", "@user2", "finance", "--followers", "500")
        r = run("accounts", "list")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) == 2

    def test_audit_account(self):
        run("accounts", "add", "instagram", "@mypage", "fitness",
            "--followers", "8000", "--bio", "Fitness tips | DM for free plan")
        r = run("accounts", "audit", "instagram_mypage")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "score" in data
        assert 0 <= data["score"] <= 100
        assert "recommendations" in data

    def test_audit_nonexistent(self):
        runner = CliRunner()
        r = runner.invoke(cli, ["--json", "accounts", "audit", "fake_account"],
                          catch_exceptions=False)
        assert r.exit_code != 0

    def test_optimize_bio(self):
        run("accounts", "add", "tiktok", "@finpage", "finance", "--followers", "2000")
        r = run("accounts", "optimize-bio", "tiktok_finpage", "--niche", "finance")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "recommended_bio" in data
        assert len(data["alternatives"]) >= 4

    def test_bulk_audit(self):
        run("accounts", "add", "tiktok", "@fit1", "fitness",
            "--followers", "3000", "--bio", "Fitness daily | Link below")
        run("accounts", "add", "instagram", "@fin1", "finance",
            "--followers", "7000", "--bio", "Money tips | DM for guide")
        r = run("accounts", "bulk-audit")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["total_accounts"] == 2

    def test_schedule(self):
        run("accounts", "add", "tiktok", "@sched", "fitness")
        r = run("accounts", "schedule", "tiktok_sched", "--frequency", "aggressive")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["frequency"] == "aggressive"
        assert len(data["content_calendar_template"]) == 7

    def test_update_account(self):
        run("accounts", "add", "tiktok", "@upd", "fitness")
        r = run("accounts", "update", "tiktok_upd", "--followers", "99999")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "followers" in data["updated_fields"]


class TestThemePageCommands:
    def test_niches_list(self):
        r = run("theme-page", "niches")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) >= 4

    def test_niches_sorted_growth(self):
        r = run("theme-page", "niches", "--sort-by", "growth")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) > 0

    def test_niche_detail(self):
        r = run("theme-page", "niche-detail", "fitness_motivation")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["display"] == "Fitness Motivation"
        assert "monetization_paths" in data

    def test_create_theme_page(self):
        r = run("theme-page", "create", "DailyFit", "fitness_motivation",
                "tiktok", "instagram")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["success"] is True
        assert "quick_start" in data
        assert len(data["quick_start"]) >= 5

    def test_learn(self):
        r = run("theme-page", "learn")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "what_is_a_theme_page" in data
        assert "30_day_action_plan" in data

    def test_funnels_list(self):
        r = run("theme-page", "funnels")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert any(f["id"] == "dm_funnel" for f in data)

    def test_playbook_dm(self):
        r = run("theme-page", "playbook", "dm_funnel", "--niche", "fitness")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "steps" in data
        assert "niche_specific_tips" in data

    def test_playbook_email(self):
        r = run("theme-page", "playbook", "email_list_funnel")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["funnel_type"] == "email_list_funnel"

    def test_list_theme_pages(self):
        run("theme-page", "create", "FitDaily", "fitness_motivation", "tiktok")
        run("theme-page", "create", "MoneyMoves", "money_mindset", "instagram")
        r = run("theme-page", "list")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert len(data) == 2


class TestSessionCommands:
    def test_status(self):
        r = run("session", "status")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert "accounts_count" in data

    def test_undo_redo_cycle(self):
        run("accounts", "add", "tiktok", "@undotest", "fitness")
        r = run("session", "undo")
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["success"] is True

        r = run("session", "redo")
        assert r.exit_code == 0

    def test_history(self):
        run("config", "set-niche", "fitness")
        run("accounts", "add", "tiktok", "@hist", "fitness")
        r = run("session", "history")
        assert r.exit_code == 0
