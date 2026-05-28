"""Tests for social-trends CLI harness."""
import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import cli
from cli_anything.social_trends.platforms import tiktok as tt
from cli_anything.social_trends.platforms import youtube as yt
from cli_anything.social_trends.core import optimizer as opt
from cli_anything.social_trends.core import trend_analyzer as ta


# ── TikTok platform tests ──────────────────────────────────────────────────────

class TestTikTokPlatform:
    def test_trending_hashtags_returns_list(self):
        tags = tt.get_trending_hashtags(limit=10)
        assert isinstance(tags, list)
        assert len(tags) <= 10
        assert len(tags) > 0

    def test_hashtags_have_required_fields(self):
        tags = tt.get_trending_hashtags(limit=5)
        for tag in tags:
            assert "hashtag" in tag
            assert "platform" in tag
            assert tag["platform"] == "tiktok"
            assert tag["hashtag"].startswith("#")

    def test_trending_sounds_returns_list(self):
        sounds = tt.get_trending_sounds(limit=10)
        assert isinstance(sounds, list)
        assert len(sounds) == 10

    def test_sounds_have_rank_and_score(self):
        sounds = tt.get_trending_sounds(limit=5)
        for sound in sounds:
            assert "rank" in sound
            assert "sound" in sound
            assert "trend_score" in sound
            assert sound["platform"] == "tiktok"

    def test_trending_effects_returns_list(self):
        effects = tt.get_trending_effects(limit=5)
        assert isinstance(effects, list)
        assert len(effects) == 5
        for e in effects:
            assert "effect" in e
            assert "rank" in e

    def test_niche_hashtags_fitness(self):
        tags = tt.get_niche_hashtags("fitness", limit=10)
        assert len(tags) > 0
        for tag in tags:
            assert "hashtag" in tag
            assert tag["niche"] == "fitness"

    def test_niche_hashtags_food(self):
        tags = tt.get_niche_hashtags("food", limit=10)
        assert len(tags) > 0

    def test_niche_hashtags_unknown_falls_back(self):
        tags = tt.get_niche_hashtags("unknownniche123", limit=5)
        assert isinstance(tags, list)

    def test_hashtags_category_filter(self):
        tags = tt.get_trending_hashtags(category="fitness", limit=10)
        assert isinstance(tags, list)


# ── YouTube platform tests ─────────────────────────────────────────────────────

class TestYouTubePlatform:
    @patch("cli_anything.social_trends.platforms.youtube.requests.get")
    def test_get_trending_videos_no_data(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html>No ytInitialData here</html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        videos = yt.get_trending_videos(limit=5)
        assert isinstance(videos, list)

    @patch("cli_anything.social_trends.platforms.youtube.requests.get")
    def test_get_trending_hashtags_no_data(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        tags = yt.get_trending_hashtags(limit=10)
        assert isinstance(tags, list)

    @patch("cli_anything.social_trends.platforms.youtube.requests.get")
    def test_get_viral_keywords_empty(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        keywords = yt.get_viral_keywords(limit=10)
        assert isinstance(keywords, list)

    def test_yt_initial_data_connection_failure(self):
        with patch("cli_anything.social_trends.platforms.youtube.requests.get", side_effect=Exception("timeout")):
            result = yt._yt_initial_data("https://example.com")
            assert result == {}

    def test_walk_flat_dict(self):
        data = {"title": {"runs": [{"text": "hello"}]}, "other": "x"}
        results = []
        yt._walk(data, "runs", results)
        assert results == [[{"text": "hello"}]]

    def test_walk_nested_list(self):
        data = [{"key": "a"}, {"key": "b"}]
        results = []
        yt._walk(data, "key", results)
        assert "a" in results and "b" in results


# ── Optimizer tests ────────────────────────────────────────────────────────────

class TestOptimizer:
    def test_account_checklist_all_platforms(self):
        checklist = opt.get_account_checklist("all")
        assert isinstance(checklist, dict)
        assert "tiktok" in checklist
        assert "youtube" in checklist

    def test_account_checklist_tiktok(self):
        checklist = opt.get_account_checklist("tiktok")
        assert "tiktok" in checklist
        assert isinstance(checklist["tiktok"], list)
        assert len(checklist["tiktok"]) > 0

    def test_account_checklist_youtube(self):
        checklist = opt.get_account_checklist("youtube")
        assert "youtube" in checklist

    def test_account_checklist_unknown(self):
        checklist = opt.get_account_checklist("snapchat")
        assert checklist == {"snapchat": []}

    def test_best_posting_times_all(self):
        times = opt.get_best_posting_times("all")
        assert "tiktok" in times
        assert "youtube" in times
        assert "instagram" in times

    def test_best_posting_times_tiktok(self):
        times = opt.get_best_posting_times("tiktok")
        assert "tiktok" in times
        for slot in times["tiktok"]:
            assert "day" in slot
            assert "time" in slot

    def test_theme_page_guide_structure(self):
        guide = opt.get_theme_page_guide()
        assert "concept" in guide
        assert "profitable_niches" in guide
        assert "step_by_step" in guide
        assert "content_sourcing" in guide
        assert "converting_theme_pages" in guide

    def test_theme_page_guide_niches(self):
        guide = opt.get_theme_page_guide()
        niches = guide["profitable_niches"]
        assert len(niches) >= 5
        for niche in niches:
            assert "niche" in niche
            assert "monetization" in niche

    def test_content_calendar_tiktok(self):
        cal = opt.get_content_calendar("tiktok", posts_per_week=7)
        assert len(cal) == 7
        for day in cal:
            assert "day" in day
            assert "format" in day
            assert "platform" in day

    def test_content_calendar_short_week(self):
        cal = opt.get_content_calendar("youtube", posts_per_week=3)
        assert len(cal) == 3

    def test_growth_hacks_tiktok(self):
        hacks = opt.get_growth_hacks("tiktok")
        assert isinstance(hacks, list)
        assert len(hacks) > 0
        for h in hacks:
            assert "hack" in h
            assert "description" in h

    def test_growth_hacks_youtube(self):
        hacks = opt.get_growth_hacks("youtube")
        assert isinstance(hacks, list)

    def test_growth_hacks_instagram(self):
        hacks = opt.get_growth_hacks("instagram")
        assert isinstance(hacks, list)

    def test_growth_hacks_unknown_falls_back(self):
        hacks = opt.get_growth_hacks("snapchat")
        assert isinstance(hacks, list)


# ── Trend Analyzer tests ───────────────────────────────────────────────────────

class TestTrendAnalyzer:
    @patch("cli_anything.social_trends.core.trend_analyzer.yt.get_trending_videos")
    @patch("cli_anything.social_trends.core.trend_analyzer.yt.get_viral_keywords")
    @patch("cli_anything.social_trends.core.trend_analyzer.tt.get_trending_hashtags")
    def test_cross_platform_trends(self, mock_tt, mock_kw, mock_yt):
        mock_yt.return_value = [
            {"title": "fitness workout viral", "platform": "youtube"}
        ]
        mock_kw.return_value = [
            {"keyword": "fitness", "frequency": 5, "platform": "youtube"},
            {"keyword": "workout", "frequency": 3, "platform": "youtube"},
        ]
        mock_tt.return_value = [
            {"hashtag": "#fitness", "platform": "tiktok"},
            {"hashtag": "#workout", "platform": "tiktok"},
        ]
        trends = ta.get_cross_platform_trends(limit=5)
        assert isinstance(trends, list)

    @patch("cli_anything.social_trends.core.trend_analyzer.yt.get_trending_videos")
    @patch("cli_anything.social_trends.core.trend_analyzer.tt.get_niche_hashtags")
    @patch("cli_anything.social_trends.core.trend_analyzer.tt.get_trending_sounds")
    def test_generate_content_ideas(self, mock_sounds, mock_tags, mock_yt):
        mock_yt.return_value = []
        mock_tags.return_value = [{"hashtag": "#gym", "niche": "fitness"}]
        mock_sounds.return_value = [{"sound": "test sound", "rank": 1, "trend_score": 90, "platform": "tiktok", "category": "pop", "source": "curated", "tip": "use it"}]
        ideas = ta.generate_content_ideas("fitness", count=5)
        assert isinstance(ideas, list)
        assert len(ideas) <= 5

    def test_viral_formula_all(self):
        formulas = ta.get_viral_formula("all")
        assert isinstance(formulas, list)
        types = [f["type"] for f in formulas]
        assert "hook" in types
        assert "structure" in types
        assert "cta" in types

    def test_viral_formula_hook(self):
        formulas = ta.get_viral_formula("hook")
        assert len(formulas) == 1
        assert formulas[0]["type"] == "hook"

    def test_generate_idea_deterministic(self):
        idea1 = ta._generate_idea("fitness")
        idea2 = ta._generate_idea("fitness")
        assert idea1 == idea2

    def test_niche_templates_structure(self):
        templates = ta._niche_templates("cooking")
        assert len(templates) > 0
        for t in templates:
            assert "idea" in t
            assert "format" in t
            assert "hook" in t


# ── CLI integration tests ──────────────────────────────────────────────────────

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_cli_help(self):
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Social Trends" in result.output

    def test_youtube_group_help(self):
        result = self.runner.invoke(cli, ["youtube", "--help"])
        assert result.exit_code == 0

    def test_tiktok_group_help(self):
        result = self.runner.invoke(cli, ["tiktok", "--help"])
        assert result.exit_code == 0

    def test_optimize_group_help(self):
        result = self.runner.invoke(cli, ["optimize", "--help"])
        assert result.exit_code == 0

    def test_theme_pages_help(self):
        result = self.runner.invoke(cli, ["theme-pages", "--help"])
        assert result.exit_code == 0

    def test_tiktok_hashtags_command(self):
        result = self.runner.invoke(cli, ["tiktok", "hashtags", "--limit", "5"])
        assert result.exit_code == 0

    def test_tiktok_sounds_command(self):
        result = self.runner.invoke(cli, ["tiktok", "sounds", "--limit", "5"])
        assert result.exit_code == 0

    def test_tiktok_effects_command(self):
        result = self.runner.invoke(cli, ["tiktok", "effects", "--limit", "5"])
        assert result.exit_code == 0

    def test_tiktok_niche_command(self):
        result = self.runner.invoke(cli, ["tiktok", "niche", "fitness"])
        assert result.exit_code == 0

    def test_optimize_checklist_all(self):
        result = self.runner.invoke(cli, ["optimize", "checklist", "--platform", "all"])
        assert result.exit_code == 0

    def test_optimize_checklist_tiktok(self):
        result = self.runner.invoke(cli, ["optimize", "checklist", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_optimize_posting_times(self):
        result = self.runner.invoke(cli, ["optimize", "posting-times"])
        assert result.exit_code == 0

    def test_optimize_hacks(self):
        result = self.runner.invoke(cli, ["optimize", "hacks", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_optimize_calendar(self):
        result = self.runner.invoke(cli, ["optimize", "calendar", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_theme_pages_all(self):
        result = self.runner.invoke(cli, ["theme-pages"])
        assert result.exit_code == 0

    def test_theme_pages_niches(self):
        result = self.runner.invoke(cli, ["theme-pages", "--section", "niches"])
        assert result.exit_code == 0

    def test_theme_pages_steps(self):
        result = self.runner.invoke(cli, ["theme-pages", "--section", "steps"])
        assert result.exit_code == 0

    def test_theme_pages_converting(self):
        result = self.runner.invoke(cli, ["theme-pages", "--section", "converting"])
        assert result.exit_code == 0

    def test_theme_pages_funnel(self):
        result = self.runner.invoke(cli, ["theme-pages", "--section", "funnel"])
        assert result.exit_code == 0

    def test_viral_command(self):
        result = self.runner.invoke(cli, ["viral"])
        assert result.exit_code == 0

    def test_viral_hook_type(self):
        result = self.runner.invoke(cli, ["viral", "--type", "hook"])
        assert result.exit_code == 0

    def test_hacks_command(self):
        result = self.runner.invoke(cli, ["hacks"])
        assert result.exit_code == 0

    def test_json_output_tiktok_hashtags(self):
        result = self.runner.invoke(cli, ["--json", "tiktok", "hashtags", "--limit", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_json_output_optimize_calendar(self):
        result = self.runner.invoke(cli, ["--json", "optimize", "calendar", "--platform", "tiktok", "--posts-per-week", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_json_output_theme_pages_niches(self):
        result = self.runner.invoke(cli, ["--json", "theme-pages", "--section", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    @patch("cli_anything.social_trends.platforms.youtube.requests.get")
    def test_youtube_trending_command(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = self.runner.invoke(cli, ["youtube", "trending", "--limit", "5"])
        assert result.exit_code == 0

    @patch("cli_anything.social_trends.platforms.youtube.requests.get")
    def test_youtube_hashtags_command(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = "<html></html>"
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        result = self.runner.invoke(cli, ["youtube", "hashtags", "--limit", "10"])
        assert result.exit_code == 0

    @patch("cli_anything.social_trends.core.trend_analyzer.yt.get_trending_videos")
    @patch("cli_anything.social_trends.core.trend_analyzer.yt.get_viral_keywords")
    @patch("cli_anything.social_trends.core.trend_analyzer.tt.get_trending_hashtags")
    def test_analyze_cross_platform_command(self, mock_tt, mock_kw, mock_yt):
        mock_yt.return_value = []
        mock_kw.return_value = []
        mock_tt.return_value = []
        result = self.runner.invoke(cli, ["analyze", "cross-platform", "--limit", "5"])
        assert result.exit_code == 0

    @patch("cli_anything.social_trends.core.trend_analyzer.yt.get_trending_videos")
    @patch("cli_anything.social_trends.core.trend_analyzer.tt.get_niche_hashtags")
    @patch("cli_anything.social_trends.core.trend_analyzer.tt.get_trending_sounds")
    def test_analyze_ideas_command(self, mock_sounds, mock_tags, mock_yt):
        mock_yt.return_value = []
        mock_tags.return_value = []
        mock_sounds.return_value = []
        result = self.runner.invoke(cli, ["analyze", "ideas", "fitness", "--count", "5"])
        assert result.exit_code == 0
