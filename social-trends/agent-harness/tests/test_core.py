"""Social Trends CLI - Core unit tests (fully offline, no network calls).

Run: cd social-trends/agent-harness && pytest tests/test_core.py -v
"""

import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.social_trends.core.store import Store
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.core import scheduler as sched_mod


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def store(tmp_path):
    """Isolated in-memory store backed by a temp file."""
    return Store(path=str(tmp_path / "session.json"))


@pytest.fixture
def store_with_account(store):
    accounts_mod.add_account(store, "tiktok", "test_user", "fitness")
    return store


@pytest.fixture
def account_id(store_with_account):
    return store_with_account.accounts[0]["id"]


# ── Store tests ───────────────────────────────────────────────────────────────

def test_store_creates_empty_session(tmp_path):
    s = Store(path=str(tmp_path / "new.json"))
    assert s.trends == []
    assert s.hashtags == []
    assert s.music == []
    assert s.accounts == []


def test_store_persists_and_reloads(tmp_path):
    path = str(tmp_path / "sess.json")
    s1 = Store(path=path)
    s1.trends = [{"id": "t0", "title": "viral video"}]
    s1.save()

    s2 = Store(path=path)
    assert len(s2.trends) == 1
    assert s2.trends[0]["title"] == "viral video"


def test_store_reset(store):
    store.trends = [{"id": "t0"}]
    store.reset()
    assert store.trends == []


# ── Trends tests ──────────────────────────────────────────────────────────────

def test_fetch_trends_youtube_mock(store):
    with patch("cli_anything.social_trends.core.trends._try_fetch_youtube", return_value=[]):
        results = trends_mod.fetch_trends(store, platform="youtube", limit=5)
    assert len(results) == 5
    assert all(t["platform"] == "youtube" for t in results)
    assert all("title" in t for t in results)
    assert all(t["source"] == "mock" for t in results)


def test_fetch_trends_tiktok_mock(store):
    with patch("cli_anything.social_trends.core.trends._try_fetch_tiktok", return_value=[]):
        results = trends_mod.fetch_trends(store, platform="tiktok", limit=5)
    assert len(results) == 5
    assert all(t["platform"] == "tiktok" for t in results)


def test_fetch_trends_both_platforms(store):
    with patch("cli_anything.social_trends.core.trends._try_fetch_youtube", return_value=[]), \
         patch("cli_anything.social_trends.core.trends._try_fetch_tiktok", return_value=[]):
        results = trends_mod.fetch_trends(store, platform="both", limit=5)
    assert len(results) == 10  # 5 youtube + 5 tiktok
    platforms = {t["platform"] for t in results}
    assert "youtube" in platforms
    assert "tiktok" in platforms


def test_fetch_trends_persists_to_store(store):
    with patch("cli_anything.social_trends.core.trends._try_fetch_youtube", return_value=[]), \
         patch("cli_anything.social_trends.core.trends._try_fetch_tiktok", return_value=[]):
        trends_mod.fetch_trends(store, platform="both", limit=3)
    assert len(store.trends) == 6


def test_list_trends_returns_cached(store):
    store.trends = [{"rank": 1, "title": "Test"}]
    result = trends_mod.list_trends(store)
    assert result == [{"rank": 1, "title": "Test"}]


def test_search_trends_by_keyword(store):
    with patch("cli_anything.social_trends.core.trends._try_fetch_youtube", return_value=[]), \
         patch("cli_anything.social_trends.core.trends._try_fetch_tiktok", return_value=[]):
        trends_mod.fetch_trends(store, platform="youtube", limit=10)
    results = trends_mod.search_trends(store, "workout")
    assert all("workout" in r["title"].lower() or
               any("workout" in h.lower() for h in r.get("hashtags", []))
               for r in results)


def test_export_trends(store, tmp_path):
    store.trends = [{"id": "t0", "title": "Viral"}]
    path = str(tmp_path / "trends.json")
    result = trends_mod.export_trends(store, path)
    assert result["success"]
    assert result["count"] == 1
    with open(path) as f:
        data = json.load(f)
    assert data["trends"][0]["title"] == "Viral"


# ── Hashtags tests ────────────────────────────────────────────────────────────

def test_research_hashtags_fitness(store):
    results = hashtags_mod.research_hashtags(store, "fitness", limit=12)
    assert len(results) == 12
    assert all("tag" in h for h in results)
    assert all("competition" in h for h in results)


def test_research_hashtags_finance(store):
    results = hashtags_mod.research_hashtags(store, "finance", limit=5)
    assert len(results) == 5
    assert all(h["niche"] == "finance" for h in results)


def test_research_hashtags_unknown_niche_fallback(store):
    results = hashtags_mod.research_hashtags(store, "underwater_basket_weaving", limit=5)
    assert len(results) > 0


def test_rank_hashtags_by_engagement(store):
    hashtags_mod.research_hashtags(store, "fitness", limit=12)
    ranked = hashtags_mod.rank_hashtags(store, by="engagement")
    rates = [h["engagement_rate"] for h in ranked]
    assert rates == sorted(rates, reverse=True)


def test_rank_hashtags_empty_store(store):
    result = hashtags_mod.rank_hashtags(store)
    assert result == []


def test_suggest_hashtags_mix(store):
    result = hashtags_mod.suggest_hashtags(store, "finance", count=30)
    assert "high_competition" in result
    assert "medium_competition" in result
    assert "low_competition" in result
    assert "combined" in result
    assert len(result["combined"]) > 0


def test_export_hashtags(store, tmp_path):
    hashtags_mod.research_hashtags(store, "gaming", limit=5)
    path = str(tmp_path / "hashtags.json")
    result = hashtags_mod.export_hashtags(store, path)
    assert result["success"]
    assert result["count"] == 5


# ── Music tests ───────────────────────────────────────────────────────────────

def test_fetch_music_tiktok_mock(store):
    with patch("cli_anything.social_trends.core.music._try_fetch_tiktok_music", return_value=[]):
        results = music_mod.fetch_music(store, platform="tiktok", limit=5)
    assert len(results) == 5
    assert all(m["platform"] == "tiktok" for m in results)


def test_fetch_music_youtube_mock(store):
    results = music_mod.fetch_music(store, platform="youtube", limit=5)
    assert len(results) == 5
    assert all(m["platform"] == "youtube" for m in results)


def test_fetch_music_both(store):
    with patch("cli_anything.social_trends.core.music._try_fetch_tiktok_music", return_value=[]):
        results = music_mod.fetch_music(store, platform="both", limit=5)
    assert len(results) == 10
    platforms = {m["platform"] for m in results}
    assert "tiktok" in platforms
    assert "youtube" in platforms


def test_search_music(store):
    with patch("cli_anything.social_trends.core.music._try_fetch_tiktok_music", return_value=[]):
        music_mod.fetch_music(store, platform="both", limit=10)
    results = music_mod.search_music(store, "taylor")
    assert all("taylor" in m["artist"].lower() or "taylor" in m["title"].lower()
               for m in results)


def test_export_music(store, tmp_path):
    store.music = [{"id": "m0", "title": "Test Track", "artist": "Artist"}]
    path = str(tmp_path / "music.json")
    result = music_mod.export_music(store, path)
    assert result["success"]
    assert result["count"] == 1


# ── Accounts tests ────────────────────────────────────────────────────────────

def test_add_account(store):
    acc = accounts_mod.add_account(store, "tiktok", "fitpage", "fitness")
    assert acc["platform"] == "tiktok"
    assert acc["username"] == "fitpage"
    assert acc["niche"] == "fitness"
    assert acc["id"].startswith("acc_")


def test_add_account_persists(store):
    accounts_mod.add_account(store, "instagram", "financeking", "finance")
    assert len(store.accounts) == 1


def test_list_accounts(store):
    accounts_mod.add_account(store, "tiktok", "user1", "fitness")
    accounts_mod.add_account(store, "youtube", "user2", "gaming")
    result = accounts_mod.list_accounts(store)
    assert len(result) == 2


def test_optimize_account_returns_full_report(store_with_account, account_id):
    report = accounts_mod.optimize_account(store_with_account, account_id)
    assert "suggested_bio" in report
    assert "content_pillars" in report
    assert "best_posting_times" in report
    assert "posting_frequency" in report
    assert "hashtag_strategy" in report
    assert "growth_actions" in report
    assert "monetization_timeline" in report


def test_optimize_account_updates_score(store_with_account, account_id):
    accounts_mod.optimize_account(store_with_account, account_id)
    acc = store_with_account.get_account(account_id)
    assert acc["optimization_score"] > 0


def test_score_account(store_with_account, account_id):
    result = accounts_mod.score_account(store_with_account, account_id)
    assert 0 <= result["score"] <= 100
    assert result["grade"] in ("A", "B", "C", "D")
    assert "breakdown" in result


def test_score_increases_after_optimize(store_with_account, account_id):
    before = accounts_mod.score_account(store_with_account, account_id)["score"]
    accounts_mod.optimize_account(store_with_account, account_id)
    after = accounts_mod.score_account(store_with_account, account_id)["score"]
    assert after >= before


def test_get_account_not_found(store):
    with pytest.raises(KeyError):
        store.get_account("nonexistent_id")


def test_export_accounts(store_with_account, tmp_path):
    path = str(tmp_path / "accounts.json")
    result = accounts_mod.export_accounts(store_with_account, path)
    assert result["success"]
    assert result["count"] == 1


# ── Theme pages tests ─────────────────────────────────────────────────────────

def test_list_niches_returns_all(store):
    niches = theme_mod.list_niches()
    assert len(niches) == 10
    names = [n["niche"] for n in niches]
    assert "fitness" in names
    assert "finance" in names
    assert "crypto" in names


def test_list_niches_sorted_by_conversion(store):
    niches = theme_mod.list_niches()
    scores = [n["conversion_potential"] for n in niches]
    assert scores == sorted(scores, reverse=True)


def test_get_guide_fitness(store):
    guide = theme_mod.get_guide("fitness")
    assert guide["niche"] == "fitness"
    assert "guide" in guide
    assert "step_1_setup" in guide["guide"]
    assert "step_4_monetization" in guide["guide"]


def test_get_guide_unknown_niche_fallback(store):
    guide = theme_mod.get_guide("underwater_basket_weaving")
    assert guide["niche"] == "motivational"


def test_get_strategy_finance(store):
    strategy = theme_mod.get_strategy("finance")
    assert strategy["niche"] == "finance"
    assert "monetization_paths" in strategy
    assert "conversion_tactics" in strategy
    assert "brand_deal_guide" in strategy
    assert "digital_products" in strategy


def test_get_conversion_plan(store_with_account, account_id):
    plan = theme_mod.get_conversion_plan(store_with_account, account_id, "finance")
    assert plan["to_niche"] == "finance"
    assert "conversion_plan" in plan
    assert "week_1" in plan["conversion_plan"]
    assert "week_4_plus" in plan["conversion_plan"]
    assert "success_metrics" in plan


def test_conversion_plan_marks_account(store_with_account, account_id):
    theme_mod.get_conversion_plan(store_with_account, account_id, "gaming")
    acc = store_with_account.get_account(account_id)
    assert acc.get("in_conversion") is True
    assert acc.get("target_niche") == "gaming"


# ── Scheduler tests ───────────────────────────────────────────────────────────

def test_optimize_schedule(store_with_account, account_id):
    result = sched_mod.optimize_schedule(store_with_account, account_id)
    assert "weekly_schedule" in result
    assert "posting_frequency" in result
    assert "algorithm_tips" in result
    assert len(result["weekly_schedule"]) == 7


def test_generate_calendar_7_days(store_with_account, account_id):
    calendar = sched_mod.generate_calendar(store_with_account, account_id, days=7)
    assert len(calendar) == 7
    for day in calendar:
        assert "date" in day
        assert "posts" in day
        assert len(day["posts"]) > 0


def test_generate_calendar_30_days(store_with_account, account_id):
    calendar = sched_mod.generate_calendar(store_with_account, account_id, days=30)
    assert len(calendar) == 30


def test_calendar_post_has_required_fields(store_with_account, account_id):
    calendar = sched_mod.generate_calendar(store_with_account, account_id, days=1)
    post = calendar[0]["posts"][0]
    assert "time" in post
    assert "content_type" in post
    assert "format" in post
    assert "hook_idea" in post
    assert "hashtags" in post
    assert "cta" in post


def test_export_schedule(store_with_account, account_id, tmp_path):
    path = str(tmp_path / "schedule.json")
    result = sched_mod.export_schedule(store_with_account, account_id, path)
    assert result["success"]
    with open(path) as f:
        data = json.load(f)
    assert "calendar" in data
    assert len(data["calendar"]) == 30


# ── CLI integration tests (no real I/O) ───────────────────────────────────────

def test_cli_trends_fetch_json(tmp_path):
    from click.testing import CliRunner
    from cli_anything.social_trends.social_trends_cli import cli
    import cli_anything.social_trends.social_trends_cli as cli_mod

    runner = CliRunner()
    old_store = cli_mod._store
    cli_mod._store = Store(path=str(tmp_path / "cli_test.json"))

    try:
        with patch("cli_anything.social_trends.core.trends._try_fetch_youtube", return_value=[]), \
             patch("cli_anything.social_trends.core.trends._try_fetch_tiktok", return_value=[]):
            result = runner.invoke(cli, ["--json", "trends", "fetch", "--platform", "youtube", "--limit", "3"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3
    finally:
        cli_mod._store = old_store


def test_cli_accounts_workflow(tmp_path):
    from click.testing import CliRunner
    from cli_anything.social_trends.social_trends_cli import cli
    import cli_anything.social_trends.social_trends_cli as cli_mod

    runner = CliRunner()
    old_store = cli_mod._store
    cli_mod._store = Store(path=str(tmp_path / "cli_acc.json"))

    try:
        r1 = runner.invoke(cli, ["--json", "accounts", "add",
                                 "--platform", "tiktok",
                                 "--username", "testpage",
                                 "--niche", "fitness"])
        assert r1.exit_code == 0
        acc = json.loads(r1.output)
        acc_id = acc["id"]

        r2 = runner.invoke(cli, ["--json", "accounts", "score", acc_id])
        assert r2.exit_code == 0
        score_data = json.loads(r2.output)
        assert "score" in score_data
    finally:
        cli_mod._store = old_store


def test_cli_hashtags_suggest_json(tmp_path):
    from click.testing import CliRunner
    from cli_anything.social_trends.social_trends_cli import cli
    import cli_anything.social_trends.social_trends_cli as cli_mod

    runner = CliRunner()
    old_store = cli_mod._store
    cli_mod._store = Store(path=str(tmp_path / "cli_ht.json"))

    try:
        result = runner.invoke(cli, ["--json", "hashtags", "suggest", "--niche", "finance", "--count", "20"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "combined" in data
        assert len(data["combined"]) > 0
    finally:
        cli_mod._store = old_store


def test_cli_theme_pages_niches_json(tmp_path):
    from click.testing import CliRunner
    from cli_anything.social_trends.social_trends_cli import cli
    import cli_anything.social_trends.social_trends_cli as cli_mod

    runner = CliRunner()
    old_store = cli_mod._store
    cli_mod._store = Store(path=str(tmp_path / "cli_tp.json"))

    try:
        result = runner.invoke(cli, ["--json", "theme-pages", "niches"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 10
    finally:
        cli_mod._store = old_store
