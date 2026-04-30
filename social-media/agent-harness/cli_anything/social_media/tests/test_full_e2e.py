"""End-to-end tests for social-media CLI via Click test runner."""

import sys
import os
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from click.testing import CliRunner
from cli_anything.social_media.social_media_cli import cli
import cli_anything.social_media.social_media_cli as cli_mod


@pytest.fixture(autouse=True)
def reset_session():
    """Reset the global session before each test."""
    cli_mod._session = None
    yield
    cli_mod._session = None


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def project_file(tmp_path):
    return str(tmp_path / "test.social-media.json")


# -- Project Commands ---------------------------------------------------------

class TestProjectCommands:
    def test_project_new(self, runner):
        result = runner.invoke(cli, ["project", "new", "--name", "Test Project"])
        assert result.exit_code == 0
        assert "Test Project" in result.output or "name" in result.output.lower()

    def test_project_new_with_save(self, runner, project_file):
        result = runner.invoke(cli, ["project", "new", "--name", "Saved", "--output", project_file])
        assert result.exit_code == 0
        assert os.path.exists(project_file)

    def test_project_open(self, runner, project_file):
        runner.invoke(cli, ["project", "new", "--name", "ToOpen", "--output", project_file])
        cli_mod._session = None
        result = runner.invoke(cli, ["project", "open", project_file])
        assert result.exit_code == 0

    def test_project_info(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["project", "info"])
        assert result.exit_code == 0

    def test_project_json_output(self, runner):
        runner.invoke(cli, ["project", "new", "--name", "JSONTest"])
        result = runner.invoke(cli, ["--json", "project", "info"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "name" in data

    def test_project_save(self, runner, project_file):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["project", "save", project_file])
        assert result.exit_code == 0
        assert os.path.exists(project_file)


# -- Trends Commands ----------------------------------------------------------

class TestTrendsCommands:
    def test_trends_fetch_tiktok(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["trends", "fetch", "--platforms", "tiktok", "--limit", "5"])
        assert result.exit_code == 0

    def test_trends_fetch_youtube(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["trends", "fetch", "--platforms", "youtube", "--limit", "5"])
        assert result.exit_code == 0

    def test_trends_fetch_both(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["trends", "fetch", "--platforms", "tiktok,youtube", "--limit", "5"])
        assert result.exit_code == 0

    def test_trends_analyze_after_fetch(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["trends", "fetch", "--platforms", "tiktok", "--limit", "5"])
        result = runner.invoke(cli, ["trends", "analyze"])
        assert result.exit_code == 0

    def test_trends_analyze_fails_without_data(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["trends", "analyze"])
        assert result.exit_code != 0 or "Error" in result.output

    def test_trends_latest(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["trends", "fetch", "--platforms", "tiktok", "--limit", "3"])
        result = runner.invoke(cli, ["trends", "latest"])
        assert result.exit_code == 0

    def test_trends_history(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["trends", "fetch", "--platforms", "tiktok", "--limit", "3"])
        result = runner.invoke(cli, ["trends", "history"])
        assert result.exit_code == 0

    def test_trends_fetch_json(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["--json", "trends", "fetch", "--platforms", "tiktok", "--limit", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "data" in data
        assert "tiktok" in data["data"]


# -- Hashtags Commands --------------------------------------------------------

class TestHashtagsCommands:
    def test_hashtags_generate_finance_tiktok(self, runner):
        result = runner.invoke(cli, ["hashtags", "generate", "--niche", "finance", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_hashtags_generate_all_strategies(self, runner):
        for strategy in ["balanced", "aggressive", "niche", "stealth"]:
            result = runner.invoke(cli, ["hashtags", "generate", "--niche", "fitness",
                                         "--platform", "tiktok", "--strategy", strategy])
            assert result.exit_code == 0, f"Failed for strategy: {strategy}"

    def test_hashtags_generate_all_platforms(self, runner):
        for platform in ["tiktok", "instagram", "youtube_shorts", "youtube"]:
            result = runner.invoke(cli, ["hashtags", "generate", "--niche", "lifestyle",
                                         "--platform", platform])
            assert result.exit_code == 0, f"Failed for platform: {platform}"

    def test_hashtags_generate_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "generate", "--niche", "beauty",
                                      "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert len(data["hashtags"]) > 0

    def test_hashtags_score(self, runner):
        result = runner.invoke(cli, ["hashtags", "score", "#fyp", "#money", "#investing"])
        assert result.exit_code == 0

    def test_hashtags_score_json(self, runner):
        result = runner.invoke(cli, ["--json", "hashtags", "score", "#fyp", "#money"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "avg_score" in data
        assert "scored_tags" in data

    def test_hashtags_niches(self, runner):
        result = runner.invoke(cli, ["hashtags", "niches"])
        assert result.exit_code == 0

    def test_hashtags_list_empty(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["hashtags", "list"])
        assert result.exit_code == 0

    def test_hashtags_generate_save(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["hashtags", "generate", "--niche", "food",
                                      "--platform", "tiktok", "--save-as", "food-set"])
        assert result.exit_code == 0
        result2 = runner.invoke(cli, ["hashtags", "list"])
        assert result2.exit_code == 0


# -- Music Commands -----------------------------------------------------------

class TestMusicCommands:
    def test_music_trending_tiktok(self, runner):
        result = runner.invoke(cli, ["music", "trending", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_music_trending_youtube(self, runner):
        result = runner.invoke(cli, ["music", "trending", "--platform", "youtube"])
        assert result.exit_code == 0

    def test_music_trending_json(self, runner):
        result = runner.invoke(cli, ["--json", "music", "trending", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trending_sounds" in data

    def test_music_recommend(self, runner):
        for niche in ["finance", "fitness", "lifestyle", "fashion"]:
            result = runner.invoke(cli, ["music", "recommend", niche])
            assert result.exit_code == 0, f"Failed for niche: {niche}"

    def test_music_categories(self, runner):
        result = runner.invoke(cli, ["music", "categories"])
        assert result.exit_code == 0


# -- Account Commands ---------------------------------------------------------

class TestAccountCommands:
    def test_account_add(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["account", "add", "myhandle", "tiktok", "finance",
                                      "--followers", "5000"])
        assert result.exit_code == 0
        assert "myhandle" in result.output

    def test_account_list(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "user1", "tiktok", "fitness"])
        result = runner.invoke(cli, ["account", "list"])
        assert result.exit_code == 0

    def test_account_optimize(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "optuser", "tiktok", "finance",
                             "--followers", "12000", "--bio", "Finance tips 💰 Link ↓"])
        result = runner.invoke(cli, ["account", "optimize", "optuser"])
        assert result.exit_code == 0

    def test_account_optimize_json(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "jsonuser", "instagram", "beauty",
                             "--followers", "8000"])
        result = runner.invoke(cli, ["--json", "account", "optimize", "jsonuser"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "optimization_score" in data
        assert "posting_plan" in data
        assert "monetization_roadmap" in data

    def test_account_score(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "scoreuser", "tiktok", "travel"])
        result = runner.invoke(cli, ["account", "score", "scoreuser"])
        assert result.exit_code == 0

    def test_account_update(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "updateme", "tiktok", "motivation"])
        result = runner.invoke(cli, ["account", "update", "updateme", "--followers", "25000"])
        assert result.exit_code == 0

    def test_account_remove(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "delme", "tiktok", "food"])
        result = runner.invoke(cli, ["account", "remove", "delme"])
        assert result.exit_code == 0

    def test_account_schedule(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "sched", "tiktok", "fitness"])
        result = runner.invoke(cli, ["account", "schedule", "sched",
                                      "--mon", "8AM", "--wed", "7PM", "--fri", "6PM"])
        assert result.exit_code == 0

    def test_multiple_platforms(self, runner):
        runner.invoke(cli, ["project", "new"])
        for platform in ["tiktok", "instagram", "youtube", "twitter"]:
            result = runner.invoke(cli, ["account", "add", f"user_{platform}", platform, "lifestyle"])
            assert result.exit_code == 0, f"Failed for platform: {platform}"


# -- Theme Page Commands -------------------------------------------------------

class TestThemePageCommands:
    def test_theme_guide(self, runner):
        result = runner.invoke(cli, ["theme-page", "guide", "--niche", "finance"])
        assert result.exit_code == 0

    def test_theme_guide_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "guide", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "conversion_funnel" in data
        assert "dm_scripts" in data
        assert "tools" in data

    def test_theme_niches(self, runner):
        result = runner.invoke(cli, ["theme-page", "niches"])
        assert result.exit_code == 0

    def test_theme_niches_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_theme_niche_specific(self, runner):
        result = runner.invoke(cli, ["theme-page", "niche", "finance"])
        assert result.exit_code == 0

    def test_theme_funnel_all_stages(self, runner):
        for stage in range(1, 6):
            result = runner.invoke(cli, ["theme-page", "funnel", str(stage)])
            assert result.exit_code == 0, f"Failed for stage {stage}"

    def test_theme_dm_scripts(self, runner):
        result = runner.invoke(cli, ["theme-page", "dm-scripts"])
        assert result.exit_code == 0

    def test_theme_dm_scripts_json(self, runner):
        result = runner.invoke(cli, ["--json", "theme-page", "dm-scripts"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "scripts" in data
        assert "new_follower_welcome" in data["scripts"]


# -- Session Commands ---------------------------------------------------------

class TestSessionCommands:
    def test_session_status(self, runner):
        runner.invoke(cli, ["project", "new"])
        result = runner.invoke(cli, ["session", "status"])
        assert result.exit_code == 0

    def test_session_undo_redo(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "acc1", "tiktok", "finance"])
        result = runner.invoke(cli, ["session", "undo"])
        assert result.exit_code == 0

    def test_session_history(self, runner):
        runner.invoke(cli, ["project", "new"])
        runner.invoke(cli, ["account", "add", "acc1", "tiktok", "finance"])
        result = runner.invoke(cli, ["session", "history"])
        assert result.exit_code == 0


# -- Full Workflow E2E Test ----------------------------------------------------

class TestFullWorkflow:
    def test_complete_workflow(self, runner, tmp_path):
        project_path = str(tmp_path / "workflow.json")

        # 1. Create project
        r = runner.invoke(cli, ["project", "new", "--name", "Brand X", "--output", project_path])
        assert r.exit_code == 0

        # 2. Fetch trends
        r = runner.invoke(cli, ["trends", "fetch", "--platforms", "tiktok,youtube", "--limit", "5"])
        assert r.exit_code == 0

        # 3. Analyze
        r = runner.invoke(cli, ["trends", "analyze"])
        assert r.exit_code == 0

        # 4. Generate hashtags
        r = runner.invoke(cli, ["hashtags", "generate", "--niche", "finance",
                                 "--platform", "tiktok", "--save-as", "finance-tiktok"])
        assert r.exit_code == 0

        # 5. Get trending music
        r = runner.invoke(cli, ["music", "trending", "--platform", "tiktok"])
        assert r.exit_code == 0

        # 6. Add account
        r = runner.invoke(cli, ["account", "add", "brandx", "tiktok", "finance",
                                 "--followers", "25000", "--bio", "Finance tips 💰 New video daily ↓"])
        assert r.exit_code == 0

        # 7. Optimize account
        r = runner.invoke(cli, ["--json", "account", "optimize", "brandx"])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["optimization_score"] >= 0

        # 8. Get theme page guide
        r = runner.invoke(cli, ["theme-page", "guide", "--niche", "finance"])
        assert r.exit_code == 0

        # 9. Save project
        r = runner.invoke(cli, ["project", "save"])
        assert r.exit_code == 0
        assert os.path.exists(project_path)

        # 10. Reload and verify
        cli_mod._session = None
        r = runner.invoke(cli, ["project", "open", project_path])
        assert r.exit_code == 0
        r = runner.invoke(cli, ["--json", "project", "info"])
        assert r.exit_code == 0
        info = json.loads(r.output)
        assert info["name"] == "Brand X"
        assert info["accounts"] == 1
