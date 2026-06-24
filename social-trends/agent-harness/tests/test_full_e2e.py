"""End-to-end tests for cli-anything-social-trends.

Tests verify the full CLI command chain including Click command wiring,
JSON output mode, and all command groups. No live network calls are made —
we mock the backend at the HTTP layer.
"""

import pytest
import json
import sys
import os
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_trends.social_trends_cli import cli


# ── Fixtures ──────────────────────────────────────────────────────────────────

MOCK_YT_VIDEOS_RESPONSE = {
    "items": [
        {
            "id": f"vid{i:03d}",
            "snippet": {
                "title": f"Trending Video {i}",
                "channelTitle": f"Channel {i}",
                "channelId": f"UC{i:05d}",
                "publishedAt": "2025-06-01T12:00:00Z",
                "description": f"A trending video #{['fitness', 'music', 'gaming'][i % 3]}",
                "tags": [["fitness", "workout"], ["music", "viral"], ["gaming", "esports"]][i % 3],
                "categoryId": "10",
                "thumbnails": {"high": {"url": f"https://img.youtube.com/vi/vid{i:03d}/hqdefault.jpg"}},
            },
            "statistics": {
                "viewCount": str(100000 * (i + 1)),
                "likeCount": str(5000 * (i + 1)),
                "commentCount": str(200 * (i + 1)),
            },
            "contentDetails": {"duration": f"PT{5 + i}M30S"},
        }
        for i in range(10)
    ]
}

MOCK_YT_CHANNEL_RESPONSE = {
    "items": [{
        "snippet": {
            "title": "Test Channel",
            "description": "A test channel about fitness and wellness.",
            "country": "US",
            "publishedAt": "2020-01-01T00:00:00Z",
        },
        "statistics": {
            "subscriberCount": "50000",
            "viewCount": "5000000",
            "videoCount": "250",
        },
        "brandingSettings": {"channel": {"keywords": "fitness wellness workout"}},
    }]
}

MOCK_TT_VIDEOS = [
    {
        "id": f"tt{i:04d}",
        "desc": f"Check this out #{['fitness', 'dance', 'comedy'][i % 3]} #viral",
        "createTime": 1700000000 + i * 3600,
        "author": {
            "nickname": f"creator_{i}",
            "id": f"uid{i}",
            "uniqueId": f"creator_{i}",
        },
        "stats": {
            "playCount": 500000 * (i + 1),
            "diggCount": 25000 * (i + 1),
            "commentCount": 1000 * (i + 1),
            "shareCount": 500 * (i + 1),
        },
        "music": {
            "id": f"m{i:03d}",
            "title": f"Hit Song {i}",
            "authorName": f"Artist {i}",
        },
        "video": {"duration": 15 + i * 5},
    }
    for i in range(10)
]


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_yt_api():
    # Patch where yt_get is used (the importing module), not where it's defined
    with patch("cli_anything.social_trends.core.youtube.yt_get") as mock:
        mock.return_value = MOCK_YT_VIDEOS_RESPONSE
        yield mock


@pytest.fixture
def mock_tt_scrape():
    with patch("cli_anything.social_trends.core.tiktok.tt_scrape_trending_hashtags") as mock:
        mock.return_value = MOCK_TT_VIDEOS
        yield mock


@pytest.fixture
def mock_tt_music_scrape():
    with patch("cli_anything.social_trends.core.tiktok.tt_scrape_trending_music") as mock:
        mock.return_value = [
            {
                "id": f"music{i}",
                "title": f"Trending Track {i}",
                "authorName": f"Artist {i}",
                "userCount": 10000 * (i + 1),
                "duration": 30,
            }
            for i in range(5)
        ]
        yield mock


@pytest.fixture
def mock_yt_key_configured():
    with patch("cli_anything.social_trends.core.youtube.yt_get") as mock_yt:
        mock_yt.return_value = MOCK_YT_VIDEOS_RESPONSE
        yield mock_yt, mock_yt


@pytest.fixture
def mock_tt_not_configured():
    with patch("cli_anything.social_trends.core.tiktok.check_tiktok_configured") as m:
        m.return_value = False
        yield m


@pytest.fixture
def mock_cache_disabled():
    # Patch cached in both core modules (imported references)
    with patch("cli_anything.social_trends.core.youtube.cached") as myt:
        myt.side_effect = lambda key, fn, ttl=None: fn()
        with patch("cli_anything.social_trends.core.tiktok.cached") as mtt:
            mtt.side_effect = lambda key, fn, ttl=None: fn()
            yield myt, mtt


# ── Auth commands ─────────────────────────────────────────────────────────────

class TestAuthCommands:
    def test_auth_youtube_saves_key(self, runner, tmp_path):
        with patch("cli_anything.social_trends.utils.trends_backend.CONFIG_DIR", tmp_path):
            with patch("cli_anything.social_trends.utils.trends_backend.save_youtube_key") as mock_save:
                result = runner.invoke(cli, ["auth", "youtube", "--api-key", "AIzatest123"])
                assert result.exit_code == 0
                mock_save.assert_called_once_with("AIzatest123")

    def test_auth_tiktok_saves_creds(self, runner):
        with patch("cli_anything.social_trends.utils.trends_backend.save_tiktok_creds") as mock_save:
            result = runner.invoke(cli, [
                "auth", "tiktok",
                "--client-key", "tt_client_key",
                "--client-secret", "tt_client_secret",
            ])
            assert result.exit_code == 0
            mock_save.assert_called_once_with("tt_client_key", "tt_client_secret")

    def test_auth_status(self, runner):
        with patch("cli_anything.social_trends.utils.trends_backend.check_youtube_configured", return_value=True):
            with patch("cli_anything.social_trends.utils.trends_backend.check_tiktok_configured", return_value=False):
                result = runner.invoke(cli, ["auth", "status"])
                assert result.exit_code == 0
                assert "youtube" in result.output.lower()
                assert "tiktok" in result.output.lower()

    def test_auth_status_json(self, runner):
        with patch("cli_anything.social_trends.utils.trends_backend.check_youtube_configured", return_value=True):
            with patch("cli_anything.social_trends.utils.trends_backend.check_tiktok_configured", return_value=False):
                result = runner.invoke(cli, ["--json", "auth", "status"])
                assert result.exit_code == 0
                data = json.loads(result.output)
                assert data["youtube"]["configured"] is True
                assert data["tiktok"]["configured"] is False

    def test_auth_clear_cache(self, runner):
        with patch("cli_anything.social_trends.utils.trends_backend.clear_cache") as mock_clear:
            mock_clear.return_value = {"status": "cache cleared"}
            result = runner.invoke(cli, ["auth", "clear-cache"])
            assert result.exit_code == 0
            mock_clear.assert_called_once()


# ── YouTube commands ──────────────────────────────────────────────────────────

class TestYouTubeCommands:
    def test_trending_default(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["youtube", "trending"])
        assert result.exit_code == 0
        assert "Trending" in result.output or "youtube" in result.output.lower()

    def test_trending_json_output(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["--json", "youtube", "trending", "--region", "US"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"
        assert "videos" in data
        assert len(data["videos"]) > 0

    def test_trending_with_category(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["--json", "youtube", "trending", "--category", "music"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["category"] == "music"

    def test_trending_region_kwarg(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["--json", "youtube", "trending", "--region", "KR"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["region"] == "KR"

    def test_music_command(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["--json", "youtube", "music"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "youtube"

    def test_hashtags_command(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["--json", "youtube", "hashtags"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data

    def test_channel_command(self, runner, mock_cache_disabled):
        with patch("cli_anything.social_trends.core.youtube.yt_get") as mock_yt:
            mock_yt.return_value = MOCK_YT_CHANNEL_RESPONSE
            result = runner.invoke(cli, ["--json", "youtube", "channel", "UCtest12345"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert data["platform"] == "youtube"
            assert "subscribers" in data

    def test_channel_not_found(self, runner, mock_cache_disabled):
        with patch("cli_anything.social_trends.core.youtube.yt_get") as mock_yt:
            mock_yt.return_value = {"items": []}
            result = runner.invoke(cli, ["youtube", "channel", "UCnotexist"])
            assert result.exit_code == 1

    def test_search_command(self, runner):
        search_result = {
            "items": [
                {
                    "id": {"videoId": "sv001"},
                    "snippet": {
                        "title": "Search Result",
                        "channelTitle": "Test",
                        "publishedAt": "2025-01-01T00:00:00Z",
                    },
                }
            ]
        }
        with patch("cli_anything.social_trends.core.youtube.yt_get") as mock_yt:
            mock_yt.return_value = search_result
            result = runner.invoke(cli, ["--json", "youtube", "search", "#fitness"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert "videos" in data
            assert data["query"] == "#fitness"

    def test_categories_command(self, runner):
        with patch("cli_anything.social_trends.core.youtube.yt_get") as mock_yt:
            mock_yt.return_value = {
                "items": [
                    {"id": "10", "snippet": {"title": "Music", "assignable": True}},
                    {"id": "20", "snippet": {"title": "Gaming", "assignable": True}},
                ]
            }
            result = runner.invoke(cli, ["--json", "youtube", "categories"])
            assert result.exit_code == 0
            data = json.loads(result.output)
            assert "categories" in data
            assert len(data["categories"]) == 2


# ── TikTok commands ───────────────────────────────────────────────────────────

class TestTikTokCommands:
    def test_trending_with_scrape(self, runner, mock_tt_scrape, mock_cache_disabled, mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "tiktok", "trending"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["platform"] == "tiktok"
        assert "videos" in data
        assert data["source"] == "public_scrape"

    def test_trending_region(self, runner, mock_tt_scrape, mock_cache_disabled, mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "tiktok", "trending", "--region", "GB"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["region"] == "GB"

    def test_hashtags_command(self, runner, mock_tt_scrape, mock_cache_disabled, mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "tiktok", "hashtags"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "hashtags" in data
        assert data["platform"] == "tiktok"

    def test_music_command_scrape(self, runner, mock_tt_music_scrape, mock_cache_disabled, mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "tiktok", "music"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "music" in data
        assert data["source"] == "public_scrape"

    def test_search_hashtag_requires_api(self, runner, mock_tt_not_configured):
        result = runner.invoke(cli, ["tiktok", "search-hashtag", "fitness"])
        assert result.exit_code == 1
        assert "Research API" in result.output or "Error" in result.output


# ── Cross-platform trends ─────────────────────────────────────────────────────

class TestTrendsCommands:
    def test_trends_all_json(self, runner, mock_yt_api, mock_tt_scrape, mock_cache_disabled,
                              mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "trends", "all", "--region", "US"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_viral" in data
        assert "youtube_count" in data
        assert "tiktok_count" in data

    def test_trends_all_niche_filter(self, runner, mock_yt_api, mock_tt_scrape, mock_cache_disabled,
                                      mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "trends", "all", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "fitness"

    def test_trends_score_from_file(self, runner, tmp_path):
        video_file = tmp_path / "videos.json"
        videos = [
            {"views": 100000, "likes": 5000, "comments": 200, "shares": 100, "platform": "tiktok"},
            {"views": 50000, "likes": 1000, "comments": 50, "shares": 10, "platform": "youtube"},
        ]
        video_file.write_text(json.dumps(videos))
        result = runner.invoke(cli, ["--json", "trends", "score", str(video_file)])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "videos" in data
        assert data["videos"][0]["viral_score"] >= data["videos"][1]["viral_score"]


# ── Hashtag commands ──────────────────────────────────────────────────────────

class TestHashtagCommands:
    def test_merge_hashtags(self, runner, mock_yt_api, mock_tt_scrape, mock_cache_disabled,
                             mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "hashtags", "merge", "--niche", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_recommendations" in data
        assert "suggested_caption_hashtags" in data

    def test_analyze_hashtags(self, runner, mock_yt_api, mock_tt_scrape, mock_cache_disabled,
                               mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "hashtags", "analyze", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "top_recommendations" in data
        assert "suggested_set" in data


# ── Music commands ────────────────────────────────────────────────────────────

class TestMusicCommands:
    def test_music_all_platforms(self, runner, mock_yt_api, mock_tt_music_scrape, mock_cache_disabled,
                                  mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "music", "trending"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tiktok" in data
        assert "youtube" in data

    def test_music_tiktok_only(self, runner, mock_tt_music_scrape, mock_cache_disabled, mock_tt_not_configured):
        result = runner.invoke(cli, ["--json", "music", "trending", "--platform", "tiktok"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "tiktok" in data
        assert "youtube" not in data

    def test_music_youtube_only(self, runner, mock_yt_api, mock_cache_disabled):
        result = runner.invoke(cli, ["--json", "music", "trending", "--platform", "youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "youtube" in data
        assert "tiktok" not in data


# ── Optimize commands ─────────────────────────────────────────────────────────

class TestOptimizeCommands:
    def test_report_no_trends(self, runner):
        result = runner.invoke(cli, [
            "--json", "optimize", "report",
            "--platforms", "tiktok,youtube",
            "--niche", "fitness",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "account_summary" in data
        assert "posting_schedule" in data
        assert "quick_wins" in data

    def test_report_with_trends(self, runner, mock_cache_disabled, mock_tt_not_configured):
        with patch("cli_anything.social_trends.core.youtube.yt_get") as mock_yt:
            mock_yt.return_value = MOCK_YT_VIDEOS_RESPONSE
            with patch("cli_anything.social_trends.core.tiktok.tt_scrape_trending_hashtags") as mock_tt:
                mock_tt.return_value = MOCK_TT_VIDEOS
                result = runner.invoke(cli, [
                    "--json", "optimize", "report",
                    "--platforms", "tiktok",
                    "--niche", "fitness",
                    "--pull-trends",
                ])
                assert result.exit_code == 0
                data = json.loads(result.output)
                assert "hashtag_report" in data

    def test_report_tier_options(self, runner):
        for tier in ["micro", "mid", "macro", "mega"]:
            result = runner.invoke(cli, [
                "--json", "optimize", "report",
                "--niche", "gaming",
                "--tier", tier,
            ])
            assert result.exit_code == 0

    def test_schedule_command(self, runner):
        result = runner.invoke(cli, ["--json", "optimize", "schedule", "--platforms", "tiktok,youtube"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "posting_schedule" in data

    def test_schedule_timezone(self, runner):
        result = runner.invoke(cli, [
            "--json", "optimize", "schedule",
            "--platforms", "tiktok",
            "--tz-offset", "-5",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        sched = data["posting_schedule"]["tiktok"]
        assert "best_hours_local" in sched

    def test_strategy_command(self, runner):
        result = runner.invoke(cli, [
            "--json", "optimize", "strategy",
            "--platforms", "tiktok",
            "--niche", "fitness",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "platform_strategies" in data


# ── Theme page commands ───────────────────────────────────────────────────────

class TestThemeCommands:
    def test_guide_command(self, runner):
        result = runner.invoke(cli, [
            "--json", "theme", "guide",
            "--niche", "fitness",
            "--platform", "tiktok",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "guide_title" in data
        assert "niche_evaluation" in data
        assert "page_setup_checklist" in data

    def test_niches_command(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "available_niches" in data
        assert data["total"] > 0

    def test_evaluate_command_known(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "evaluate", "fitness"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["found"] is True

    def test_evaluate_command_unknown(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "evaluate", "basket_weaving_championship"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["found"] is False

    def test_monetize_command(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "monetize", "--strategy", "shoutouts"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "pricing_guide" in data
        assert "tips" in data

    def test_list_strategies_command(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "list-strategies"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert "strategies" in data
        assert len(data["strategies"]) > 0

    def test_calendar_7_day(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "calendar", "--template", "7_day_theme_page"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "calendar" in data
        assert "day_1" in data["calendar"]

    def test_calendar_30_day(self, runner):
        result = runner.invoke(cli, ["--json", "theme", "calendar", "--template", "30_day_growth_sprint"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "week_1" in data["calendar"]

    def test_setup_command_tiktok(self, runner):
        result = runner.invoke(cli, [
            "--json", "theme", "setup",
            "--platform", "tiktok",
            "--niche", "fitness",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "universal_checklist" in data
        assert "platform_checklist" in data
        assert len(data["platform_checklist"]) > 0

    def test_setup_command_youtube(self, runner):
        result = runner.invoke(cli, [
            "--json", "theme", "setup",
            "--platform", "youtube",
            "--niche", "tech",
        ])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "monetization_unlock_milestones" in data

    def test_guide_all_monetization_strategies(self, runner):
        strategies = ["shoutouts", "affiliate_marketing", "digital_products",
                      "page_flipping", "brand_deals"]
        for strategy in strategies:
            result = runner.invoke(cli, [
                "--json", "theme", "guide",
                "--niche", "luxury",
                "--platform", "instagram",
                "--monetize", strategy,
            ])
            assert result.exit_code == 0, f"Failed for strategy: {strategy}"


# ── JSON output mode consistency ──────────────────────────────────────────────

class TestJsonOutputMode:
    """Verify --json flag always produces valid parseable JSON."""

    def test_all_theme_json_valid(self, runner):
        commands = [
            ["--json", "theme", "niches"],
            ["--json", "theme", "evaluate", "fitness"],
            ["--json", "theme", "list-strategies"],
            ["--json", "theme", "calendar", "--template", "7_day_theme_page"],
            ["--json", "theme", "monetize", "--strategy", "affiliate_marketing"],
        ]
        for cmd in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Failed: {cmd} — {result.output}"
            try:
                json.loads(result.output)
            except json.JSONDecodeError:
                pytest.fail(f"Non-JSON output for {cmd}: {result.output[:200]}")

    def test_optimize_json_valid(self, runner):
        commands = [
            ["--json", "optimize", "report", "--niche", "fitness"],
            ["--json", "optimize", "schedule", "--platforms", "tiktok"],
            ["--json", "optimize", "strategy", "--niche", "gaming", "--platforms", "youtube"],
        ]
        for cmd in commands:
            result = runner.invoke(cli, cmd)
            assert result.exit_code == 0, f"Failed: {cmd}"
            json.loads(result.output)
