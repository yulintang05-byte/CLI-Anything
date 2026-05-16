"""Unit tests for social media CLI core modules."""

import pytest
from cli_anything.social_media.core import account_optimizer as ao
from cli_anything.social_media.core import theme_pages as tp
from cli_anything.social_media.core import account_manager as am


class TestAccountOptimizer:
    def test_detect_niche_fitness(self):
        result = ao.detect_niche("daily gym workout gains muscle cardio")
        assert result["niche"] == "fitness"
        assert result["confidence"] in ("high", "medium")

    def test_detect_niche_finance(self):
        result = ao.detect_niche("investing crypto passive income wealth")
        assert result["niche"] == "finance"

    def test_detect_niche_unknown(self):
        result = ao.detect_niche("hello world")
        assert result["niche"] == "general"

    def test_analyze_bio_short(self):
        result = ao.analyze_bio("hi")
        assert result["bio_score"] < 70
        assert any("short" in i.lower() for i in result["issues"])

    def test_analyze_bio_good(self):
        result = ao.analyze_bio("💪 Daily fitness tips | Helping you build your dream body\n👇 Free workout plan in bio")
        assert result["bio_score"] >= 70

    def test_optimize_posting_schedule(self):
        result = ao.optimize_posting_schedule("tiktok")
        assert "schedule" in result
        assert "best_times" in result["schedule"]

    def test_optimize_posting_schedule_unknown(self):
        result = ao.optimize_posting_schedule("myspace")
        assert "error" in result

    def test_hashtag_strategy(self):
        result = ao.hashtag_strategy("fitness", "tiktok")
        assert "recommended_mix" in result
        assert len(result["recommended_mix"]) <= 5  # TikTok limit

    def test_full_audit(self):
        result = ao.full_account_audit(
            handle="testuser", bio="💪 Fitness tips | Build muscle fast 👇",
            platform="tiktok", niche="fitness", followers=1000,
            avg_views=5000, avg_likes=250
        )
        assert "bio_analysis" in result
        assert "hashtag_strategy" in result
        assert "priority_actions" in result
        assert result["audit"]["engagement_rate_pct"] == pytest.approx(5.0)


class TestThemePages:
    def test_list_niches(self):
        result = tp.list_niches()
        assert "available_niches" in result
        assert len(result["available_niches"]) >= 5

    def test_get_niche_playbook_exists(self):
        result = tp.get_niche_playbook("motivation_luxury")
        assert "monetization" in result
        assert "conversion_playbook" in result

    def test_get_niche_playbook_missing(self):
        result = tp.get_niche_playbook("doesnotexist_xyz")
        assert "error" in result

    def test_full_guide_structure(self):
        result = tp.full_theme_page_guide()
        assert "niches" in result
        assert "monetization_roadmap" in result
        assert "tools_stack" in result
        assert "quick_start_steps" in result
        assert len(result["quick_start_steps"]) >= 10


class TestAccountManager:
    def test_add_and_list(self, tmp_path, monkeypatch):
        monkeypatch.setattr(am, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(am, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        am.add_account("testuser", "tiktok", "fitness", "bio here", 1000)
        result = am.list_accounts()
        assert result["total_accounts"] == 1
        assert result["accounts"][0]["handle"] == "testuser"

    def test_remove_account(self, tmp_path, monkeypatch):
        monkeypatch.setattr(am, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(am, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        am.add_account("testuser", "tiktok")
        result = am.remove_account("testuser", "tiktok")
        assert result["status"] == "removed"
        assert am.list_accounts()["total_accounts"] == 0

    def test_update_metrics(self, tmp_path, monkeypatch):
        monkeypatch.setattr(am, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(am, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        am.add_account("testuser", "youtube", followers=500)
        result = am.update_metrics("testuser", "youtube", followers=750)
        assert result["status"] == "updated"
        assert result["snapshot"]["followers"] == 750

    def test_get_account_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(am, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(am, "ACCOUNTS_FILE", tmp_path / "accounts.json")
        result = am.get_account("nobody", "tiktok")
        assert "error" in result
