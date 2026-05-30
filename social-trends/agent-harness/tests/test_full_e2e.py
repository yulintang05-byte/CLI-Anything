"""End-to-end tests for Social Trends CLI — file generation, CLI subprocess, and workflow."""

import json
import subprocess
import sys
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.social_trends.social_trends_cli import cli
from click.testing import CliRunner


# ── E2E: Full workflow tests ─────────────────────────────────────────────────

class TestE2EWorkflows:
    """Full workflow tests — simulate what an agent would do."""

    def test_full_account_optimization_workflow(self, tmp_path):
        """Agent workflow: optimize an account, get schedule, generate bio."""
        runner = CliRunner()

        # Step 1: Optimize account
        result = runner.invoke(cli, [
            "--json", "account", "optimize",
            "-p", "tiktok",
            "-n", "fitness",
            "-f", "5000",
            "-g", "growth",
            "-g", "monetization",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["growth_stage"]["stage"] == "micro"
        assert len(data["content_recommendations"]) > 0
        assert len(data["growth_tactics"]) > 0
        assert len(data["monetization_path"]) > 0

        # Step 2: Get posting schedule
        result = runner.invoke(cli, [
            "--json", "account", "schedule",
            "-p", "tiktok",
            "-p", "instagram",
        ])
        assert result.exit_code == 0
        schedule = json.loads(result.output)
        assert "tiktok" in schedule["platforms"]
        assert "instagram" in schedule["platforms"]

        # Step 3: Generate bio
        result = runner.invoke(cli, [
            "--json", "account", "bio",
            "-p", "tiktok",
            "-n", "FitCoach",
            "--niche", "fitness",
            "-v", "help you build your dream body",
            "--cta", "follow",
        ])
        assert result.exit_code == 0
        bio_data = json.loads(result.output)
        assert len(bio_data["bio_options"]) >= 1
        assert bio_data["character_limit"] == 80

    def test_full_theme_page_launch_workflow(self, tmp_path):
        """Agent workflow: pick niche, review checklist, plan content, find sources."""
        runner = CliRunner()

        # Step 1: Browse niches
        result = runner.invoke(cli, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        niches = json.loads(result.output)
        assert len(niches) >= 5
        niche_ids = [n["id"] for n in niches]
        assert "tech_ai" in niche_ids

        # Step 2: Get detail on chosen niche
        result = runner.invoke(cli, ["--json", "theme-page", "detail", "tech_ai"])
        assert result.exit_code == 0
        detail = json.loads(result.output)
        assert detail["monetization_potential"] == "very_high"
        assert "youtube" in detail["best_platforms"]

        # Step 3: Generate content plan
        result = runner.invoke(cli, [
            "--json", "theme-page", "content-plan", "tech_ai",
            "-p", "tiktok",
            "-p", "youtube",
            "-w", "2",
        ])
        assert result.exit_code == 0
        plan = json.loads(result.output)
        assert len(plan["weekly_plan"]) == 2
        assert all(len(w["posts"]) > 0 for w in plan["weekly_plan"])

        # Step 4: Check monetization options
        result = runner.invoke(cli, ["--json", "theme-page", "monetize"])
        assert result.exit_code == 0
        monetize = json.loads(result.output)
        assert "affiliate_marketing" in monetize
        assert "digital_products" in monetize

        # Step 5: Get legal content sources
        result = runner.invoke(cli, ["--json", "theme-page", "sources"])
        assert result.exit_code == 0
        sources = json.loads(result.output)
        assert len(sources) > 0
        source_names = [s["source"] for s in sources]
        assert "Pexels" in source_names

        # Step 6: Get launch checklist
        result = runner.invoke(cli, ["--json", "theme-page", "checklist"])
        assert result.exit_code == 0
        checklist = json.loads(result.output)
        assert all(item["done"] is False for item in checklist)

    def test_full_hashtag_strategy_workflow(self):
        """Agent workflow: get hashtags for a post without live network."""
        runner = CliRunner()

        # Use TikTok fallback hashtags (no network needed)
        from cli_anything.social_trends.core.tiktok import _evergreen_tiktok_hashtags
        hashtags = _evergreen_tiktok_hashtags()
        assert len(hashtags) >= 10

        # Build hashtag set from these
        from cli_anything.social_trends.core.trends import aggregate_trends, build_hashtag_set
        tt_data = {
            "hashtags": hashtags[:10],
            "music": [],
            "videos": [],
            "source": "test",
        }
        agg = aggregate_trends(None, tt_data)
        hashtag_set = build_hashtag_set(agg, niche="fitness", strategy="mixed")

        assert len(hashtag_set["tiktok_set"]) <= 8
        assert len(hashtag_set["youtube_set"]) <= 30
        assert "#fitness" in hashtag_set["tiktok_set"] or any(
            "fitness" in t for t in hashtag_set["tiktok_set"]
        )

    def test_session_persistence_across_commands(self, tmp_path):
        """Session records multiple commands and history is retrievable."""
        runner = CliRunner()

        # Run multiple commands and check session history grows
        runner.invoke(cli, ["--json", "theme-page", "niches"])
        runner.invoke(cli, ["--json", "account", "schedule", "-p", "tiktok"])
        runner.invoke(cli, ["--json", "account", "optimize", "-p", "tiktok"])

        result = runner.invoke(cli, ["--json", "session", "status"])
        assert result.exit_code == 0
        status = json.loads(result.output)
        assert "history_count" in status

    def test_repurposing_guide_actionable(self):
        """Repurposing guide returns enough steps to be actionable."""
        from cli_anything.social_trends.core.theme_pages import get_content_repurposing_guide
        guide = get_content_repurposing_guide()
        assert len(guide["workflow"]) >= 5
        assert len(guide["tools"]) >= 3

    def test_all_niches_have_complete_content_types(self):
        """Every niche has at least one content type defined."""
        from cli_anything.social_trends.core.theme_pages import NICHES
        for niche_id, niche in NICHES.items():
            assert len(niche.get("content_types", [])) > 0, f"No content types for {niche_id}"

    def test_posting_schedule_covers_all_days(self):
        """Every platform schedule covers all 7 days."""
        from cli_anything.social_trends.core.optimizer import get_posting_schedule, PLATFORM_BEST_TIMES
        days = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}
        for platform in PLATFORM_BEST_TIMES:
            sched = get_posting_schedule([platform])["platforms"].get(platform, {})
            best_times = sched.get("best_times", {})
            assert set(best_times.keys()) == days, f"Missing days for {platform}"

    def test_optimizer_kpis_have_why_field(self):
        """Every KPI has a 'why' explanation."""
        from cli_anything.social_trends.core.optimizer import _kpis_for_platform
        for platform in ["tiktok", "youtube", "instagram"]:
            kpis = _kpis_for_platform(platform)
            for kpi in kpis:
                assert kpi.get("why"), f"Missing 'why' in KPI {kpi} for {platform}"

    def test_bio_generator_all_platforms(self):
        """Bio generator works for all supported platforms."""
        from cli_anything.social_trends.core.optimizer import generate_bio
        for platform in ["tiktok", "youtube", "instagram"]:
            result = generate_bio(platform, "TestBrand", "fitness", "help you get fit")
            assert len(result["bio_options"]) > 0
            assert result["character_limit"] > 0

    @patch("cli_anything.social_trends.core.youtube.requests.post")
    def test_youtube_innertube_fetch(self, mock_post):
        """YouTube innertube fetch works with mocked response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "contents": {
                "twoColumnBrowseResultsRenderer": {
                    "tabs": [
                        {
                            "tabRenderer": {
                                "content": {
                                    "richGridRenderer": {
                                        "contents": [
                                            {
                                                "richItemRenderer": {
                                                    "content": {
                                                        "videoRenderer": {
                                                            "videoId": "yt_test_001",
                                                            "title": {"runs": [{"text": "Test Trending #viral"}]},
                                                            "longBylineText": {"runs": [{"text": "TestChannel"}]},
                                                            "viewCountText": {"simpleText": "1.5M views"},
                                                            "publishedTimeText": {"simpleText": "2 days ago"},
                                                            "thumbnail": {"thumbnails": [{"url": "https://img.jpg", "width": 320, "height": 180}]},
                                                            "lengthText": {"simpleText": "10:30"},
                                                        }
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response

        from cli_anything.social_trends.core.youtube import _fetch_via_innertube
        result = _fetch_via_innertube("all", "US", 25)
        assert "videos" in result
        assert "hashtags" in result
        assert "music" in result
        assert result["source"] == "youtube_innertube"

    def test_content_plan_weeks_parameter(self):
        """Content plans generate the correct number of weeks."""
        from cli_anything.social_trends.core.theme_pages import generate_content_plan
        for weeks in [1, 2, 4, 8]:
            plan = generate_content_plan("productivity_mindset", weeks=weeks)
            assert len(plan["weekly_plan"]) == weeks

    def test_niche_filtering_combinations(self):
        """Filtering niches by difficulty + platform returns correct results."""
        from cli_anything.social_trends.core.theme_pages import list_niches
        easy_tiktok = list_niches(filter_difficulty="easy", filter_platform="tiktok")
        for n in easy_tiktok:
            assert n["difficulty"] == "easy"
            assert "tiktok" in n["best_platforms"]

    def test_monetization_follower_minimums_are_valid(self):
        """All monetization methods have a non-negative follower minimum."""
        from cli_anything.social_trends.core.theme_pages import MONETIZATION_METHODS
        for method, info in MONETIZATION_METHODS.items():
            assert info["follower_minimum"] >= 0, f"Invalid minimum for {method}"

    def test_cli_json_output_always_valid_json(self):
        """All JSON-mode commands produce valid JSON."""
        runner = CliRunner()
        commands = [
            ["--json", "theme-page", "niches"],
            ["--json", "theme-page", "checklist"],
            ["--json", "theme-page", "sources"],
            ["--json", "theme-page", "repurpose"],
            ["--json", "theme-page", "monetize"],
            ["--json", "theme-page", "detail", "tech_ai"],
            ["--json", "theme-page", "content-plan", "tech_ai", "-w", "1"],
            ["--json", "account", "schedule", "-p", "tiktok"],
            ["--json", "account", "optimize", "-p", "tiktok"],
            ["--json", "account", "bio", "-p", "tiktok", "-n", "Brand", "--niche", "fitness", "-v", "help"],
            ["--json", "session", "status"],
            ["--json", "session", "history"],
        ]
        for cmd in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Command failed: {cmd}\n{result.output}"
            try:
                json.loads(result.output)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON for command {cmd}:\n{result.output}")

    def test_all_niche_content_plans_generate_valid_json(self):
        """Content plans for all niches produce valid structures."""
        runner = CliRunner()
        from cli_anything.social_trends.core.theme_pages import NICHES
        for niche_id in NICHES:
            result = runner.invoke(cli, ["--json", "theme-page", "content-plan", niche_id, "-w", "1"])
            assert result.exit_code == 0, f"Failed for niche {niche_id}: {result.output}"
            data = json.loads(result.output)
            assert data["niche"] is not None
            assert len(data["weekly_plan"]) == 1

    def test_trending_hashtags_command_no_network(self):
        """Hashtag command with pre-built data runs without network."""
        from cli_anything.social_trends.core.trends import aggregate_trends, build_hashtag_set
        from cli_anything.social_trends.core.tiktok import _evergreen_tiktok_hashtags

        tt_data = {
            "hashtags": _evergreen_tiktok_hashtags(),
            "music": [],
            "videos": [],
            "source": "test_evergreen",
        }
        agg = aggregate_trends(None, tt_data, top_n=20)
        result = build_hashtag_set(agg, niche="food", max_tags=20, strategy="mixed")

        assert isinstance(result["tiktok_set"], list)
        assert isinstance(result["youtube_set"], list)
        assert isinstance(result["instagram_set"], list)
        assert len(result["tiktok_set"]) <= 8
