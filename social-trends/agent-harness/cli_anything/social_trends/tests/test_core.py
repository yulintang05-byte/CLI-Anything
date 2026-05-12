"""Unit tests for social-trends core, trends, optimizer, and theme_pages modules."""

import json
import os
import tempfile
import time

import pytest

from cli_anything.social_trends.core import (
    TrendSession,
    default_session_path,
    session_exists,
)
from cli_anything.social_trends.trends import (
    merge_hashtags,
    merge_trends,
    generate_hashtag_sets,
    score_content_idea,
    analyze_niche_opportunity,
    _hashtag_recommendation,
    _suggest_content_angles,
    _optimal_posting_times,
)
from cli_anything.social_trends.optimizer import (
    generate_optimization_report,
    build_content_calendar,
    _content_pillars,
    _posting_frequency_rec,
    _engagement_hooks,
    _growth_tactics,
)
from cli_anything.social_trends.theme_pages import (
    list_niches,
    get_niche,
    score_niche,
    get_theme_page_guide,
    NICHES,
)


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def tmp_path_str(tmp_path):
    return str(tmp_path / "test_session.trends.json")


@pytest.fixture
def sample_session(tmp_path_str):
    sess = TrendSession(name="test", region="US", niche="fitness")
    sess.save(tmp_path_str)
    return sess, tmp_path_str


@pytest.fixture
def sample_youtube_trends():
    return [
        {"id": "yt1", "title": "Best Workout 2025", "views": 5_000_000, "likes": 400_000,
         "comments": 10_000, "hashtags": ["fitness", "gym", "workout"], "score": 850.0},
        {"id": "yt2", "title": "Morning Routine Tips", "views": 2_000_000, "likes": 180_000,
         "comments": 5_000, "hashtags": ["morning", "routine", "productivity"], "score": 720.0},
        {"id": "yt3", "title": "Viral Food Recipe", "views": 8_000_000, "likes": 700_000,
         "comments": 25_000, "hashtags": ["food", "recipe", "viral"], "score": 960.0},
    ]


@pytest.fixture
def sample_tiktok_trends():
    return [
        {"id": "tt1", "views": 4_200_000, "likes": 380_000, "comments": 12_000,
         "hashtags": ["fyp", "viral", "fitness"], "score": 920.0},
        {"id": "tt2", "views": 3_100_000, "likes": 290_000, "comments": 8_500,
         "hashtags": ["luxury", "lifestyle", "fyp"], "score": 880.0},
    ]


@pytest.fixture
def sample_hashtags():
    return [
        {"tag": "fitness", "score": 900.0, "frequency": 15, "avg_views": 3_000_000,
         "avg_likes": 250_000, "platforms": ["youtube", "tiktok"], "recommendation": "Top priority"},
        {"tag": "fyp", "score": 850.0, "frequency": 12, "avg_views": 4_000_000,
         "avg_likes": 300_000, "platforms": ["tiktok"], "recommendation": "High value"},
        {"tag": "viral", "score": 800.0, "frequency": 10, "avg_views": 2_500_000,
         "avg_likes": 200_000, "platforms": ["youtube", "tiktok"], "recommendation": "High value"},
        {"tag": "gym", "score": 750.0, "frequency": 8, "avg_views": 1_800_000,
         "avg_likes": 150_000, "platforms": ["youtube"], "recommendation": "Consistent performer"},
        {"tag": "workout", "score": 700.0, "frequency": 7, "avg_views": 1_500_000,
         "avg_likes": 120_000, "platforms": ["youtube", "tiktok"], "recommendation": "Consistent performer"},
    ]


@pytest.fixture
def sample_sounds():
    return [
        {"music_id": "s1", "title": "Trending Song 1", "frequency": 45, "avg_views": 3_200_000, "score": 980},
        {"music_id": "s2", "title": "Trending Song 2", "frequency": 38, "avg_views": 2_800_000, "score": 940},
    ]


@pytest.fixture
def sample_accounts():
    return [
        {"platform": "tiktok", "handle": "@fitnessdaily", "niche": "fitness"},
        {"platform": "instagram", "handle": "@luxuryvibes", "niche": "luxury_lifestyle"},
    ]


# ── TrendSession tests ─────────────────────────────────────────────────

class TestTrendSession:
    def test_create_session(self):
        sess = TrendSession(name="test_session", region="US", niche="fitness")
        assert sess.name == "test_session"
        assert sess.region == "US"
        assert sess.niche == "fitness"
        assert sess.youtube_trends == []
        assert sess.tiktok_trends == []
        assert sess.hashtags == []
        assert sess.sounds == []
        assert sess.accounts == []

    def test_save_and_load(self, tmp_path_str):
        sess = TrendSession(name="save_test", region="GB", niche="food")
        sess.save(tmp_path_str)

        assert session_exists(tmp_path_str)
        loaded = TrendSession.load(tmp_path_str)
        assert loaded.name == "save_test"
        assert loaded.region == "GB"
        assert loaded.niche == "food"

    def test_save_creates_json(self, tmp_path_str):
        sess = TrendSession(name="json_test")
        sess.save(tmp_path_str)
        with open(tmp_path_str) as f:
            data = json.load(f)
        assert data["name"] == "json_test"
        assert "created_at" in data

    def test_set_youtube_trends(self, sample_session, sample_youtube_trends):
        sess, path = sample_session
        sess.set_youtube_trends(sample_youtube_trends)
        assert len(sess.youtube_trends) == 3
        assert sess.modified is True

    def test_set_tiktok_trends(self, sample_session, sample_tiktok_trends):
        sess, path = sample_session
        sess.set_tiktok_trends(sample_tiktok_trends)
        assert len(sess.tiktok_trends) == 2
        assert sess.modified is True

    def test_add_account(self, sample_session):
        sess, path = sample_session
        acct = sess.add_account("tiktok", "@testuser", "fitness")
        assert acct["platform"] == "tiktok"
        assert acct["handle"] == "@testuser"
        assert acct["niche"] == "fitness"
        assert len(sess.accounts) == 1
        assert sess.modified is True

    def test_remove_account(self, sample_session):
        sess, path = sample_session
        sess.add_account("tiktok", "@removeuser", "fitness")
        assert len(sess.accounts) == 1
        removed = sess.remove_account("@removeuser")
        assert removed is True
        assert len(sess.accounts) == 0

    def test_remove_nonexistent_account(self, sample_session):
        sess, path = sample_session
        removed = sess.remove_account("@doesnotexist")
        assert removed is False

    def test_top_hashtags(self, sample_session, sample_hashtags):
        sess, path = sample_session
        sess.set_hashtags(sample_hashtags)
        top = sess.top_hashtags(n=3)
        assert len(top) == 3
        assert top[0]["score"] >= top[1]["score"]

    def test_top_sounds(self, sample_session, sample_sounds):
        sess, path = sample_session
        sess.set_sounds(sample_sounds)
        top = sess.top_sounds(n=2)
        assert len(top) == 2
        # sorted by score descending
        assert top[0].get("score", 0) >= top[1].get("score", 0)

    def test_all_trends_combined(self, sample_session, sample_youtube_trends, sample_tiktok_trends):
        sess, path = sample_session
        sess.set_youtube_trends(sample_youtube_trends)
        sess.set_tiktok_trends(sample_tiktok_trends)
        combined = sess.all_trends()
        assert len(combined) == 5
        # All should have a platform key
        for t in combined:
            assert "platform" in t

    def test_summary(self, sample_session, sample_youtube_trends, sample_hashtags):
        sess, path = sample_session
        sess.set_youtube_trends(sample_youtube_trends)
        sess.set_hashtags(sample_hashtags)
        summary = sess.summary
        assert summary["youtube_trends"] == 3
        assert summary["hashtags"] == 5
        assert summary["region"] == "US"
        assert summary["niche"] == "fitness"

    def test_modified_cleared_on_save(self, tmp_path_str):
        sess = TrendSession(name="save_mod_test")
        sess.set_youtube_trends([{"title": "test", "score": 1.0}])
        assert sess.modified is True
        sess.save(tmp_path_str)
        assert sess.modified is False

    def test_default_session_path(self):
        path = default_session_path("mysession")
        assert path.endswith(".trends.json")
        assert "mysession" in path

    def test_session_exists_false(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        assert not session_exists(path)

    def test_roundtrip_with_data(self, tmp_path_str, sample_youtube_trends, sample_hashtags):
        sess = TrendSession(name="roundtrip", region="UK", niche="food")
        sess.set_youtube_trends(sample_youtube_trends)
        sess.set_hashtags(sample_hashtags)
        sess.add_account("instagram", "@testpage", "food")
        sess.save(tmp_path_str)

        loaded = TrendSession.load(tmp_path_str)
        assert loaded.name == "roundtrip"
        assert len(loaded.youtube_trends) == 3
        assert len(loaded.hashtags) == 5
        assert len(loaded.accounts) == 1


# ── Trends engine tests ────────────────────────────────────────────────

class TestTrendsEngine:
    def test_merge_hashtags_dedup(self):
        yt = [{"tag": "fitness", "score": 500, "frequency": 5, "avg_views": 1_000_000, "avg_likes": 80_000}]
        tt = [{"tag": "fitness", "score": 400, "frequency": 4, "avg_views": 800_000, "avg_likes": 60_000}]
        merged = merge_hashtags(yt, tt)
        assert any(h["tag"] == "fitness" for h in merged)
        fitness = next(h for h in merged if h["tag"] == "fitness")
        # Should have cross-platform boost (both in platforms list)
        assert len(fitness["platforms"]) == 2 or fitness["score"] > 900

    def test_merge_hashtags_cross_platform_boost(self):
        yt = [{"tag": "viral", "score": 300, "frequency": 3, "avg_views": 500_000, "avg_likes": 40_000}]
        tt = [{"tag": "viral", "score": 250, "frequency": 2, "avg_views": 400_000, "avg_likes": 30_000}]
        merged = merge_hashtags(yt, tt)
        viral = next((h for h in merged if h["tag"] == "viral"), None)
        assert viral is not None
        # Cross-platform score = (300+250)*1.5 = 825
        assert viral["score"] > 500

    def test_merge_hashtags_sorting(self):
        yt = [
            {"tag": "a", "score": 100, "frequency": 1, "avg_views": 10_000, "avg_likes": 1_000},
            {"tag": "b", "score": 500, "frequency": 5, "avg_views": 500_000, "avg_likes": 40_000},
        ]
        merged = merge_hashtags(yt, [])
        assert merged[0]["score"] >= merged[1]["score"]

    def test_merge_trends_combines_platforms(self, sample_youtube_trends, sample_tiktok_trends):
        merged = merge_trends(sample_youtube_trends, sample_tiktok_trends)
        assert len(merged) == 5
        platforms = {t["platform"] for t in merged}
        assert "youtube" in platforms
        assert "tiktok" in platforms

    def test_merge_trends_sorted_by_score(self, sample_youtube_trends, sample_tiktok_trends):
        merged = merge_trends(sample_youtube_trends, sample_tiktok_trends)
        scores = [t["score"] for t in merged]
        assert scores == sorted(scores, reverse=True)

    def test_generate_hashtag_sets_structure(self, sample_hashtags):
        sets = generate_hashtag_sets(sample_hashtags, niche="fitness")
        assert "viral" in sets
        assert "niche" in sets
        assert "balanced" in sets
        for key, tags in sets.items():
            assert isinstance(tags, list)
            assert len(tags) > 0

    def test_generate_hashtag_sets_always_include_base(self, sample_hashtags):
        sets = generate_hashtag_sets(sample_hashtags, niche="")
        for key, tags in sets.items():
            # base tags should be present
            assert any(t in ["fyp", "viral", "trending"] for t in tags)

    def test_generate_hashtag_sets_max_size(self, sample_hashtags):
        sets = generate_hashtag_sets(sample_hashtags, niche="fitness")
        for key, tags in sets.items():
            assert len(tags) <= 15

    def test_score_content_idea_high_relevance(self, sample_hashtags, sample_sounds):
        result = score_content_idea(
            title="Fitness workout routine",
            hashtags=["fitness", "gym", "fyp"],
            trending_hashtags=sample_hashtags,
            trending_sounds=sample_sounds,
        )
        assert result["relevance_score"] >= 0
        assert result["relevance_score"] <= 100
        assert "matched_hashtags" in result
        assert "verdict" in result
        assert len(result["matched_hashtags"]) >= 2

    def test_score_content_idea_low_relevance(self, sample_hashtags, sample_sounds):
        result = score_content_idea(
            title="Completely unrelated quantum physics video",
            hashtags=["science", "physics"],
            trending_hashtags=sample_hashtags,
            trending_sounds=sample_sounds,
        )
        assert result["relevance_score"] < 50

    def test_score_content_idea_empty_inputs(self):
        result = score_content_idea("test", [], [], [])
        assert result["relevance_score"] == 0.0
        assert result["matched_hashtags"] == []

    def test_analyze_niche_opportunity(self, sample_hashtags, sample_youtube_trends, sample_tiktok_trends):
        combined = merge_trends(sample_youtube_trends, sample_tiktok_trends)
        result = analyze_niche_opportunity("fitness", sample_hashtags, combined)
        assert "opportunity_score" in result
        assert 0 <= result["opportunity_score"] <= 100
        assert "content_angles" in result
        assert isinstance(result["content_angles"], list)
        assert "recommended_posting_times" in result

    def test_hashtag_recommendation_viral(self):
        rec = _hashtag_recommendation("fitness", 2_000_000, 10, ["youtube", "tiktok"])
        assert "viral" in rec.lower() or "priority" in rec.lower()

    def test_hashtag_recommendation_high_value(self):
        rec = _hashtag_recommendation("gym", 600_000, 5, ["youtube"])
        assert "high" in rec.lower() or "value" in rec.lower()

    def test_suggest_content_angles_known_niche(self):
        angles = _suggest_content_angles("fitness workout")
        assert len(angles) >= 3
        assert isinstance(angles[0], str)

    def test_suggest_content_angles_unknown_niche(self):
        angles = _suggest_content_angles("quantum_computing_xyz")
        assert len(angles) >= 3  # generic fallback

    def test_optimal_posting_times_known_niche(self):
        times = _optimal_posting_times("fitness")
        assert len(times) == 3
        for t in times:
            assert ":" in t  # time format check

    def test_optimal_posting_times_default(self):
        times = _optimal_posting_times("unknown_niche_xyz")
        assert len(times) == 3


# ── Optimizer tests ────────────────────────────────────────────────────

class TestOptimizer:
    def test_generate_optimization_report_structure(
        self, sample_accounts, sample_hashtags, sample_sounds,
        sample_youtube_trends, sample_tiktok_trends
    ):
        combined = merge_trends(sample_youtube_trends, sample_tiktok_trends)
        report = generate_optimization_report(
            accounts=sample_accounts,
            hashtags=sample_hashtags,
            sounds=sample_sounds,
            trends=combined,
            niche="fitness",
            region="US",
        )

        assert "generated_at" in report
        assert "global_strategy" in report
        assert "accounts" in report
        assert "content_calendar" in report
        assert "growth_tactics" in report
        assert len(report["accounts"]) == 2

    def test_optimization_report_account_fields(
        self, sample_accounts, sample_hashtags, sample_sounds,
        sample_youtube_trends, sample_tiktok_trends
    ):
        combined = merge_trends(sample_youtube_trends, sample_tiktok_trends)
        report = generate_optimization_report(
            accounts=sample_accounts,
            hashtags=sample_hashtags,
            sounds=sample_sounds,
            trends=combined,
        )
        for acct in report["accounts"]:
            assert "handle" in acct
            assert "platform" in acct
            assert "bio_template" in acct
            assert "recommended_hashtags" in acct
            assert "optimal_posting_times" in acct
            assert "content_angles" in acct
            assert "platform_tips" in acct
            assert "monetization_paths" in acct

    def test_optimization_report_empty_accounts(self, sample_hashtags, sample_sounds):
        report = generate_optimization_report(
            accounts=[],
            hashtags=sample_hashtags,
            sounds=sample_sounds,
            trends=[],
        )
        assert report["accounts"] == []
        assert "global_strategy" in report

    def test_build_content_calendar_7_days(self, sample_hashtags, sample_youtube_trends):
        calendar = build_content_calendar(
            trends=sample_youtube_trends,
            hashtags=sample_hashtags,
            niche="fitness",
            days=7,
        )
        assert len(calendar) == 7

    def test_build_content_calendar_structure(self, sample_hashtags, sample_youtube_trends):
        calendar = build_content_calendar(
            trends=sample_youtube_trends,
            hashtags=sample_hashtags,
            days=3,
        )
        for day in calendar:
            assert "day" in day
            assert "theme" in day
            assert "content_idea" in day
            assert "hashtags" in day
            assert "best_posting_time" in day
            assert "platforms" in day

    def test_build_content_calendar_no_trends(self, sample_hashtags):
        calendar = build_content_calendar(trends=[], hashtags=sample_hashtags, days=3)
        assert len(calendar) == 3
        for day in calendar:
            assert day["inspired_by"] == ""

    def test_content_pillars_fitness(self):
        pillars = _content_pillars("fitness")
        assert len(pillars) >= 4
        assert any("workout" in p.lower() or "fitness" in p.lower() for p in pillars)

    def test_content_pillars_generic(self):
        pillars = _content_pillars("totally_unknown_niche")
        assert len(pillars) >= 4

    def test_posting_frequency_rec(self):
        freq = _posting_frequency_rec("fitness")
        assert "tiktok" in freq
        assert "instagram_reels" in freq
        assert "youtube" in freq

    def test_engagement_hooks_count(self):
        hooks = _engagement_hooks()
        assert len(hooks) >= 5
        for hook in hooks:
            assert isinstance(hook, str)
            assert len(hook) > 10

    def test_growth_tactics_structure(self):
        tactics = _growth_tactics("fitness")
        assert len(tactics) >= 5
        for tactic in tactics:
            assert "tactic" in tactic
            assert "description" in tactic
            assert "effort" in tactic
            assert "impact" in tactic


# ── Theme page tests ───────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches_returns_all(self):
        niches = list_niches()
        assert len(niches) >= 8

    def test_list_niches_has_required_keys(self):
        niches = list_niches()
        for n in niches:
            assert "key" in n
            assert "name" in n
            assert "avg_cpm" in n
            assert "competition" in n
            assert "monetization_ease" in n

    def test_list_niches_sorted_by_cpm(self):
        niches = list_niches(sort_by="avg_cpm")
        cpms = [n["avg_cpm"] for n in niches]
        assert cpms == sorted(cpms, reverse=True)

    def test_list_niches_sorted_by_competition(self):
        niches = list_niches(sort_by="competition")
        assert niches[0]["competition"] in ("low", "very low")

    def test_get_niche_valid(self):
        niche = get_niche("fitness_wellness")
        assert niche is not None
        assert niche["name"] == "Fitness & Wellness"
        assert "hashtags" in niche
        assert "content_sources" in niche

    def test_get_niche_invalid(self):
        niche = get_niche("nonexistent_niche_xyz")
        assert niche is None

    def test_score_niche_valid(self):
        result = score_niche("finance_investing")
        assert "total_score" in result
        assert 0 < result["total_score"] <= 100
        assert "monetization_score" in result
        assert "cpm_score" in result
        assert "competition_score" in result
        assert "recommendation" in result

    def test_score_niche_invalid(self):
        result = score_niche("nonexistent_niche")
        assert "error" in result

    def test_score_niche_finance_is_high(self):
        # Finance has highest CPM ($12) and high monetization
        result = score_niche("finance_investing")
        assert result["total_score"] >= 60

    def test_score_niche_gaming_lower_cpm(self):
        # Gaming has lower CPM ($2.50)
        finance = score_niche("finance_investing")
        gaming = score_niche("gaming_clips")
        assert finance["cpm_score"] > gaming["cpm_score"]

    def test_get_theme_page_guide_structure(self):
        guide = get_theme_page_guide("fitness_wellness")
        assert "title" in guide
        assert "overview" in guide
        assert "account_setup" in guide
        assert "content_strategy" in guide
        assert "content_sourcing" in guide
        assert "growth_playbook" in guide
        assert "monetization_roadmap" in guide
        assert "milestones" in guide
        assert "common_mistakes" in guide
        assert "tools" in guide

    def test_get_theme_page_guide_general(self):
        guide = get_theme_page_guide("")
        assert guide["title"].startswith("Theme Page Creation Guide")

    def test_guide_account_setup_steps(self):
        guide = get_theme_page_guide("luxury_lifestyle")
        steps = guide["account_setup"]["steps"]
        assert len(steps) >= 4

    def test_guide_monetization_roadmap_milestones(self):
        guide = get_theme_page_guide("finance_investing")
        roadmap = guide["monetization_roadmap"]
        assert len(roadmap) >= 3
        milestones = [m["milestone"] for m in roadmap]
        # Should progress from smaller to larger audience
        assert any("1,000" in m or "100" in m for m in milestones)
        assert any("100,000" in m or "50,000" in m for m in milestones)

    def test_guide_common_mistakes_count(self):
        guide = get_theme_page_guide("food_recipes")
        assert len(guide["common_mistakes"]) >= 8

    def test_guide_growth_playbook_phases(self):
        guide = get_theme_page_guide("motivation_quotes")
        phases = guide["growth_playbook"]
        assert len(phases) >= 3
        for phase in phases:
            assert "phase" in phase
            assert "strategy" in phase
            assert "timeframe" in phase

    def test_all_niches_have_content_sources(self):
        for key in NICHES:
            niche = NICHES[key]
            assert "content_sources" in niche
            assert len(niche["content_sources"]) >= 2

    def test_all_niches_have_hashtags(self):
        for key in NICHES:
            niche = NICHES[key]
            assert "hashtags" in niche
            assert len(niche["hashtags"]) >= 4

    def test_tools_section_has_categories(self):
        guide = get_theme_page_guide("fitness_wellness")
        tools = guide["tools"]
        assert "content_creation" in tools
        assert "scheduling_analytics" in tools
        assert "content_discovery" in tools
        assert "monetization" in tools


# ── CLI integration tests ──────────────────────────────────────────────

class TestCLIIntegration:
    """Test CLI commands via Click test runner (no actual API calls)."""

    def setup_method(self):
        from click.testing import CliRunner
        from cli_anything.social_trends.cli import cli
        self.runner = CliRunner()
        self.cli = cli

    def _invoke(self, args: list, project: str = "") -> object:
        if project:
            return self.runner.invoke(self.cli, ["--project", project] + args)
        return self.runner.invoke(self.cli, args)

    def test_version(self):
        result = self._invoke(["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_session_new(self, tmp_path):
        path = str(tmp_path / "new_session.trends.json")
        result = self._invoke(["session", "new", "mytest", "--output", path])
        assert result.exit_code == 0
        assert "Created session" in result.output or "mytest" in result.output

    def test_session_new_json(self, tmp_path):
        path = str(tmp_path / "json_session.trends.json")
        result = self._invoke(["--json", "session", "new", "jsontest", "--output", path])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "jsontest"
        assert "path" in data

    def test_session_new_duplicate_fails(self, tmp_path):
        path = str(tmp_path / "dup_session.trends.json")
        self._invoke(["session", "new", "duptest", "--output", path])
        result = self._invoke(["session", "new", "duptest", "--output", path])
        assert result.exit_code != 0 or "already exists" in result.output.lower()

    def test_account_add(self, tmp_path):
        path = str(tmp_path / "acct_session.trends.json")
        self._invoke(["session", "new", "accttest", "--output", path])
        result = self._invoke(["--project", path, "account", "add", "tiktok", "@mypage"])
        assert result.exit_code == 0
        assert "@mypage" in result.output or "Added" in result.output

    def test_account_add_json(self, tmp_path):
        path = str(tmp_path / "acct_json.trends.json")
        self._invoke(["session", "new", "acctjson", "--output", path])
        result = self._invoke(["--project", path, "--json", "account", "add", "instagram", "@instapage"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["handle"] == "@instapage"
        assert data["platform"] == "instagram"

    def test_account_list_empty(self, tmp_path):
        path = str(tmp_path / "list_empty.trends.json")
        self._invoke(["session", "new", "listempty", "--output", path])
        result = self._invoke(["--project", path, "account", "list"])
        assert result.exit_code == 0

    def test_account_add_and_list(self, tmp_path):
        path = str(tmp_path / "addlist.trends.json")
        self._invoke(["session", "new", "addlisttest", "--output", path])
        self._invoke(["--project", path, "account", "add", "tiktok", "@user1"])
        self._invoke(["--project", path, "account", "add", "youtube", "@user2"])
        result = self._invoke(["--project", path, "account", "list"])
        assert result.exit_code == 0
        assert "@user1" in result.output
        assert "@user2" in result.output

    def test_trends_fetch_mock(self, tmp_path):
        path = str(tmp_path / "mock_trends.trends.json")
        self._invoke(["session", "new", "mocktest", "--output", path])
        result = self._invoke(["--project", path, "trends", "fetch", "--mock"])
        assert result.exit_code == 0
        assert "trend" in result.output.lower() or "Mock" in result.output

    def test_trends_fetch_mock_json(self, tmp_path):
        path = str(tmp_path / "mock_json.trends.json")
        self._invoke(["session", "new", "mockjson", "--output", path])
        result = self._invoke(["--project", path, "--json", "trends", "fetch", "--mock"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_trends_list_empty(self, tmp_path):
        path = str(tmp_path / "trends_empty.trends.json")
        self._invoke(["session", "new", "trendsempty", "--output", path])
        result = self._invoke(["--project", path, "trends", "list"])
        assert result.exit_code == 0

    def test_hashtags_recommend_after_fetch(self, tmp_path):
        path = str(tmp_path / "ht_session.trends.json")
        self._invoke(["session", "new", "httest", "--output", path])
        self._invoke(["--project", path, "trends", "fetch", "--mock"])
        result = self._invoke(["--project", path, "hashtags", "recommend"])
        assert result.exit_code == 0
        assert "#" in result.output or "hashtag" in result.output.lower()

    def test_hashtags_sets_after_recommend(self, tmp_path):
        path = str(tmp_path / "sets_session.trends.json")
        self._invoke(["session", "new", "setstest", "--output", path])
        self._invoke(["--project", path, "trends", "fetch", "--mock"])
        self._invoke(["--project", path, "hashtags", "recommend"])
        result = self._invoke(["--project", path, "hashtags", "sets"])
        assert result.exit_code == 0
        assert "VIRAL" in result.output or "viral" in result.output.lower()

    def test_music_trending_mock(self, tmp_path):
        path = str(tmp_path / "music_session.trends.json")
        self._invoke(["session", "new", "musictest", "--output", path])
        result = self._invoke(["--project", path, "music", "trending", "--mock"])
        assert result.exit_code == 0

    def test_music_trending_mock_json(self, tmp_path):
        path = str(tmp_path / "music_json.trends.json")
        self._invoke(["session", "new", "musicjson", "--output", path])
        result = self._invoke(["--project", path, "--json", "music", "trending", "--mock"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)

    def test_optimize_run_requires_accounts(self, tmp_path):
        path = str(tmp_path / "opt_no_accts.trends.json")
        self._invoke(["session", "new", "optempty", "--output", path])
        result = self._invoke(["--project", path, "optimize", "run"])
        assert result.exit_code != 0 or "No accounts" in result.output

    def test_optimize_run_with_accounts(self, tmp_path):
        path = str(tmp_path / "opt_full.trends.json")
        self._invoke(["session", "new", "optfull", "--output", path])
        self._invoke(["--project", path, "trends", "fetch", "--mock"])
        self._invoke(["--project", path, "hashtags", "recommend"])
        self._invoke(["--project", path, "music", "trending", "--mock"])
        self._invoke(["--project", path, "account", "add", "tiktok", "@testpage"])
        result = self._invoke(["--project", path, "optimize", "run"])
        assert result.exit_code == 0

    def test_optimize_calendar(self, tmp_path):
        path = str(tmp_path / "cal_session.trends.json")
        self._invoke(["session", "new", "caltest", "--output", path])
        self._invoke(["--project", path, "trends", "fetch", "--mock"])
        result = self._invoke(["--project", path, "optimize", "calendar"])
        assert result.exit_code == 0
        assert "Monday" in result.output or "calendar" in result.output.lower()

    def test_optimize_score_idea(self, tmp_path):
        path = str(tmp_path / "score_session.trends.json")
        self._invoke(["session", "new", "scoretest", "--output", path])
        self._invoke(["--project", path, "trends", "fetch", "--mock"])
        self._invoke(["--project", path, "hashtags", "recommend"])
        self._invoke(["--project", path, "music", "trending", "--mock"])
        result = self._invoke([
            "--project", path,
            "optimize", "score-idea",
            "My viral fitness content",
            "--hashtags", "fitness", "--hashtags", "fyp",
        ])
        assert result.exit_code == 0

    def test_theme_page_niches(self):
        result = self._invoke(["theme-page", "niches"])
        assert result.exit_code == 0
        assert "finance" in result.output.lower() or "luxury" in result.output.lower()

    def test_theme_page_niches_json(self):
        result = self._invoke(["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) >= 8

    def test_theme_page_guide(self):
        result = self._invoke(["theme-page", "guide", "fitness_wellness"])
        assert result.exit_code == 0
        assert "fitness" in result.output.lower()

    def test_theme_page_guide_json(self):
        result = self._invoke(["--json", "theme-page", "guide", "luxury_lifestyle"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "account_setup" in data
        assert "monetization_roadmap" in data

    def test_theme_page_score(self):
        result = self._invoke(["theme-page", "score", "finance_investing"])
        assert result.exit_code == 0
        assert "score" in result.output.lower() or "Score" in result.output

    def test_theme_page_score_json(self):
        result = self._invoke(["--json", "theme-page", "score", "tech_gadgets"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "total_score" in data
        assert data["total_score"] > 0

    def test_no_project_fails_gracefully(self):
        result = self._invoke(["account", "list"])
        assert result.exit_code != 0 or "No session" in result.output

    def test_session_info(self, tmp_path):
        path = str(tmp_path / "info_session.trends.json")
        self._invoke(["session", "new", "infotest", "--region", "GB", "--niche", "food", "--output", path])
        result = self._invoke(["--project", path, "session", "info"])
        assert result.exit_code == 0

    def test_session_info_json(self, tmp_path):
        path = str(tmp_path / "info_json.trends.json")
        self._invoke(["session", "new", "infojson", "--region", "UK", "--niche", "travel", "--output", path])
        result = self._invoke(["--project", path, "--json", "session", "info"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["niche"] == "travel"
        assert data["youtube_trends"] == 0

    def test_hashtags_score_found(self, tmp_path):
        path = str(tmp_path / "ht_score.trends.json")
        self._invoke(["session", "new", "htscoretest", "--output", path])
        self._invoke(["--project", path, "trends", "fetch", "--mock"])
        self._invoke(["--project", path, "hashtags", "recommend"])
        result = self._invoke(["--project", path, "hashtags", "score", "fyp"])
        assert result.exit_code == 0

    def test_hashtags_score_not_found(self, tmp_path):
        path = str(tmp_path / "ht_notfound.trends.json")
        self._invoke(["session", "new", "htnotfound", "--output", path])
        result = self._invoke(["--project", path, "hashtags", "score", "xyzunknowntag99"])
        assert result.exit_code == 0
        assert "not in" in result.output.lower() or "found" in result.output.lower() or "0" in result.output

    def test_full_workflow_mock(self, tmp_path):
        """End-to-end workflow with mock data — no API keys needed."""
        path = str(tmp_path / "e2e_session.trends.json")

        # 1. Create session
        r = self._invoke(["session", "new", "e2etest", "--region", "US", "--niche", "fitness", "--output", path])
        assert r.exit_code == 0

        # 2. Add accounts
        r = self._invoke(["--project", path, "account", "add", "tiktok", "@fitpage", "--niche", "fitness"])
        assert r.exit_code == 0

        # 3. Fetch trends (mock)
        r = self._invoke(["--project", path, "trends", "fetch", "all", "--mock"])
        assert r.exit_code == 0

        # 4. Recommend hashtags
        r = self._invoke(["--project", path, "hashtags", "recommend"])
        assert r.exit_code == 0

        # 5. Get hashtag sets
        r = self._invoke(["--project", path, "hashtags", "sets"])
        assert r.exit_code == 0

        # 6. Trending music
        r = self._invoke(["--project", path, "music", "trending", "--mock"])
        assert r.exit_code == 0

        # 7. Optimize
        r = self._invoke(["--project", path, "optimize", "run"])
        assert r.exit_code == 0

        # 8. Calendar
        r = self._invoke(["--project", path, "optimize", "calendar", "--days", "3"])
        assert r.exit_code == 0

        # 9. Session info
        r = self._invoke(["--project", path, "--json", "session", "info"])
        assert r.exit_code == 0
        data = json.loads(r.output)
        assert data["youtube_trends"] > 0
        assert data["tiktok_trends"] > 0
        assert data["hashtags"] > 0
        assert data["sounds"] > 0
        assert data["has_optimization"] is True
