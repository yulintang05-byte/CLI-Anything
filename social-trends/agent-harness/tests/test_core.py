"""Core unit tests for social-trends — no network calls required."""
import json
import pytest
from click.testing import CliRunner

from cli_anything.social_trends.cli import main
from cli_anything.social_trends.analyzers.trends import (
    analyze_hashtags,
    analyze_trending_music,
    analyze_topics,
    generate_full_report,
)
from cli_anything.social_trends.optimizers.account import generate_account_optimization
from cli_anything.social_trends.theme_pages.guide import generate_theme_page_guide, _rank_niches


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_youtube_data():
    return {
        "region": "US",
        "category": "0",
        "videos": [
            {
                "id": "abc123",
                "url": "https://www.youtube.com/watch?v=abc123",
                "title": "Best AI tools for 2025 #ai #tech tutorial",
                "channel": "TechReview",
                "description": "Learn the best AI tools. #technology #ai #tutorial",
                "published": "2025-05-10",
                "tags": ["ai", "technology", "tutorial", "best tools"],
                "views": "1500000",
                "likes": "45000",
                "duration": "PT10M30S",
            },
            {
                "id": "def456",
                "url": "https://www.youtube.com/watch?v=def456",
                "title": "How to make money online in 2025 #finance #money",
                "channel": "FinanceHub",
                "description": "Top money-making strategies. #personalfinance #investing",
                "published": "2025-05-09",
                "tags": ["finance", "money", "investing", "income"],
                "views": "800000",
                "likes": "22000",
                "duration": "PT15M00S",
            },
        ],
        "total": 2,
        "source": "test",
    }


@pytest.fixture()
def sample_tiktok_data():
    return {
        "region": "US",
        "videos": [
            {
                "id": "tt001",
                "url": "https://www.tiktok.com/@creator/video/tt001",
                "author": "@creator",
                "description": "Best AI hack #ai #tech #fyp",
                "hashtags": ["#ai", "#tech", "#fyp"],
                "music": {"id": "music001", "title": "Trending Beat", "author": "DJ Viral", "is_original": False},
                "stats": {"plays": 2000000, "likes": 150000, "comments": 5000, "shares": 25000},
                "duration": 30,
            },
            {
                "id": "tt002",
                "url": "https://www.tiktok.com/@creator2/video/tt002",
                "author": "@creator2",
                "description": "Finance tip that changed my life #finance #money #fyp",
                "hashtags": ["#finance", "#money", "#fyp"],
                "music": {"id": "music002", "title": "Lo-fi Chill", "author": "ChillBeat", "is_original": False},
                "stats": {"plays": 1200000, "likes": 80000, "comments": 3500, "shares": 15000},
                "duration": 45,
            },
        ],
        "hashtags": [
            {"tag": "#fyp", "video_count": 1000000, "view_count": 500000000000, "rank": 1},
            {"tag": "#ai", "video_count": 500000, "view_count": 10000000000, "rank": 2},
            {"tag": "#finance", "video_count": 300000, "view_count": 5000000000, "rank": 3},
        ],
        "sounds": [
            {"id": "music001", "title": "Trending Beat", "author": "DJ Viral", "use_count": 500000, "is_original": False},
            {"id": "music002", "title": "Lo-fi Chill", "author": "ChillBeat", "use_count": 300000, "is_original": False},
        ],
        "total_videos": 2,
        "total_hashtags": 3,
        "total_sounds": 2,
        "source": "test",
    }


# ---------------------------------------------------------------------------
# Analyzer tests
# ---------------------------------------------------------------------------

def test_analyze_hashtags_youtube_only(sample_youtube_data):
    result = analyze_hashtags(youtube_data=sample_youtube_data)
    assert "top_hashtags" in result
    assert isinstance(result["top_hashtags"], list)


def test_analyze_hashtags_tiktok_only(sample_tiktok_data):
    result = analyze_hashtags(tiktok_data=sample_tiktok_data)
    top_tags = [h["tag"] for h in result["top_hashtags"]]
    assert "#fyp" in top_tags


def test_analyze_hashtags_cross_platform(sample_youtube_data, sample_tiktok_data):
    result = analyze_hashtags(sample_youtube_data, sample_tiktok_data)
    cross = result["cross_platform"]
    # #ai and #finance appear in both platforms
    cross_tags = [h["tag"] for h in cross]
    assert any("ai" in t or "finance" in t or "tech" in t for t in cross_tags)


def test_analyze_trending_music(sample_tiktok_data):
    result = analyze_trending_music(sample_tiktok_data)
    assert "sounds" in result
    assert len(result["sounds"]) >= 1
    assert "insights" in result
    assert len(result["insights"]) >= 1


def test_analyze_topics(sample_youtube_data, sample_tiktok_data):
    result = analyze_topics(sample_youtube_data, sample_tiktok_data)
    assert "top_keywords" in result
    assert "content_angles" in result
    assert result["total_videos_analyzed"] == 4


def test_generate_full_report(sample_youtube_data, sample_tiktok_data):
    result = generate_full_report(sample_youtube_data, sample_tiktok_data)
    assert "summary" in result
    assert "hashtags" in result
    assert "music" in result
    assert "topics" in result
    assert "action_items" in result
    assert isinstance(result["action_items"], list)
    assert len(result["action_items"]) >= 3


# ---------------------------------------------------------------------------
# Optimizer tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("followers,expected_phase", [
    (0, "0–1k"),
    (500, "0–1k"),
    (1000, "1k–10k"),
    (5000, "1k–10k"),
    (10000, "10k–100k"),
    (50000, "10k–100k"),
    (100000, "100k+"),
    (1000000, "100k+"),
])
def test_growth_phase_determination(followers, expected_phase):
    result = generate_account_optimization(follower_count=followers)
    assert result["growth_phase"]["range"] == expected_phase


def test_optimize_all_platforms():
    result = generate_account_optimization(platform="all", niche="fitness", follower_count=5000)
    assert "platform_specs" in result
    assert "tiktok" in result["platform_specs"]
    assert "youtube" in result["platform_specs"]
    assert "instagram" in result["platform_specs"]


def test_optimize_single_platform():
    result = generate_account_optimization(platform="tiktok", niche="finance", follower_count=1000)
    assert "tiktok" in result["platform_specs"]
    assert len(result["content_calendar"]) == 7


def test_optimize_with_trend_data(sample_tiktok_data, sample_youtube_data):
    trend_data = generate_full_report(sample_youtube_data, sample_tiktok_data)
    result = generate_account_optimization(
        platform="tiktok",
        niche="tech",
        follower_count=2500,
        trend_data=trend_data,
    )
    assert len(result["trend_specific_tips"]) >= 1


def test_monetization_roadmap_milestones():
    result = generate_account_optimization(follower_count=15000)
    roadmap = result["monetization_roadmap"]
    assert len(roadmap) == 5
    completed = [m for m in roadmap if m["status"] == "completed"]
    assert len(completed) == 2  # 1k and 10k milestones completed


# ---------------------------------------------------------------------------
# Theme page tests
# ---------------------------------------------------------------------------

def test_niche_ranking_is_sorted():
    ranking = _rank_niches()
    scores = [n["profit_score"] for n in ranking]
    assert scores == sorted(scores, reverse=True)


def test_theme_guide_all_fields():
    result = generate_theme_page_guide(niche="finance", current_followers=0)
    assert "theme_page_sop" in result
    assert "monetization_paths" in result
    assert "repurposing_tools" in result
    assert "legal_notes" in result
    assert "conversion_checklist" in result
    assert "top_10_niches_by_profit" in result
    assert len(result["top_10_niches_by_profit"]) == 10


def test_theme_guide_niche_matching():
    result = generate_theme_page_guide(niche="gym fitness workout")
    assert result["niche_data"].get("label", "").lower().find("fitness") >= 0 or result["niche_data"] != {}


def test_theme_guide_phases():
    sop = generate_theme_page_guide()["theme_page_sop"]
    assert "phase_1_setup" in sop
    assert "phase_2_content" in sop
    assert "phase_3_grow" in sop
    assert "phase_4_monetize" in sop


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "scrape" in result.output
    assert "analyze" in result.output
    assert "optimize" in result.output
    assert "report" in result.output
    assert "theme" in result.output


def test_cli_optimize(tmp_path):
    runner = CliRunner()
    out = str(tmp_path / "plan.json")
    result = runner.invoke(main, [
        "optimize",
        "--platform", "tiktok",
        "--niche", "fitness",
        "--followers", "5000",
        "--output", out,
    ])
    assert result.exit_code == 0, result.output
    data = json.loads(tmp_path.joinpath("plan.json").read_text())
    assert data["niche"] == "fitness"
    assert "tiktok" in data["platform_specs"]


def test_cli_theme_list_niches():
    runner = CliRunner()
    result = runner.invoke(main, ["theme", "--list-niches"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "top_niches_by_profit" in data
    assert len(data["top_niches_by_profit"]) == 10


def test_cli_analyze_hashtags_no_input():
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "hashtags"])
    assert result.exit_code != 0


def test_cli_analyze_hashtags_from_file(tmp_path, sample_youtube_data, sample_tiktok_data):
    yt_file = tmp_path / "yt.json"
    tt_file = tmp_path / "tt.json"
    yt_file.write_text(json.dumps(sample_youtube_data))
    tt_file.write_text(json.dumps(sample_tiktok_data))

    runner = CliRunner()
    result = runner.invoke(main, [
        "analyze", "hashtags",
        "--youtube-data", str(yt_file),
        "--tiktok-data", str(tt_file),
    ])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "top_hashtags" in data
