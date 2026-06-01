"""TrendScout – Unit tests (no network required).

Tests cover: session, account management, trend logic, theme page playbook.
Run: cd trendscout/agent-harness && pytest tests/test_core.py -v
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cli_anything.trendscout.core.session import Session
from cli_anything.trendscout.core import account as acc_mod
from cli_anything.trendscout.core import theme_page as tp_mod
from cli_anything.trendscout.core import trends as trends_mod


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def session():
    return Session()


@pytest.fixture
def session_with_accounts():
    s = Session()
    acc_mod.add_account(s, "fitpage", "tiktok", niche="fitness", followers=5000)
    acc_mod.add_account(s, "techreviews", "youtube", niche="tech", followers=12000)
    return s


# ── Session ───────────────────────────────────────────────────────────────────

class TestSession:
    def test_initial_state(self, session):
        assert session.config["accounts"] == []
        assert session.config["watched_niches"] == []
        assert not session._modified

    def test_snapshot_sets_modified(self, session):
        session.snapshot("test")
        assert session._modified

    def test_undo(self, session):
        session.config["accounts"].append({"id": "a0"})
        session.snapshot("add a0")
        session.config["accounts"].clear()
        session.undo()
        assert len(session.config["accounts"]) == 1

    def test_undo_empty_raises(self, session):
        with pytest.raises(RuntimeError, match="Nothing to undo"):
            session.undo()

    def test_redo_after_undo(self, session):
        session.config["watched_niches"].append("fitness")
        session.snapshot("add niche")
        session.config["watched_niches"].clear()
        session.undo()
        assert len(session.config["watched_niches"]) == 1
        session.redo()
        assert len(session.config["watched_niches"]) == 0

    def test_redo_empty_raises(self, session):
        with pytest.raises(RuntimeError, match="Nothing to redo"):
            session.redo()

    def test_snapshot_clears_redo(self, session):
        session.config["accounts"].append({"id": "a0"})
        session.snapshot("s1")
        session.config["accounts"].clear()
        session.undo()
        session.snapshot("new_branch")
        assert len(session._redo_stack) == 0

    def test_max_undo_limit(self, session):
        for i in range(Session.MAX_UNDO + 15):
            session.snapshot(f"snap{i}")
        assert len(session._undo_stack) == Session.MAX_UNDO

    def test_status_shape(self, session):
        s = session.status()
        assert "accounts" in s
        assert "modified" in s
        assert "undo_count" in s
        assert "redo_count" in s

    def test_list_history(self, session):
        session.snapshot("op1")
        session.snapshot("op2")
        h = session.list_history()
        assert "op1" in h
        assert "op2" in h


# ── Account management ────────────────────────────────────────────────────────

class TestAccount:
    def test_add_account(self, session):
        result = acc_mod.add_account(session, "mypage", "tiktok", niche="gaming")
        assert result["success"]
        assert result["handle"] == "mypage"
        assert result["platform"] == "tiktok"

    def test_add_account_strips_at(self, session):
        result = acc_mod.add_account(session, "@mypage", "tiktok")
        assert result["handle"] == "mypage"

    def test_add_account_invalid_platform(self, session):
        with pytest.raises(ValueError, match="Unsupported platform"):
            acc_mod.add_account(session, "page", "snapchat")

    def test_add_duplicate_raises(self, session):
        acc_mod.add_account(session, "page1", "tiktok")
        with pytest.raises(ValueError, match="already exists"):
            acc_mod.add_account(session, "page1", "tiktok")

    def test_sequential_ids(self, session):
        acc_mod.add_account(session, "p1", "tiktok")
        acc_mod.add_account(session, "p2", "youtube")
        accounts = acc_mod.list_accounts(session)
        assert accounts[0]["id"] == "acc0"
        assert accounts[1]["id"] == "acc1"

    def test_list_accounts_empty(self, session):
        assert acc_mod.list_accounts(session) == []

    def test_list_accounts(self, session_with_accounts):
        result = acc_mod.list_accounts(session_with_accounts)
        assert len(result) == 2
        handles = [a["handle"] for a in result]
        assert "fitpage" in handles
        assert "techreviews" in handles

    def test_remove_account(self, session_with_accounts):
        result = acc_mod.remove_account(session_with_accounts, "acc0")
        assert result["success"]
        assert len(acc_mod.list_accounts(session_with_accounts)) == 1

    def test_remove_nonexistent_raises(self, session):
        with pytest.raises(ValueError, match="not found"):
            acc_mod.remove_account(session, "accX")

    def test_update_followers(self, session_with_accounts):
        result = acc_mod.update_account(session_with_accounts, "acc0", followers=10000)
        assert result["success"]
        account = acc_mod.list_accounts(session_with_accounts)[0]
        assert account["followers"] == 10000

    def test_update_niche(self, session_with_accounts):
        acc_mod.update_account(session_with_accounts, "acc0", niche="bodybuilding")
        account = acc_mod.list_accounts(session_with_accounts)[0]
        assert account["niche"] == "bodybuilding"

    def test_audit_returns_score(self, session_with_accounts):
        result = acc_mod.audit_account(session_with_accounts, "acc0")
        assert "score" in result
        assert "grade" in result
        assert 0 <= result["score"] <= 100
        assert result["grade"] in ("A", "B", "C", "D", "F")

    def test_audit_with_all_completed(self, session_with_accounts):
        checklist = acc_mod.get_checklist("tiktok")
        all_ids = [item["id"] for item in checklist]
        result = acc_mod.audit_account(session_with_accounts, "acc0", completed_items=all_ids)
        assert result["score"] == 100
        assert result["grade"] == "A"

    def test_audit_with_no_completed(self, session_with_accounts):
        result = acc_mod.audit_account(session_with_accounts, "acc0", completed_items=[])
        assert result["score"] == 0
        assert result["grade"] == "F"

    def test_audit_caches_score(self, session_with_accounts):
        acc_mod.audit_account(session_with_accounts, "acc0", completed_items=["bio_keywords", "profile_pic"])
        accounts = acc_mod.list_accounts(session_with_accounts)
        acc = next(a for a in accounts if a["id"] == "acc0")
        assert acc["profile_score"] is not None

    def test_optimize_all_empty(self, session):
        result = acc_mod.optimize_all_accounts(session)
        assert result["total_accounts"] == 0
        assert result["overall_avg_score"] == 0

    def test_optimize_all(self, session_with_accounts):
        result = acc_mod.optimize_all_accounts(session_with_accounts)
        assert result["total_accounts"] == 2
        assert "overall_avg_score" in result
        assert len(result["accounts"]) == 2

    def test_growth_plan_shape(self, session_with_accounts):
        result = acc_mod.growth_plan(session_with_accounts, "acc0", goal_followers=50000, timeframe_weeks=12)
        assert result["goal_followers"] == 50000
        assert len(result["phases"]) == 3
        assert "key_metrics_to_track" in result

    def test_growth_plan_already_at_goal(self, session_with_accounts):
        acc_mod.update_account(session_with_accounts, "acc0", followers=100000)
        result = acc_mod.growth_plan(session_with_accounts, "acc0", goal_followers=50000)
        assert result["weekly_follower_target"] == 0

    def test_get_checklist_tiktok(self):
        result = acc_mod.get_checklist("tiktok")
        assert len(result) >= 5
        ids = [item["id"] for item in result]
        assert "bio_keywords" in ids
        assert "pinned_videos" in ids

    def test_get_checklist_youtube(self):
        result = acc_mod.get_checklist("youtube")
        ids = [item["id"] for item in result]
        assert "thumbnails" in ids
        assert "seo_titles" in ids

    def test_get_checklist_invalid_raises(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            acc_mod.get_checklist("snapchat")

    def test_audit_top_priority_actions_ordered_by_weight(self, session_with_accounts):
        result = acc_mod.audit_account(session_with_accounts, "acc0", completed_items=[])
        actions = result["top_priority_actions"]
        weights = [a["impact"] for a in actions]
        assert weights == sorted(weights, reverse=True)


# ── Theme page ────────────────────────────────────────────────────────────────

class TestThemePage:
    def test_get_playbook_steps(self):
        playbook = tp_mod.get_playbook()
        assert playbook["total_steps"] == 7
        assert len(playbook["steps"]) == 7

    def test_get_playbook_step_valid(self):
        step = tp_mod.get_playbook_step(1)
        assert step["step"] == 1
        assert "title" in step
        assert "action_items" in step
        assert len(step["action_items"]) > 0

    def test_get_playbook_step_last(self):
        step = tp_mod.get_playbook_step(7)
        assert step["next_step"] is None

    def test_get_playbook_step_chained(self):
        for i in range(1, 7):
            step = tp_mod.get_playbook_step(i)
            assert step["next_step"] == i + 1

    def test_get_playbook_step_invalid(self):
        with pytest.raises(ValueError, match="not found"):
            tp_mod.get_playbook_step(0)
        with pytest.raises(ValueError, match="not found"):
            tp_mod.get_playbook_step(8)

    def test_list_niches_cpm_sort(self):
        result = tp_mod.list_niches(sort_by="cpm")
        assert result["sort_by"] == "cpm"
        assert result["count"] >= 10
        niches = result["niches"]
        # First niche should have high/very high CPM
        assert "high" in niches[0]["cpm"].lower()

    def test_list_niches_opportunity_sort(self):
        result = tp_mod.list_niches(sort_by="opportunity")
        assert result["sort_by"] == "opportunity"
        assert result["count"] >= 10

    def test_list_niches_competition_sort(self):
        result = tp_mod.list_niches(sort_by="competition")
        # First should be low competition
        assert "low" in result["niches"][0]["competition"].lower()

    def test_list_niches_invalid_sort(self):
        with pytest.raises(ValueError, match="Unknown sort_by"):
            tp_mod.list_niches(sort_by="invalid")

    def test_list_content_formats_tiktok(self):
        result = tp_mod.list_content_formats("tiktok")
        assert result["platform"] == "tiktok"
        assert result["count"] >= 5
        # Should be sorted by virality (very high first)
        first_virality = result["formats"][0]["virality"].lower()
        assert "very high" in first_virality or "high" in first_virality

    def test_list_content_formats_youtube(self):
        result = tp_mod.list_content_formats("youtube")
        assert result["platform"] == "youtube"
        assert result["count"] >= 5

    def test_list_content_formats_invalid(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            tp_mod.list_content_formats("instagram")

    def test_list_monetization_all(self):
        result = tp_mod.list_monetization_methods("all")
        assert result["count"] >= 8
        methods = [m["method"] for m in result["methods"]]
        assert "Affiliate Marketing" in methods
        assert "Brand Sponsorships" in methods

    def test_list_monetization_niche_filter(self):
        result = tp_mod.list_monetization_methods("fitness")
        assert result["count"] >= 2
        # All returned methods should be relevant to fitness or "all niches"
        for m in result["methods"]:
            relevant = any("fitness" in b.lower() or "all niches" in b.lower() for b in m["best_for"])
            assert relevant, f"Method '{m['method']}' not relevant to fitness: {m['best_for']}"

    def test_quick_start_guide_shape(self):
        result = tp_mod.quick_start_guide("gaming", "tiktok")
        assert result["niche"] == "gaming"
        assert result["platform"] == "tiktok"
        assert "week_1_actions" in result
        assert len(result["week_1_actions"]) >= 3
        assert "top_content_formats" in result
        assert "recommended_monetization" in result
        assert "pro_tip" in result

    def test_quick_start_guide_unknown_niche(self):
        # Unknown niches should still work (fallback niche config)
        result = tp_mod.quick_start_guide("beekeeping", "tiktok")
        assert result["niche"] == "beekeeping"
        assert result["week_1_actions"]

    def test_every_niche_has_monetization(self):
        for niche_data in tp_mod.NICHES_WITH_CPM:
            assert len(niche_data["monetization"]) > 0

    def test_every_monetization_has_required_fields(self):
        for m in tp_mod.MONETIZATION_METHODS:
            assert "method" in m
            assert "difficulty" in m
            assert "income_potential" in m
            assert "how_to" in m
            assert "best_for" in m

    def test_all_playbook_steps_have_details(self):
        for step in tp_mod.THEME_PAGE_PLAYBOOK_STEPS:
            assert len(step["details"]) >= 3


# ── Trend logic (offline) ─────────────────────────────────────────────────────

class TestTrendsLogic:
    def test_best_posting_times_both(self):
        result = trends_mod.best_posting_times("both")
        assert "platforms" in result
        assert "tiktok" in result["platforms"]
        assert "youtube" in result["platforms"]
        assert "instagram" in result["platforms"]

    def test_best_posting_times_tiktok(self):
        result = trends_mod.best_posting_times("tiktok")
        assert "best_days" in result
        assert "best_times_est" in result
        assert "optimal_frequency" in result

    def test_best_posting_times_youtube(self):
        result = trends_mod.best_posting_times("youtube")
        assert "best_days" in result

    def test_best_posting_times_invalid_platform(self):
        with pytest.raises(ValueError, match="Unknown platform"):
            trends_mod.best_posting_times("snapchat")

    def test_niche_strategy_tip_known_niches(self):
        from cli_anything.trendscout.core.trends import _niche_strategy_tip
        for niche in ["gaming", "music", "beauty", "fitness", "food", "travel"]:
            tip = _niche_strategy_tip(niche)
            assert isinstance(tip, str)
            assert len(tip) > 20

    def test_niche_strategy_tip_unknown_niche(self):
        from cli_anything.trendscout.core.trends import _niche_strategy_tip
        tip = _niche_strategy_tip("beekeeping")
        assert isinstance(tip, str)
        assert len(tip) > 0
