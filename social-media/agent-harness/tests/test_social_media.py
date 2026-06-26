"""Tests for the Social Media CLI harness."""
import json
import pytest
from click.testing import CliRunner
from cli_anything.social_media.social_media_cli import cli
from cli_anything.social_media.scrapers import tiktok as tt
from cli_anything.social_media.scrapers import youtube as yt
from cli_anything.social_media.core import accounts as acct
from cli_anything.social_media.core import hashtags as ht
from cli_anything.social_media.core import theme_pages as theme


runner = CliRunner()


# ── scraper tests ──────────────────────────────────────────────────────────────

class TestTikTokScraper:
    def test_fetch_returns_report(self):
        report = tt.fetch_trends()
        assert report.platform == "tiktok"
        assert len(report.trending_sounds) >= 5
        assert len(report.trending_hashtags) >= 10
        assert len(report.trending_formats) >= 5
        assert len(report.cultural_moments) >= 3

    def test_sounds_have_required_fields(self):
        report = tt.fetch_trends()
        for sound in report.trending_sounds:
            assert "title" in sound
            assert "artist" in sound
            assert "video_count" in sound
            assert "use_case" in sound

    def test_hashtags_have_required_fields(self):
        report = tt.fetch_trends()
        for tag in report.trending_hashtags:
            assert "tag" in tag
            assert tag["tag"].startswith("#")

    def test_world_cup_hashtag_present(self):
        report = tt.fetch_trends()
        tags = [h["tag"] for h in report.trending_hashtags]
        assert any("WorldCup" in t or "worldcup" in t.lower() for t in tags)


class TestYouTubeScraper:
    def test_fetch_returns_report(self):
        report = yt.fetch_trends()
        assert report.platform == "youtube-shorts"
        assert len(report.trending_niches) >= 5
        assert len(report.top_hashtags) >= 10
        assert len(report.format_tips) >= 5

    def test_hashtags_start_with_hash(self):
        report = yt.fetch_trends()
        for tag in report.top_hashtags:
            assert tag["tag"].startswith("#")

    def test_strategy_has_key_fields(self):
        report = yt.fetch_trends()
        s = report.hashtag_strategy
        assert "optimal_count" in s
        assert "formula" in s
        assert "avoid" in s


# ── hashtag engine tests ───────────────────────────────────────────────────────

class TestHashtagEngine:
    def test_generate_tiktok_set(self):
        result = ht.generate_hashtag_set("fitness", "tiktok")
        assert result["platform"] == "tiktok"
        assert 3 <= len(result["hashtags"]) <= 10
        assert all(t.startswith("#") for t in result["hashtags"])

    def test_generate_youtube_always_includes_shorts(self):
        result = ht.generate_hashtag_set("finance", "youtube")
        tags = [t.lower() for t in result["hashtags"]]
        assert "#shorts" in tags

    def test_generate_custom_count(self):
        result = ht.generate_hashtag_set("food", "tiktok", count=3)
        assert len(result["hashtags"]) <= 3

    def test_niche_matching(self):
        for keyword in ["gym", "workout", "health", "exercise"]:
            result = ht.generate_hashtag_set(keyword, "tiktok")
            assert result["niche"] == keyword

    def test_unknown_niche_falls_back_to_general(self):
        result = ht.generate_hashtag_set("astrophysics", "tiktok")
        assert result["hashtags"]  # should not be empty

    def test_formatted_output_is_space_joined(self):
        result = ht.generate_hashtag_set("tech", "instagram")
        assert result["formatted"] == " ".join(result["hashtags"])


# ── account optimizer tests ────────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_tiktok_checklist(self):
        result = acct.get_optimization_checklist("tiktok")
        assert "checklist" in result
        assert "profile" in result["checklist"]
        assert "content" in result["checklist"]
        assert result["total_items"] > 10

    def test_youtube_checklist(self):
        result = acct.get_optimization_checklist("youtube")
        assert "checklist" in result
        assert "shorts" in result["checklist"]

    def test_instagram_checklist(self):
        result = acct.get_optimization_checklist("instagram")
        assert "checklist" in result
        assert "reels" in result["checklist"]

    def test_audit_with_profile(self):
        profile = acct.AccountProfile(
            platform="tiktok",
            handle="test_user",
            follower_count=500,
            bio_set=True,
            profile_pic_set=True,
        )
        result = acct.get_optimization_checklist("tiktok", profile)
        assert "audit" in result
        assert "quick_wins" in result["audit"]
        assert "follower_tier" in result["audit"]

    def test_follower_tier_labels(self):
        assert "nano" in acct._follower_tier(0)
        assert "micro" in acct._follower_tier(5_000)
        assert "mid-tier" in acct._follower_tier(50_000)
        assert "macro" in acct._follower_tier(500_000)
        assert "mega" in acct._follower_tier(2_000_000)

    def test_unknown_platform_returns_error(self):
        result = acct.get_optimization_checklist("myspace")
        assert "error" in result


# ── theme page tests ───────────────────────────────────────────────────────────

class TestThemePages:
    def test_niche_recommendations_returns_list(self):
        niches = theme.get_niche_recommendations()
        assert len(niches) >= 5
        for n in niches:
            assert "niche" in n
            assert "monetization" in n
            assert "content_pillars" in n

    def test_keyword_filter(self):
        niches = theme.get_niche_recommendations(["money", "wealth"])
        assert any("money" in n["niche"].lower() or "wealth" in n["niche"].lower() for n in niches)

    def test_conversion_funnel_has_5_stages(self):
        funnel = theme.get_conversion_funnel()
        stage_keys = [k for k in funnel.keys() if k.startswith("stage_")]
        assert len(stage_keys) == 5

    def test_setup_guide_has_7_steps(self):
        steps = theme.get_setup_guide()
        assert len(steps) == 7
        for step in steps:
            assert "step" in step
            assert "title" in step
            assert "action" in step

    def test_content_calendar_has_all_days(self):
        cal = theme.get_content_calendar()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for day in days:
            assert day in cal["weekly_schedule"]


# ── CLI integration tests ──────────────────────────────────────────────────────

class TestCLI:
    def test_trends_tiktok_sounds(self):
        result = runner.invoke(cli, ["trends", "tiktok", "--section", "sounds"])
        assert result.exit_code == 0
        assert "Trending Sounds" in result.output

    def test_trends_tiktok_json(self):
        result = runner.invoke(cli, ["--json", "trends", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "trending_sounds" in data
        assert "trending_hashtags" in data

    def test_trends_youtube(self):
        result = runner.invoke(cli, ["trends", "youtube", "--section", "niches"])
        assert result.exit_code == 0
        assert "Trending Niches" in result.output

    def test_trends_all(self):
        result = runner.invoke(cli, ["trends", "all"])
        assert result.exit_code == 0
        assert "tiktok" in result.output.lower() or "TikTok" in result.output

    def test_hashtags_command(self):
        result = runner.invoke(cli, ["hashtags", "fitness"])
        assert result.exit_code == 0
        assert "#" in result.output

    def test_hashtags_json(self):
        result = runner.invoke(cli, ["--json", "hashtags", "finance", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "#Shorts" in data["hashtags"] or "#shorts" in [t.lower() for t in data["hashtags"]]

    def test_music_command(self):
        result = runner.invoke(cli, ["music"])
        assert result.exit_code == 0

    def test_accounts_optimize(self):
        result = runner.invoke(cli, ["accounts", "optimize", "tiktok", "--niche", "fitness"])
        assert result.exit_code == 0
        assert "profile" in result.output.lower() or "content" in result.output.lower()

    def test_accounts_audit(self):
        result = runner.invoke(cli, [
            "accounts", "audit", "tiktok",
            "--handle", "testuser",
            "--followers", "2500",
            "--niche", "finance",
        ])
        assert result.exit_code == 0

    def test_themes_niches(self):
        result = runner.invoke(cli, ["themes", "niches"])
        assert result.exit_code == 0
        assert "niche" in result.output.lower() or "Niche" in result.output

    def test_themes_setup(self):
        result = runner.invoke(cli, ["themes", "setup"])
        assert result.exit_code == 0
        assert "Step" in result.output

    def test_themes_funnel(self):
        result = runner.invoke(cli, ["themes", "funnel", "--niche", "finance"])
        assert result.exit_code == 0

    def test_themes_calendar(self):
        result = runner.invoke(cli, ["themes", "calendar"])
        assert result.exit_code == 0
        assert "monday" in result.output.lower()

    def test_optimize_command(self):
        result = runner.invoke(cli, ["optimize", "--platform", "tiktok", "--niche", "fitness", "--followers", "500"])
        assert result.exit_code == 0
        assert "#" in result.output

    def test_optimize_json(self):
        result = runner.invoke(cli, ["--json", "hashtags", "lifestyle", "--platform", "instagram"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert "formatted" in data
