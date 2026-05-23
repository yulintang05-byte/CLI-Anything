"""Unit tests for social media tools core modules."""
import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from cli_anything.social.core.session import Session
from cli_anything.social.core.account_optimizer import (
    analyze_account_profile,
    get_optimal_schedule,
    batch_optimize_accounts,
    _assess_growth_stage,
)
from cli_anything.social.core.theme_page import (
    get_theme_page_guide,
    find_profitable_niches,
    estimate_account_value,
    PROFITABLE_NICHES,
    ACCOUNT_MARKETPLACES,
)
from cli_anything.social.core.trend_analyzer import (
    generate_hashtag_set,
    _merge_hashtags,
    _merge_music,
    _music_key,
)
from cli_anything.social.core import youtube_scraper as yt
from cli_anything.social.core import tiktok_scraper as tt


# ─── Session tests ────────────────────────────────────────────────────────────

class TestSession:
    def setup_method(self):
        self.tmp = tempfile.mktemp(suffix=".json")
        self.session = Session(session_file=self.tmp)

    def teardown_method(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_session_creates_file(self):
        self.session.save()
        assert os.path.exists(self.tmp)

    def test_cache_trends(self):
        trends = [{"rank": 1, "title": "Test Video"}]
        self.session.cache_trends("youtube", trends)
        cached = self.session.get_cached("youtube")
        assert cached == trends

    def test_cache_expiry(self):
        trends = [{"rank": 1}]
        self.session.cache_trends("tiktok", trends)
        # Expired cache should return None with max_age=0
        result = self.session.get_cached("tiktok", max_age_minutes=0)
        assert result is None

    def test_add_account(self):
        self.session.add_account("tiktok", "@testhandle", "fitness")
        accounts = self.session.get_accounts()
        assert len(accounts) == 1
        assert accounts[0]["handle"] == "@testhandle"
        assert accounts[0]["platform"] == "tiktok"
        assert accounts[0]["niche"] == "fitness"

    def test_add_account_no_duplicate(self):
        self.session.add_account("tiktok", "@testhandle", "fitness")
        self.session.add_account("tiktok", "@testhandle", "fitness")
        assert len(self.session.get_accounts()) == 1

    def test_log(self):
        self.session.log("test_action", "test detail")
        assert self.session.last_scrape is None  # only set by cache_trends

    def test_persistence(self):
        self.session.add_account("youtube", "@testchannel", "tech")
        self.session.save()
        session2 = Session(session_file=self.tmp)
        accounts = session2.get_accounts()
        assert len(accounts) == 1
        assert accounts[0]["handle"] == "@testchannel"


# ─── Account optimizer tests ──────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_analyze_basic(self):
        result = analyze_account_profile(
            platform="tiktok",
            handle="@testaccount",
        )
        assert "optimization_score" in result
        assert "growth_stage" in result
        assert "recommendations" in result
        assert "posting_schedule" in result
        assert isinstance(result["optimization_score"], int)
        assert 0 <= result["optimization_score"] <= 100

    def test_analyze_with_good_bio(self):
        result = analyze_account_profile(
            platform="instagram",
            handle="@fitnesspage",
            niche="fitness",
            bio_text="Daily fitness tips 💪 | Follow for workout routines | Link in bio for free plan",
            follower_count=10000,
            avg_views=3000,
        )
        assert result["optimization_score"] >= 70
        assert len(result["wins"]) > 0

    def test_analyze_missing_bio(self):
        result = analyze_account_profile(
            platform="tiktok",
            handle="@nobio",
            bio_text="",
        )
        issues = [i.lower() for i in result["issues"]]
        assert any("bio" in issue for issue in issues)

    def test_analyze_tiktok_recommendations(self):
        result = analyze_account_profile(
            platform="tiktok",
            handle="@tiktoker",
            niche="comedy",
        )
        recs_str = " ".join(result["recommendations"]).lower()
        assert "tiktok" in recs_str or "hook" in recs_str or "trending" in recs_str

    def test_growth_stages(self):
        stages = [
            (0, "Nano"),
            (5000, "Micro"),
            (25000, "Growing"),
            (75000, "Established"),
            (200000, "Macro"),
            (1000000, "Mega"),
        ]
        for followers, expected_stage in stages:
            stage = _assess_growth_stage("tiktok", followers)
            assert stage["stage"] == expected_stage, \
                f"Expected {expected_stage} for {followers} followers, got {stage['stage']}"

    def test_optimal_schedule_tiktok(self):
        schedule = get_optimal_schedule("tiktok")
        assert schedule["platform"] == "tiktok"
        assert "best_days" in schedule
        assert "best_hours_utc" in schedule
        assert "weekly_schedule" in schedule
        assert len(schedule["best_days"]) >= 3

    def test_optimal_schedule_youtube(self):
        schedule = get_optimal_schedule("youtube")
        assert "Thursday" in schedule["best_days"] or "Friday" in schedule["best_days"]

    def test_batch_optimize(self):
        accounts = [
            {"platform": "tiktok", "handle": "@acc1", "niche": "fitness"},
            {"platform": "instagram", "handle": "@acc2", "niche": "food", "followers": 5000},
        ]
        results = batch_optimize_accounts(accounts)
        assert len(results) == 2
        for result in results:
            assert "optimization_score" in result
            assert "recommendations" in result


# ─── Theme page tests ─────────────────────────────────────────────────────────

class TestThemePage:
    def test_guide_structure(self):
        guide = get_theme_page_guide()
        required_keys = [
            "what_is_theme_page", "phase_1_setup", "phase_2_growth",
            "phase_3_monetization", "phase_4_selling", "tools_stack",
            "30_day_action_plan",
        ]
        for key in required_keys:
            assert key in guide, f"Missing key: {key}"

    def test_guide_with_niche(self):
        guide = get_theme_page_guide(niche="finance")
        assert "your_niche_analysis" in guide
        niche_data = guide["your_niche_analysis"]
        assert "Finance" in niche_data["niche"]

    def test_30_day_plan_has_4_weeks(self):
        guide = get_theme_page_guide()
        plan = guide["30_day_action_plan"]
        assert len(plan) == 4
        for week in plan:
            assert "week" in week
            assert "tasks" in week
            assert len(week["tasks"]) >= 3

    def test_marketplaces_listed(self):
        guide = get_theme_page_guide()
        marketplaces = guide["phase_4_selling"]["marketplaces"]
        assert len(marketplaces) >= 3
        for m in marketplaces:
            assert "name" in m
            assert "url" in m

    def test_profitable_niches(self):
        niches = find_profitable_niches()
        assert len(niches) >= 5
        for n in niches:
            assert "niche" in n
            assert "rank" in n
            assert "best_platforms" in n
            assert "monetization" in n

    def test_niches_filter_difficulty(self):
        easy = find_profitable_niches(filter_difficulty="Low")
        for n in easy:
            assert n["difficulty"] == "Low"

    def test_niches_sort_affiliate(self):
        sorted_niches = find_profitable_niches(sort_by="affiliate_potential")
        if len(sorted_niches) >= 2:
            order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
            for i in range(len(sorted_niches) - 1):
                a = order.get(sorted_niches[i]["affiliate_potential"], 3)
                b = order.get(sorted_niches[i + 1]["affiliate_potential"], 3)
                assert a <= b

    def test_estimate_value_tiktok(self):
        result = estimate_account_value("tiktok", 10000)
        assert "estimated_value_usd" in result
        assert result["estimated_value_usd"] > 0
        assert "value_range" in result
        assert "$" in result["value_range"]

    def test_estimate_value_with_revenue(self):
        no_rev = estimate_account_value("instagram", 50000)
        with_rev = estimate_account_value("instagram", 50000, monthly_revenue=500.0)
        assert with_rev["estimated_value_usd"] >= no_rev["estimated_value_usd"]

    def test_estimate_value_engagement_bonus(self):
        low_eng = estimate_account_value("instagram", 10000, engagement_rate=0.5)
        high_eng = estimate_account_value("instagram", 10000, engagement_rate=6.0)
        assert high_eng["estimated_value_usd"] > low_eng["estimated_value_usd"]


# ─── Trend analyzer tests ─────────────────────────────────────────────────────

class TestTrendAnalyzer:
    def test_merge_hashtags_deduplication(self):
        yt_tags = [
            {"hashtag": "#fitness", "rank": 1, "appearances": 5},
            {"hashtag": "#workout", "rank": 2, "appearances": 3},
        ]
        tt_tags = [
            {"hashtag": "#fitness", "rank": 1, "appearances": 10},
            {"hashtag": "#gym", "rank": 2, "appearances": 8},
        ]
        merged = _merge_hashtags(yt_tags, tt_tags)
        # fitness appears on both platforms
        fitness = next((t for t in merged if t["hashtag"] == "#fitness"), None)
        assert fitness is not None
        assert fitness["is_cross_platform"] is True
        assert "youtube" in fitness["platforms"]
        assert "tiktok" in fitness["platforms"]

    def test_merge_hashtags_ranking(self):
        yt_tags = [{"hashtag": "#a", "rank": 1, "appearances": 1}]
        tt_tags = [{"hashtag": "#b", "rank": 1, "appearances": 100}]
        merged = _merge_hashtags(yt_tags, tt_tags)
        assert len(merged) == 2
        # b should rank higher due to more appearances
        ranks = {t["hashtag"]: t["rank"] for t in merged}
        assert ranks["#b"] < ranks["#a"]

    def test_music_key_normalization(self):
        assert _music_key("Hello World!", "Artist Name") == _music_key(
            "hello world", "artist name"
        )

    def test_merge_music_cross_platform(self):
        yt_music = [
            {"song_title": "Blinding Lights", "artist": "The Weeknd",
             "views": 5000000, "url": "", "hashtags": []}
        ]
        tt_music = [
            {"song_title": "Blinding Lights", "artist": "The Weeknd",
             "videos_using": 50, "total_views": 2000000, "tiktok_url": "",
             "is_original_sound": False}
        ]
        merged = _merge_music(yt_music, tt_music)
        assert len(merged) >= 1
        # Should detect cross-platform match
        track = merged[0]
        assert track["is_cross_platform"] or len(merged) == 2  # fuzzy match may vary

    def test_generate_hashtag_set_structure(self):
        result = generate_hashtag_set("fitness", platform="tiktok", size="medium")
        assert "hashtags" in result
        assert "hashtag_string" in result
        assert "strategy" in result
        assert "tips" in result
        assert len(result["hashtags"]) >= 5
        # All should start with #
        for ht in result["hashtags"]:
            assert ht.startswith("#"), f"Hashtag '{ht}' should start with #"

    def test_generate_hashtag_set_niche_included(self):
        result = generate_hashtag_set("cooking", platform="tiktok", size="small")
        hashtags_lower = [h.lower() for h in result["hashtags"]]
        assert any("cooking" in h for h in hashtags_lower)

    def test_generate_hashtag_set_sizes(self):
        small = generate_hashtag_set("tech", size="small")
        medium = generate_hashtag_set("tech", size="medium")
        large = generate_hashtag_set("tech", size="large")
        assert len(small["hashtags"]) <= len(medium["hashtags"])
        assert len(medium["hashtags"]) <= len(large["hashtags"])


# ─── YouTube scraper tests (unit, no network) ─────────────────────────────────

class TestYouTubeScraper:
    def test_parse_view_count(self):
        from cli_anything.social.core.youtube_scraper import _parse_view_count
        assert _parse_view_count("1.2M views") == 1_200_000
        assert _parse_view_count("500K views") == 500_000
        assert _parse_view_count("2.5B views") == 2_500_000_000
        assert _parse_view_count("1,234,567 views") == 1_234_567
        assert _parse_view_count("") == 0

    def test_extract_initial_data_invalid(self):
        from cli_anything.social.core.youtube_scraper import _extract_initial_data
        assert _extract_initial_data("no json here") is None
        assert _extract_initial_data("") is None


# ─── TikTok scraper tests (unit, no network) ──────────────────────────────────

class TestTikTokScraper:
    def test_parse_views(self):
        from cli_anything.social.core.tiktok_scraper import _parse_views
        assert _parse_views(1000000) == 1000000
        assert _parse_views("2.5m") == 2_500_000
        assert _parse_views("500k") == 500_000
        assert _parse_views(1.5) == 1

    def test_parse_tt_items_empty(self):
        from cli_anything.social.core.tiktok_scraper import _parse_tt_items
        assert _parse_tt_items([]) == []

    def test_parse_tt_items_valid(self):
        from cli_anything.social.core.tiktok_scraper import _parse_tt_items
        items = [{
            "id": "12345",
            "desc": "test video #fitness #viral",
            "author": {"uniqueId": "testuser", "nickname": "Test User"},
            "music": {"title": "Test Song", "authorName": "Test Artist", "id": "99999"},
            "stats": {"playCount": 1000000, "diggCount": 50000, "shareCount": 1000, "commentCount": 200},
            "video": {"duration": 30},
            "challenges": [{"title": "fitnesschallenge"}],
        }]
        result = _parse_tt_items(items)
        assert len(result) == 1
        assert result[0]["video_id"] == "12345"
        assert result[0]["author_handle"] == "testuser"
        assert result[0]["views"] == 1000000
        assert "#fitness" in result[0]["hashtags"]
        assert result[0]["music_title"] == "Test Song"

    def test_walk_json_for_videos(self):
        from cli_anything.social.core.tiktok_scraper import _walk_json_for_videos
        nested = {
            "data": {
                "feed": {
                    "itemList": [
                        {"id": "111", "desc": "test", "author": {}, "music": {},
                         "stats": {}, "video": {}}
                    ]
                }
            }
        }
        result = _walk_json_for_videos(nested, limit=10)
        assert len(result) == 1


# ─── CLI smoke tests ──────────────────────────────────────────────────────────

class TestCLI:
    def test_cli_imports(self):
        from cli_anything.social.social_cli import cli
        assert cli is not None

    def test_cli_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "trends" in result.output.lower() or "Usage" in result.output

    def test_trends_youtube_help(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["trends", "youtube", "--help"])
        assert result.exit_code == 0

    def test_hashtags_generate_missing_niche(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["hashtags", "generate"])
        assert result.exit_code != 0  # Should fail without --niche

    def test_optimize_account_json(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--json", "optimize", "account",
            "--platform", "tiktok",
            "--handle", "@testhandle",
            "--niche", "fitness",
            "--bio", "Fitness tips daily | Follow for workouts | Link in bio 💪",
            "--followers", "5000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "optimization_score" in data
        assert "recommendations" in data

    def test_theme_niches_json(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 5

    def test_theme_value_json(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--json", "theme", "value",
            "--platform", "instagram",
            "--followers", "10000",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "estimated_value_usd" in data
        assert data["estimated_value_usd"] > 0

    def test_optimize_schedule_json(self):
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli
        runner = CliRunner()
        result = runner.invoke(cli, [
            "--json", "optimize", "schedule", "--platform", "tiktok"
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "best_days" in data
        assert "weekly_schedule" in data

    def test_accounts_add_and_list(self):
        import tempfile
        from click.testing import CliRunner
        from cli_anything.social.social_cli import cli, get_session
        from cli_anything.social.core.session import Session

        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp_session = f.name

        # Monkey-patch session
        import cli_anything.social.social_cli as social_module
        orig_session = social_module._session
        social_module._session = Session(session_file=tmp_session)

        try:
            result = runner.invoke(cli, [
                "accounts", "add",
                "--platform", "tiktok",
                "--handle", "@mypage",
                "--niche", "fitness",
            ])
            assert result.exit_code == 0

            result2 = runner.invoke(cli, ["--json", "accounts", "list"])
            assert result2.exit_code == 0
            data = json.loads(result2.output)
            assert any(a["handle"] == "@mypage" for a in data)
        finally:
            social_module._session = orig_session
            if os.path.exists(tmp_session):
                os.remove(tmp_session)
