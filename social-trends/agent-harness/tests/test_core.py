"""Unit tests for the social trends CLI — no network calls required."""

import pytest
from cli_anything.social_trends.analyzers.trend_analyzer import (
    virality_score,
    rank_trends,
    extract_all_hashtags,
    find_crossover_trends,
    generate_content_calendar,
)
from cli_anything.social_trends.optimizer.account_optimizer import (
    get_optimization_checklist,
    get_posting_schedule,
    get_bio_template,
    get_hashtag_strategy,
    get_full_optimization_report,
)
from cli_anything.social_trends.theme_page_guide import THEME_PAGE_GUIDE


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_yt_videos():
    return [
        {
            "platform": "youtube",
            "video_id": "abc123",
            "title": "How to Make Money Online #sidehustle #finance",
            "channel": "MoneyChannel",
            "views": "5000000",
            "likes": "250000",
            "comments": "15000",
            "hashtags": ["sidehustle", "finance", "money"],
        },
        {
            "platform": "youtube",
            "video_id": "def456",
            "title": "Viral Dance Challenge #dance #trending",
            "channel": "DanceCrew",
            "views": "12000000",
            "likes": "800000",
            "comments": "45000",
            "hashtags": ["dance", "trending", "challenge"],
        },
    ]


@pytest.fixture
def sample_tt_videos():
    return [
        {
            "platform": "tiktok",
            "id": "tt001",
            "description": "Day in my life #dance #fyp #trending",
            "hashtags": ["dance", "fyp", "trending"],
            "plays": 8000000,
            "likes": 500000,
            "comments": 12000,
            "shares": 50000,
        },
        {
            "platform": "tiktok",
            "id": "tt002",
            "description": "Finance tips that changed my life #finance #money",
            "hashtags": ["finance", "money", "investing"],
            "plays": 3000000,
            "likes": 200000,
            "comments": 8000,
            "shares": 25000,
        },
    ]


# ─── Analyzer Tests ────────────────────────────────────────────────────────────

class TestViralityScore:
    def test_high_view_video_scores_higher(self):
        low = {"views": "100000", "likes": "1000", "comments": "50"}
        high = {"views": "10000000", "likes": "500000", "comments": "20000"}
        assert virality_score(high) > virality_score(low)

    def test_zero_views_returns_zero(self):
        assert virality_score({"views": "0"}) == 0.0

    def test_score_is_0_to_100(self):
        item = {"views": "100000000", "likes": "10000000", "comments": "5000000", "shares": "1000000"}
        score = virality_score(item)
        assert 0 <= score <= 100

    def test_handles_string_k_m_views(self):
        item = {"views": "5M", "likes": "500K"}
        score = virality_score(item)
        assert score > 0

    def test_crossover_boosts_score(self):
        base = {"views": "1000000", "likes": "50000"}
        with_crossover = {**base, "crossover": True}
        assert virality_score(with_crossover) > virality_score(base)


class TestRankTrends:
    def test_returns_sorted_descending(self, sample_yt_videos, sample_tt_videos):
        all_items = sample_yt_videos + sample_tt_videos
        ranked = rank_trends(all_items)
        scores = [item["virality_score"] for item in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_adds_virality_score_field(self, sample_yt_videos):
        ranked = rank_trends(sample_yt_videos)
        for item in ranked:
            assert "virality_score" in item

    def test_empty_list_returns_empty(self):
        assert rank_trends([]) == []


class TestExtractHashtags:
    def test_extracts_from_both_platforms(self, sample_yt_videos, sample_tt_videos):
        tags = extract_all_hashtags(sample_yt_videos, sample_tt_videos)
        tag_names = [t["hashtag"] for t in tags]
        assert "#dance" in tag_names
        assert "#finance" in tag_names

    def test_crossover_flag_set_correctly(self, sample_yt_videos, sample_tt_videos):
        tags = extract_all_hashtags(sample_yt_videos, sample_tt_videos)
        crossover = {t["hashtag"]: t["crossover"] for t in tags}
        # #dance appears in both yt and tt
        assert crossover.get("#dance") is True
        # #challenge only in yt
        assert crossover.get("#challenge") is False

    def test_sorted_by_mentions(self, sample_yt_videos, sample_tt_videos):
        tags = extract_all_hashtags(sample_yt_videos, sample_tt_videos)
        counts = [t["total_mentions"] for t in tags]
        assert counts == sorted(counts, reverse=True)


class TestFindCrossoverTrends:
    def test_finds_shared_hashtags(self, sample_yt_videos, sample_tt_videos):
        crossover = find_crossover_trends(sample_yt_videos, sample_tt_videos)
        crossover_tags = [t["hashtag"] for t in crossover]
        assert "#dance" in crossover_tags
        assert "#trending" in crossover_tags

    def test_no_crossover_returns_empty(self):
        yt = [{"platform": "youtube", "hashtags": ["cats"]}]
        tt = [{"platform": "tiktok", "hashtags": ["dogs"]}]
        assert find_crossover_trends(yt, tt) == []

    def test_all_items_have_crossover_true(self, sample_yt_videos, sample_tt_videos):
        crossover = find_crossover_trends(sample_yt_videos, sample_tt_videos)
        for item in crossover:
            assert item["crossover"] is True
            assert "youtube" in item["platforms"]
            assert "tiktok" in item["platforms"]


class TestContentCalendar:
    def test_returns_correct_day_count(self, sample_yt_videos, sample_tt_videos):
        items = sample_yt_videos + sample_tt_videos
        calendar = generate_content_calendar(items, days=7)
        assert len(calendar) == 7

    def test_each_day_has_posting_windows(self, sample_yt_videos):
        calendar = generate_content_calendar(sample_yt_videos, days=3)
        for day in calendar:
            assert "posting_windows" in day
            assert "tiktok" in day["posting_windows"]
            assert "youtube" in day["posting_windows"]

    def test_days_numbered_correctly(self, sample_yt_videos):
        calendar = generate_content_calendar(sample_yt_videos, days=5)
        for i, day in enumerate(calendar):
            assert day["day_number"] == i + 1


# ─── Optimizer Tests ──────────────────────────────────────────────────────────

class TestOptimizationChecklist:
    @pytest.mark.parametrize("platform", ["tiktok", "youtube", "instagram"])
    def test_returns_checklist_for_all_platforms(self, platform):
        result = get_optimization_checklist(platform)
        assert result["platform"] == platform
        assert "checklist" in result
        assert len(result["checklist"]) > 0

    def test_raises_on_unknown_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            get_optimization_checklist("snapchat")

    def test_tiktok_has_content_tips(self):
        result = get_optimization_checklist("tiktok")
        assert "content" in result["checklist"]
        assert len(result["checklist"]["content"]) > 0


class TestPostingSchedule:
    @pytest.mark.parametrize("platform", ["tiktok", "youtube", "instagram"])
    def test_returns_schedule(self, platform):
        result = get_posting_schedule(platform)
        assert result["platform"] == platform
        assert "schedule" in result

    def test_schedule_has_best_times(self):
        result = get_posting_schedule("tiktok")
        assert "best_times" in result["schedule"]


class TestBioTemplate:
    @pytest.mark.parametrize("platform", ["tiktok", "youtube", "instagram"])
    def test_returns_template(self, platform):
        result = get_bio_template(platform, "fitness")
        assert result["platform"] == platform
        assert "template" in result
        assert len(result["template"]) > 0

    def test_niche_reflected_in_template(self):
        result = get_bio_template("tiktok", "cooking")
        assert "cooking" in result["template"]

    def test_includes_tips(self):
        result = get_bio_template("youtube", "gaming")
        assert "tips" in result
        assert isinstance(result["tips"], list)


class TestHashtagStrategy:
    def test_returns_rules(self):
        result = get_hashtag_strategy("tiktok")
        assert "rules" in result
        assert len(result["rules"]) > 0

    def test_with_trends_includes_trending_now(self):
        trends = [
            {"hashtag": "#fitness", "post_count": 10000},
            {"hashtag": "#workout", "post_count": 5000},
        ]
        result = get_hashtag_strategy("instagram", trends=trends)
        assert "trending_now" in result
        assert "#fitness" in result["trending_now"]

    def test_without_trends_no_trending_now(self):
        result = get_hashtag_strategy("youtube")
        assert "trending_now" not in result


class TestFullOptimizationReport:
    @pytest.mark.parametrize("platform", ["tiktok", "youtube", "instagram"])
    def test_report_has_all_sections(self, platform):
        report = get_full_optimization_report(platform, niche="tech")
        assert "bio_optimization" in report
        assert "posting_schedule" in report
        assert "hashtag_strategy" in report
        assert "checklist" in report
        assert "priority_actions" in report

    def test_priority_actions_are_list(self):
        report = get_full_optimization_report("tiktok")
        assert isinstance(report["priority_actions"], list)
        assert len(report["priority_actions"]) == 5


# ─── Theme Page Guide Tests ───────────────────────────────────────────────────

class TestThemePageGuide:
    def test_guide_has_required_sections(self):
        required = [
            "WHAT IS A THEME PAGE",
            "STEP 1 — CHOOSE YOUR NICHE",
            "STEP 6 — MONETIZATION METHODS",
            "30-DAY LAUNCH CHECKLIST",
            "COMMON MISTAKES TO AVOID",
        ]
        for section in required:
            assert section in THEME_PAGE_GUIDE, f"Missing section: {section}"

    def test_monetization_has_three_tiers(self):
        mono = THEME_PAGE_GUIDE["STEP 6 — MONETIZATION METHODS"]
        assert any("1K to 10K" in k for k in mono.keys())
        assert any("10K to 100K" in k for k in mono.keys())
        assert any("100K+" in k for k in mono.keys())

    def test_30_day_checklist_is_list(self):
        checklist = THEME_PAGE_GUIDE["30-DAY LAUNCH CHECKLIST"]
        assert isinstance(checklist, list)
        assert len(checklist) >= 12

    def test_niche_list_populated(self):
        niche_section = THEME_PAGE_GUIDE["STEP 1 — CHOOSE YOUR NICHE"]
        assert "Best-Performing Niches in 2024-2025" in niche_section
        niches = niche_section["Best-Performing Niches in 2024-2025"]
        assert len(niches) >= 5


# ─── CLI Integration Tests ────────────────────────────────────────────────────

from click.testing import CliRunner
from cli_anything.social_trends.social_trends_cli import main


class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_main_help(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "trends" in result.output
        assert "account" in result.output

    def test_trends_help(self):
        result = self.runner.invoke(main, ["trends", "--help"])
        assert result.exit_code == 0

    def test_account_help(self):
        result = self.runner.invoke(main, ["account", "--help"])
        assert result.exit_code == 0

    def test_account_optimize_json(self):
        result = self.runner.invoke(main, ["--json", "account", "optimize", "--platform", "tiktok"])
        assert result.exit_code == 0
        import json
        # Strip any non-JSON lines (progress messages written to stderr mix in)
        json_start = result.output.find("{")
        assert json_start != -1, "No JSON found in output"
        data = json.loads(result.output[json_start:])
        assert isinstance(data, dict)
        assert "platform" in data

    def test_account_theme_guide_terminal(self):
        result = self.runner.invoke(main, ["account", "theme-guide"])
        assert result.exit_code == 0
        assert "THEME PAGE" in result.output.upper()
        assert "MONETIZATION" in result.output.upper()

    def test_account_theme_guide_markdown(self):
        result = self.runner.invoke(main, ["account", "theme-guide", "--format", "markdown"])
        assert result.exit_code == 0
        assert "# Theme Page" in result.output

    def test_account_theme_guide_json(self):
        result = self.runner.invoke(main, ["account", "theme-guide", "--format", "json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "guide" in data

    def test_config_show(self):
        result = self.runner.invoke(main, ["config", "show"])
        assert result.exit_code == 0
        assert "YOUTUBE_API_KEY" in result.output

    def test_config_set_key_creates_env(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = self.runner.invoke(main, ["config", "set-key", "--platform", "youtube", "--key", "test_key_123"])
        assert result.exit_code == 0
        env_file = tmp_path / ".env"
        assert env_file.exists()
        content = env_file.read_text()
        assert "YOUTUBE_API_KEY=test_key_123" in content
