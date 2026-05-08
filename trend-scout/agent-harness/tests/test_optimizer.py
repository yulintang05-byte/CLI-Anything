"""Tests for account optimizer."""

import pytest
from unittest.mock import patch, MagicMock
from cli_anything.trend_scout.core.optimizer import AccountOptimizer
from cli_anything.trend_scout.core.analyzer import TrendAnalyzer


@pytest.fixture
def optimizer():
    return AccountOptimizer()


class TestTierClassification:
    def test_nano(self, optimizer):
        assert optimizer._tier(0) == "Nano (0-1K)"
        assert optimizer._tier(999) == "Nano (0-1K)"

    def test_micro(self, optimizer):
        assert optimizer._tier(1000) == "Micro (1K-10K)"
        assert optimizer._tier(9999) == "Micro (1K-10K)"

    def test_mid_tier(self, optimizer):
        assert optimizer._tier(10_000) == "Mid-tier (10K-100K)"

    def test_macro(self, optimizer):
        assert optimizer._tier(100_000) == "Macro (100K-1M)"

    def test_mega(self, optimizer):
        assert optimizer._tier(1_000_000) == "Mega (1M+)"


class TestEngagementTargets:
    def test_small_account_high_target(self, optimizer):
        target = optimizer._engagement_target(500)
        assert "5" in target or "15" in target

    def test_mega_account_low_target(self, optimizer):
        target = optimizer._engagement_target(5_000_000)
        assert "0.5" in target or "1.5" in target


class TestProfileFixes:
    def test_youtube_has_extra_fixes(self, optimizer):
        fixes = optimizer._get_profile_fixes("youtube", "gaming")
        elements = [f["element"] for f in fixes]
        assert "Channel Art" in elements or "Channel Trailer" in elements

    def test_instagram_has_story_highlights(self, optimizer):
        fixes = optimizer._get_profile_fixes("instagram", "fashion")
        elements = [f["element"] for f in fixes]
        assert "Story Highlights" in elements

    def test_all_fixes_have_priority(self, optimizer):
        fixes = optimizer._get_profile_fixes("tiktok", "fitness")
        for f in fixes:
            assert "priority" in f
            assert f["priority"] in ("HIGH", "MEDIUM", "LOW")

    def test_all_fixes_have_action(self, optimizer):
        for platform in ("tiktok", "youtube", "instagram"):
            fixes = optimizer._get_profile_fixes(platform, "food")
            for f in fixes:
                assert "action" in f
                assert len(f["action"]) > 0


class TestGrowthRoadmap:
    def test_nano_gets_phase_1(self, optimizer):
        roadmap = optimizer._build_growth_roadmap("tiktok", 0, "fitness")
        phases = [r["phase"] for r in roadmap]
        assert any("Foundation" in p for p in phases)

    def test_large_account_gets_monetize_phase(self, optimizer):
        roadmap = optimizer._build_growth_roadmap("youtube", 200_000, "gaming")
        phases = [r["phase"] for r in roadmap]
        assert any("Monetize" in p for p in phases)

    def test_all_phases_have_tactics(self, optimizer):
        roadmap = optimizer._build_growth_roadmap("tiktok", 0, "fitness")
        for phase in roadmap:
            assert "tactics" in phase
            assert len(phase["tactics"]) > 0


class TestAccountAudit:
    def test_no_bio_is_critical(self, optimizer):
        audit = optimizer._audit_account("tiktok", 100, "fitness", ["no_bio"])
        assert any("bio" in c.lower() or "Bio" in c for c in audit["critical"])

    def test_no_issues_gives_improvements(self, optimizer):
        audit = optimizer._audit_account("tiktok", 5000, "fitness", [])
        assert len(audit["improvements"]) > 0

    def test_has_algorithm_guide(self, optimizer):
        audit = optimizer._audit_account("tiktok", 0, "fitness", [])
        assert "platform_algorithm" in audit
        assert len(audit["platform_algorithm"]) > 0


class TestOptimizeAll:
    def test_all_accounts_get_plans(self, optimizer):
        accounts = [
            {"platform": "tiktok", "username": "test1", "niche": "fitness", "followers": 1000},
            {"platform": "youtube", "username": "test2", "niche": "gaming", "followers": 5000},
        ]
        result = optimizer.optimize_all_accounts(accounts)
        assert "accounts" in result
        assert len(result["accounts"]) == 2

    def test_has_unified_strategy(self, optimizer):
        accounts = [
            {"platform": "tiktok", "username": "x", "niche": "fitness"},
        ]
        result = optimizer.optimize_all_accounts(accounts)
        assert "unified_strategy" in result

    def test_has_repurposing_workflow(self, optimizer):
        accounts = [
            {"platform": "tiktok", "username": "x", "niche": "fitness"},
            {"platform": "instagram", "username": "y", "niche": "fitness"},
        ]
        result = optimizer.optimize_all_accounts(accounts)
        assert "repurposing_workflow" in result
        workflow = result["repurposing_workflow"]
        assert any("TikTok" in step for step in workflow)
        assert any("Instagram" in step for step in workflow)


class TestBioOptimization:
    def test_tiktok_has_character_limit(self, optimizer):
        result = optimizer.get_bio_optimization("tiktok", "fitness")
        assert result["character_limit"] == 80

    def test_youtube_has_longer_limit(self, optimizer):
        result = optimizer.get_bio_optimization("youtube", "gaming")
        assert result["character_limit"] == 1000

    def test_has_examples(self, optimizer):
        for platform in ("tiktok", "youtube", "instagram"):
            result = optimizer.get_bio_optimization(platform, "food")
            assert len(result.get("examples", [])) > 0

    def test_has_cta_options(self, optimizer):
        result = optimizer.get_bio_optimization("tiktok", "fashion")
        assert "cta_options" in result
        assert len(result["cta_options"]) >= 3


class TestUniversalTags:
    def test_always_includes_fyp(self):
        analyzer = TrendAnalyzer()
        tags = analyzer._get_universal_tags("fitness")
        assert "#fyp" in tags

    def test_includes_niche_tags(self):
        analyzer = TrendAnalyzer()
        fitness_tags = analyzer._get_universal_tags("fitness")
        assert any("fitness" in t.lower() or "gym" in t.lower() for t in fitness_tags)

    def test_generic_niche_falls_back(self):
        analyzer = TrendAnalyzer()
        tags = analyzer._get_universal_tags("underwater_knitting")
        assert "#fyp" in tags
        assert any("underwater" in t.lower() for t in tags)
