"""SocialOptimizer core unit tests."""

import json
import pytest
from pathlib import Path

from cli_anything.social_optimizer.core import config as config_mod
from cli_anything.social_optimizer.core import accounts as accounts_mod
from cli_anything.social_optimizer.core import schedule as schedule_mod
from cli_anything.social_optimizer.core import strategy as strategy_mod
from cli_anything.social_optimizer.core import theme_page as theme_mod


# ── config ─────────────────────────────────────────────────────────────────────

def test_add_account(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    acc = config_mod.add_account("Fitness Page", "tiktok", "fitdaily", niche="fitness")
    assert acc["handle"] == "fitdaily"
    assert acc["platform"] == "tiktok"
    assert acc["niche"] == "fitness"


def test_add_account_duplicate(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    config_mod.add_account("FP", "tiktok", "fitdaily")
    with pytest.raises(ValueError, match="already exists"):
        config_mod.add_account("FP2", "tiktok", "fitdaily")


def test_add_account_invalid_platform(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    with pytest.raises(ValueError, match="Unsupported platform"):
        config_mod.add_account("X", "snapchat", "handle")


def test_list_accounts(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    config_mod.add_account("A", "tiktok", "handle1")
    config_mod.add_account("B", "youtube", "handle2")

    all_accs = config_mod.list_accounts()
    assert len(all_accs) == 2

    tt_only = config_mod.list_accounts("tiktok")
    assert len(tt_only) == 1
    assert tt_only[0]["platform"] == "tiktok"


def test_remove_account(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    config_mod.add_account("A", "tiktok", "handle1")
    removed = config_mod.remove_account("handle1")
    assert removed["handle"] == "handle1"
    assert config_mod.list_accounts() == []


def test_remove_nonexistent(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    with pytest.raises(ValueError, match="not found"):
        config_mod.remove_account("nonexistent")


# ── accounts optimization ──────────────────────────────────────────────────────

def test_optimize_tiktok():
    result = accounts_mod.optimize_account("tiktok")
    assert result["platform"] == "tiktok"
    assert len(result["high_priority"]) > 0
    assert all("item" in i and "detail" in i for i in result["high_priority"])


def test_optimize_youtube():
    result = accounts_mod.optimize_account("youtube")
    assert result["platform"] == "youtube"
    assert len(result["high_priority"]) > 0


def test_optimize_with_niche():
    result = accounts_mod.optimize_account("tiktok", "fitness")
    assert result["niche"] == "fitness"
    assert isinstance(result["niche_specific_tips"], list)
    assert len(result["niche_specific_tips"]) > 0


def test_optimize_invalid_platform():
    with pytest.raises(ValueError):
        accounts_mod.optimize_account("snapchat")


def test_audit_all_accounts(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(config_mod, "ACCOUNTS_FILE", tmp_path / "accounts.json")

    config_mod.add_account("Fit", "tiktok", "fitpage", niche="fitness")
    config_mod.add_account("Cook", "instagram", "cookpage", niche="food")
    accounts = config_mod.list_accounts()

    results = accounts_mod.audit_all_accounts(accounts)
    assert len(results) == 2
    for r in results:
        assert "handle" in r
        assert "platform" in r


def test_all_supported_platforms():
    for plat in ["tiktok", "youtube", "instagram", "twitter", "facebook"]:
        result = accounts_mod.optimize_account(plat)
        assert result["platform"] == plat
        assert len(result["high_priority"]) >= 1


# ── schedule ───────────────────────────────────────────────────────────────────

def test_get_best_times():
    times = schedule_mod.get_best_times("tiktok")
    assert "monday" in times
    assert all(isinstance(v, list) for v in times.values())
    for hours in times.values():
        for h in hours:
            assert h.endswith(":00")


def test_get_best_times_all_platforms():
    for plat in ["tiktok", "youtube", "instagram", "twitter", "facebook"]:
        times = schedule_mod.get_best_times(plat)
        assert len(times) == 7


def test_get_best_times_invalid():
    with pytest.raises(ValueError):
        schedule_mod.get_best_times("twitch")


def test_generate_schedule():
    sched = schedule_mod.generate_schedule("tiktok", posts_per_day=2)
    assert len(sched) <= 14
    for s in sched:
        assert "day" in s
        assert "time" in s
        assert "post_type" in s


def test_generate_schedule_single_post():
    sched = schedule_mod.generate_schedule("youtube", posts_per_day=1)
    assert len(sched) == 7


def test_schedule_frequency_advice():
    advice = schedule_mod.schedule_frequency_advice("tiktok")
    assert advice["optimal_posts_per_day"] > 0
    assert "note" in advice
    assert "content_mix" in advice


def test_schedule_frequency_all_platforms():
    for plat in ["tiktok", "youtube", "instagram", "twitter", "facebook"]:
        advice = schedule_mod.schedule_frequency_advice(plat)
        assert "weekly_target" in advice


# ── strategy ───────────────────────────────────────────────────────────────────

def test_get_viral_frameworks_all():
    fws = strategy_mod.get_viral_frameworks()
    assert len(fws) >= 5
    for fw in fws:
        assert "name" in fw
        assert "structure" in fw
        assert "example" in fw


def test_get_viral_frameworks_niche():
    fws = strategy_mod.get_viral_frameworks("fitness")
    assert len(fws) > 0
    for fw in fws:
        assert "all" in fw["best_for"] or "fitness" in fw["best_for"]


def test_get_hook_templates():
    hooks = strategy_mod.get_hook_templates("fitness", 5)
    assert len(hooks) == 5
    for h in hooks:
        assert isinstance(h, str)
        assert len(h) > 5


def test_get_cta_templates():
    ctas = strategy_mod.get_cta_templates("tiktok", "fitness", "fitdaily")
    assert len(ctas) > 0
    for c in ctas:
        assert isinstance(c, str)


def test_generate_content_plan():
    plan = strategy_mod.generate_content_plan("fitness", "tiktok", 7)
    assert len(plan) == 7
    days = {p["day"] for p in plan}
    assert len(days) == 7
    for p in plan:
        assert "framework" in p
        assert "suggested_hook" in p
        assert "suggested_cta" in p


def test_viral_checklist():
    checklist = strategy_mod.viral_checklist("tiktok")
    assert len(checklist) >= 5
    for item in checklist:
        assert "item" in item
        assert "check" in item


def test_viral_checklist_all_platforms():
    for plat in ["tiktok", "youtube", "instagram"]:
        cl = strategy_mod.viral_checklist(plat)
        assert len(cl) >= 5


# ── theme page ─────────────────────────────────────────────────────────────────

def test_niche_research_known():
    data = theme_mod.niche_research("fitness")
    assert data["keyword"] == "fitness"
    assert "monetization_potential" in data
    assert data["monetization_potential"] >= 1
    assert isinstance(data["monetization"], list)


def test_niche_research_unknown():
    data = theme_mod.niche_research("unicorns")
    assert data["keyword"] == "unicorns"
    assert "note" in data


def test_list_niches():
    niches = theme_mod.list_niches()
    assert len(niches) >= 5
    scores = [n["monetization"] for n in niches]
    assert scores == sorted(scores, reverse=True)


def test_list_niches_filtered():
    niches = theme_mod.list_niches(min_monetization=9)
    assert all(n["monetization"] >= 9 for n in niches)


def test_get_creation_guide():
    guide = theme_mod.get_creation_guide()
    assert len(guide) == 6
    phases = [p["phase"] for p in guide]
    assert phases == list(range(1, 7))


def test_get_creation_guide_phase():
    guide = theme_mod.get_creation_guide(phase=3)
    assert len(guide) == 1
    assert guide[0]["phase"] == 3
    assert len(guide[0]["steps"]) >= 3


def test_get_converting_guide():
    guide = theme_mod.get_converting_guide()
    assert len(guide) >= 4
    stages = {g["stage"] for g in guide}
    assert "Cold Traffic → Follower" in stages


def test_monetization_strategies():
    strategies = theme_mod.monetization_strategies()
    assert len(strategies) >= 5
    for s in strategies:
        assert "strategy" in s
        assert "revenue_range" in s
        assert "entry_point" in s


def test_monetization_strategies_with_niche():
    strategies = theme_mod.monetization_strategies(niche="finance")
    assert len(strategies) >= 5
