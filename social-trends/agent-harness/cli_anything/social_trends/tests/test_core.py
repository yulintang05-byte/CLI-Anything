"""Unit tests for Social Trends core modules."""

import pytest
from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod


@pytest.fixture
def sess(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "cli_anything.social_trends.core.session._CONFIG_DIR", tmp_path
    )
    monkeypatch.setattr(
        "cli_anything.social_trends.core.session._CONFIG_FILE", tmp_path / "config.json"
    )
    monkeypatch.setattr(
        "cli_anything.social_trends.core.session._CACHE_FILE", tmp_path / "cache.json"
    )
    return Session()


# ── Session tests ─────────────────────────────────────────────────────────────

class TestSession:
    def test_default_config(self, sess):
        assert "api_keys" in sess.config
        assert "accounts" in sess.config
        assert "theme_pages" in sess.config

    def test_undo_redo(self, sess):
        # snapshot() saves the CURRENT state before a mutation
        sess.snapshot("before fitness")
        sess.config["niches"] = ["fitness"]
        sess.snapshot("before finance")
        sess.config["niches"] = ["finance"]

        sess.undo()
        assert sess.config["niches"] == ["fitness"]

        sess.redo()
        assert sess.config["niches"] == ["finance"]

    def test_undo_empty_raises(self, sess):
        with pytest.raises(RuntimeError):
            sess.undo()

    def test_cache_set_get(self, sess):
        sess.set_cache("test_key", {"data": 42})
        result = sess.get_cache("test_key", max_age_minutes=5)
        assert result == {"data": 42}

    def test_cache_expired(self, sess):
        sess.set_cache("test_key", {"data": 42})
        result = sess.get_cache("test_key", max_age_minutes=0)
        assert result is None

    def test_status(self, sess):
        s = sess.status()
        assert "accounts_count" in s
        assert "youtube_api_key_set" in s


# ── Trends tests ──────────────────────────────────────────────────────────────

class TestTrends:
    def test_youtube_fallback_no_key(self, sess):
        result = trends_mod.fetch_youtube_trends(sess, region="US", max_results=5)
        assert result["platform"] == "youtube"
        assert "videos" in result
        assert len(result["videos"]) <= 5
        assert "warning" in result

    def test_tiktok_fallback_no_key(self, sess):
        result = trends_mod.fetch_tiktok_trends(sess, region="US", max_results=5)
        assert result["platform"] == "tiktok"
        assert "videos" in result
        assert "top_hashtags" in result

    def test_fetch_all_trends(self, sess):
        result = trends_mod.fetch_all_trends(sess)
        assert "youtube" in result
        assert "tiktok" in result
        assert "cross_platform_hashtags" in result

    def test_hashtags_known_niche(self, sess):
        result = trends_mod.get_hashtags_for_niche(sess, "fitness")
        assert result["niche"] == "fitness"
        assert len(result["recommended_mix"]) > 5
        assert any(t.startswith("#") for t in result["recommended_mix"])

    def test_hashtags_unknown_niche(self, sess):
        result = trends_mod.get_hashtags_for_niche(sess, "woodworking")
        assert "niche" in result
        assert len(result["recommended_mix"]) > 0

    def test_trending_music(self, sess):
        result = trends_mod.get_trending_music(sess, "tiktok", "rising")
        assert result["trend_type"] == "rising"
        assert all(t["trend"] == "rising" for t in result["tracks"])

    def test_viral_patterns(self, sess):
        result = trends_mod.analyze_viral_patterns(sess)
        assert "content_formats" in result
        assert "hook_formulas" in result
        assert "posting_windows" in result
        assert len(result["hook_formulas"]) >= 3


# ── Accounts tests ────────────────────────────────────────────────────────────

class TestAccounts:
    def test_add_account(self, sess):
        result = accounts_mod.add_account(sess, "tiktok", "testuser", "fitness")
        assert result["success"] is True
        assert "tiktok_testuser" in sess.config["accounts"]

    def test_add_invalid_platform(self, sess):
        with pytest.raises(ValueError):
            accounts_mod.add_account(sess, "myspace", "testuser", "fitness")

    def test_remove_account(self, sess):
        accounts_mod.add_account(sess, "tiktok", "testuser", "fitness")
        result = accounts_mod.remove_account(sess, "tiktok_testuser")
        assert result["success"] is True
        assert "tiktok_testuser" not in sess.config["accounts"]

    def test_remove_nonexistent(self, sess):
        with pytest.raises(KeyError):
            accounts_mod.remove_account(sess, "nonexistent")

    def test_audit_account_basic(self, sess):
        accounts_mod.add_account(
            sess, "instagram", "mybrand", "finance",
            followers=8500,
            bio="Finance tips daily | DM for coaching",
        )
        result = accounts_mod.audit_account(sess, "instagram_mybrand")
        assert "score" in result
        assert result["score"] <= 100
        assert result["score"] >= 0
        assert "grade" in result
        assert "recommendations" in result

    def test_audit_empty_bio_penalized(self, sess):
        accounts_mod.add_account(sess, "tiktok", "nobio", "travel", followers=0, bio="")
        result = accounts_mod.audit_account(sess, "tiktok_nobio")
        assert result["score"] < 90
        issue_fields = [i["field"] for i in result["issues"]]
        assert "bio" in issue_fields

    def test_optimize_bio(self, sess):
        accounts_mod.add_account(sess, "instagram", "fitpage", "fitness")
        result = accounts_mod.optimize_bio(sess, "instagram_fitpage", "fitness")
        assert "recommended_bio" in result
        assert len(result["recommended_bio"]) > 10
        assert len(result["alternatives"]) >= 4

    def test_list_accounts(self, sess):
        accounts_mod.add_account(sess, "tiktok", "user1", "fitness")
        accounts_mod.add_account(sess, "instagram", "user2", "finance")
        result = accounts_mod.list_accounts(sess)
        assert len(result) == 2

    def test_bulk_audit(self, sess):
        accounts_mod.add_account(sess, "tiktok", "user1", "fitness",
                                  bio="Fitness tips daily | DM me", followers=5000)
        accounts_mod.add_account(sess, "instagram", "user2", "finance",
                                  bio="Finance hacks | Link below", followers=12000)
        result = accounts_mod.bulk_audit(sess)
        assert result["total_accounts"] == 2
        assert "avg_score" in result

    def test_posting_schedule(self, sess):
        accounts_mod.add_account(sess, "tiktok", "sched_user", "fitness")
        result = accounts_mod.get_posting_schedule(sess, "tiktok_sched_user", "aggressive")
        assert result["frequency"] == "aggressive"
        assert "content_calendar_template" in result
        assert len(result["content_calendar_template"]) == 7


# ── Theme Page tests ──────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches(self):
        niches = theme_mod.list_niches()
        assert len(niches) > 3
        for n in niches:
            assert "id" in n
            assert "monetization_potential" in n

    def test_get_niche_detail(self):
        detail = theme_mod.get_niche_detail("fitness_motivation")
        assert detail["display"] == "Fitness Motivation"
        assert "monetization_paths" in detail

    def test_get_niche_detail_invalid(self):
        with pytest.raises(KeyError):
            theme_mod.get_niche_detail("invalid_niche_xyz")

    def test_create_theme_page(self, sess):
        result = theme_mod.create_theme_page(
            sess, "MyFitPage", "fitness_motivation", ["tiktok", "instagram"]
        )
        assert result["success"] is True
        assert "myfitpage" in sess.config["theme_pages"]
        assert "quick_start" in result
        assert len(result["quick_start"]) > 0

    def test_create_theme_page_invalid_niche(self, sess):
        with pytest.raises(KeyError):
            theme_mod.create_theme_page(sess, "Test", "invalid_xyz", ["tiktok"])

    def test_learn_theme_page_basics(self):
        guide = theme_mod.learn_theme_page_basics()
        assert "what_is_a_theme_page" in guide
        assert "the_5_page_types" in guide
        assert "30_day_action_plan" in guide
        assert len(guide["30_day_action_plan"]) >= 6

    def test_conversion_playbook(self, sess):
        result = theme_mod.get_conversion_playbook(sess, "dm_funnel", "fitness")
        assert "steps" in result
        assert "conversion_rate" in result
        assert len(result["niche_specific_tips"]) > 0

    def test_conversion_playbook_invalid(self, sess):
        with pytest.raises(KeyError):
            theme_mod.get_conversion_playbook(sess, "nonexistent_funnel")

    def test_list_funnels(self):
        funnels = theme_mod.list_funnels()
        assert len(funnels) >= 4
        ids = [f["id"] for f in funnels]
        assert "dm_funnel" in ids
        assert "email_list_funnel" in ids
