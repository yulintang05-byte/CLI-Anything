"""Core unit tests for socialtrends module.

Tests all non-network functions — no API keys required.
"""

import pytest

# ── hashtag_analyzer tests ────────────────────────────────────────────────────

class TestHashtagAnalyzer:
    def test_list_niches(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import list_niches
        niches = list_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 10
        assert "fitness" in niches
        assert "food" in niches

    def test_suggest_hashtags_returns_tags(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags
        result = suggest_hashtags(niche="fitness", platform="tiktok", count=30)
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0
        assert all(h.startswith("#") for h in result["hashtags"])

    def test_suggest_hashtags_includes_boost(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags, PLATFORM_BOOST
        result = suggest_hashtags(niche="fitness", platform="tiktok", include_boost=True)
        boost = PLATFORM_BOOST["tiktok"]
        found = any(b in result["hashtags"] for b in boost)
        assert found, "Platform boost tags should be included"

    def test_suggest_hashtags_no_boost(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags, PLATFORM_BOOST
        result = suggest_hashtags(niche="fitness", platform="tiktok", include_boost=False)
        boost = PLATFORM_BOOST["tiktok"]
        for b in boost:
            assert b not in result["hashtags"], f"Boost tag {b} should not be included"

    def test_suggest_hashtags_unknown_niche(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags
        result = suggest_hashtags(niche="xyznonsense123", platform="tiktok")
        assert "error" in result
        assert "available_niches" in result

    def test_suggest_hashtags_count_respected(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags
        result = suggest_hashtags(niche="food", platform="instagram", count=15)
        assert len(result["hashtags"]) <= 15

    def test_score_hashtag_known(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import score_hashtag
        result = score_hashtag("#fitness")
        assert "score" in result
        assert 0 <= result["score"] <= 100
        assert result["tier"] in ("mega", "large", "medium", "niche", "unknown")

    def test_score_hashtag_no_prefix(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import score_hashtag
        result = score_hashtag("gym")
        assert result["hashtag"] == "#gym"

    def test_analyze_hashtag_set(self):
        from cli_anything.socialtrends.core.hashtag_analyzer import analyze_hashtag_set
        tags = ["#fitness", "#gym", "#fyp", "#homeworkout", "#girlswholift"]
        result = analyze_hashtag_set(tags)
        assert "total" in result
        assert result["total"] == len(tags)
        assert "avg_score" in result
        assert "tier_breakdown" in result


# ── account_optimizer tests ───────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_get_platform_spec(self):
        from cli_anything.socialtrends.core.account_optimizer import get_platform_spec
        spec = get_platform_spec("tiktok")
        assert spec["platform"] == "tiktok"
        assert "bio_limit" in spec
        assert "best_post_times_et" in spec

    def test_get_platform_spec_unknown(self):
        from cli_anything.socialtrends.core.account_optimizer import get_platform_spec
        result = get_platform_spec("myspace")
        assert "error" in result

    def test_generate_bio_tiktok(self):
        from cli_anything.socialtrends.core.account_optimizer import generate_bio
        result = generate_bio("tiktok", "fitness", "Alex", cta="Get my free plan")
        assert "bio_template" in result
        assert "char_count" in result
        assert result["char_count"] > 0

    def test_generate_bio_instagram(self):
        from cli_anything.socialtrends.core.account_optimizer import generate_bio
        result = generate_bio("instagram", "food", "Chef Maria")
        assert len(result["bio_template"]) > 0
        assert result["limit"] == 150

    def test_get_posting_schedule(self):
        from cli_anything.socialtrends.core.account_optimizer import get_posting_schedule
        result = get_posting_schedule("tiktok", timezone="PT", posts_per_week=7)
        assert "schedule" in result
        assert len(result["schedule"]) == 7
        for day_entry in result["schedule"]:
            assert "day" in day_entry
            assert "post_at" in day_entry

    def test_generate_caption_hook(self):
        from cli_anything.socialtrends.core.account_optimizer import generate_caption
        result = generate_caption(topic="how to lose belly fat", niche="fitness")
        assert "caption" in result
        assert len(result["caption"]) > 20
        assert "formula_used" in result

    def test_generate_caption_with_hashtags(self):
        from cli_anything.socialtrends.core.account_optimizer import generate_caption
        tags = ["#fitness", "#gym", "#fyp"]
        result = generate_caption("workout tips", "fitness", include_hashtags=True, hashtags=tags)
        assert "#fitness" in result["caption"]

    def test_calculate_engagement_rate(self):
        from cli_anything.socialtrends.core.account_optimizer import calculate_engagement_rate
        result = calculate_engagement_rate(10000, 500, 50, shares=20, saves=80)
        assert "engagement_rate_percent" in result
        assert result["engagement_rate_percent"] > 0
        assert "rating" in result

    def test_engagement_rate_zero_followers(self):
        from cli_anything.socialtrends.core.account_optimizer import calculate_engagement_rate
        result = calculate_engagement_rate(0, 100, 10)
        assert result["engagement_rate_percent"] == 0

    def test_full_account_audit(self):
        from cli_anything.socialtrends.core.account_optimizer import full_account_audit
        result = full_account_audit(
            platform="tiktok", niche="fitness", followers=25000,
            avg_likes=1200, avg_comments=80, posts_per_week=5,
        )
        assert "overall_score" in result
        assert 0 <= result["overall_score"] <= 100
        assert "priority_actions" in result
        assert "algorithm_signals" in result


# ── theme_pages tests ─────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches(self):
        from cli_anything.socialtrends.core.theme_pages import list_niches
        niches = list_niches()
        assert isinstance(niches, list)
        assert len(niches) >= 5
        assert all("name" in n for n in niches)

    def test_get_niche_known(self):
        from cli_anything.socialtrends.core.theme_pages import get_niche
        result = get_niche("luxury")
        assert result["slug"] == "luxury"
        assert "monetization_potential" in result
        assert "content_types" in result

    def test_get_niche_unknown(self):
        from cli_anything.socialtrends.core.theme_pages import get_niche
        result = get_niche("nonexistentniche")
        assert "error" in result

    def test_list_conversion_strategies(self):
        from cli_anything.socialtrends.core.theme_pages import list_conversion_strategies
        strategies = list_conversion_strategies()
        assert len(strategies) >= 4
        assert all("slug" in s for s in strategies)

    def test_get_conversion_strategy_known(self):
        from cli_anything.socialtrends.core.theme_pages import get_conversion_strategy
        result = get_conversion_strategy("email_list_building")
        assert "steps" in result
        assert len(result["steps"]) >= 3

    def test_get_conversion_strategy_unknown(self):
        from cli_anything.socialtrends.core.theme_pages import get_conversion_strategy
        result = get_conversion_strategy("nonsense")
        assert "error" in result

    def test_get_content_sourcing_all(self):
        from cli_anything.socialtrends.core.theme_pages import get_content_sourcing_guide
        result = get_content_sourcing_guide()
        assert "repost_with_credit" in result
        assert "original_content" in result

    def test_get_growth_playbook(self):
        from cli_anything.socialtrends.core.theme_pages import get_growth_playbook
        playbook = get_growth_playbook("0_to_10k")
        assert isinstance(playbook, list)
        assert len(playbook) > 0
        assert "actions" in playbook[0]

    def test_monetization_timeline_low_followers(self):
        from cli_anything.socialtrends.core.theme_pages import get_monetization_timeline
        result = get_monetization_timeline("fitness", followers=500)
        assert "revenue_estimates" in result
        assert "next_milestone_actions" in result

    def test_monetization_timeline_high_followers(self):
        from cli_anything.socialtrends.core.theme_pages import get_monetization_timeline
        result = get_monetization_timeline("finance", followers=500000)
        assert "revenue_estimates" in result
        assert "speaking_consulting" in result["revenue_estimates"]


# ── music_trends tests ────────────────────────────────────────────────────────

class TestMusicTrends:
    def test_get_music_recommendations(self):
        from cli_anything.socialtrends.core.music_trends import get_music_recommendations
        result = get_music_recommendations("fitness")
        assert "recommended_moods" in result
        assert "evergreen_tiktok_sounds" in result
        assert "where_to_find_trending_sounds" in result

    def test_get_music_recommendations_unknown_niche(self):
        from cli_anything.socialtrends.core.music_trends import get_music_recommendations
        result = get_music_recommendations("unknownniche")
        assert "recommended_moods" in result

    def test_get_evergreen_sounds(self):
        from cli_anything.socialtrends.core.music_trends import get_evergreen_sounds
        sounds = get_evergreen_sounds()
        assert len(sounds) >= 5
        assert all("name" in s for s in sounds)
        assert all("artist" in s for s in sounds)

    def test_spotify_fallback(self):
        from cli_anything.socialtrends.core.music_trends import _spotify_fallback_charts
        charts = _spotify_fallback_charts("US")
        assert len(charts) >= 5
        assert all("rank" in c for c in charts)
        assert all("artist" in c for c in charts)


# ── tiktok_trends tests ───────────────────────────────────────────────────────

class TestTikTokTrends:
    def test_curated_trending(self):
        from cli_anything.socialtrends.core.tiktok_trends import get_curated_trending
        result = get_curated_trending(region="US")
        assert "mega_viral" in result
        assert isinstance(result["mega_viral"], list)
        assert "#fyp" in result["mega_viral"]

    def test_extract_trending_hashtags(self):
        from cli_anything.socialtrends.core.tiktok_trends import extract_trending_hashtags
        videos = [
            {"hashtags": ["#fitness", "#gym", "#fyp"], "likes": 100, "comments": 10, "shares": 5},
            {"hashtags": ["#fitness", "#workout"],     "likes": 200, "comments": 20, "shares": 10},
        ]
        result = extract_trending_hashtags(videos, top_n=10)
        assert len(result) > 0
        tags = [r["hashtag"] for r in result]
        assert "#fitness" in tags
        # fitness appears in both videos, should rank high
        fitness_entry = next(r for r in result if r["hashtag"] == "#fitness")
        assert fitness_entry["count"] == 2


# ── cache tests ───────────────────────────────────────────────────────────────

class TestCache:
    def test_set_and_get(self, tmp_path, monkeypatch):
        from cli_anything.socialtrends.utils import cache as c
        monkeypatch.setattr(c, "CACHE_DIR", tmp_path)
        c.set_cached("test_key", {"data": 42}, ttl_hours=1)
        result = c.get_cached("test_key")
        assert result == {"data": 42}

    def test_expired_returns_none(self, tmp_path, monkeypatch):
        import time
        from cli_anything.socialtrends.utils import cache as c
        monkeypatch.setattr(c, "CACHE_DIR", tmp_path)
        c.set_cached("expired_key", {"data": "old"}, ttl_hours=0.000001)
        time.sleep(0.01)
        result = c.get_cached("expired_key")
        assert result is None

    def test_clear_cache(self, tmp_path, monkeypatch):
        from cli_anything.socialtrends.utils import cache as c
        monkeypatch.setattr(c, "CACHE_DIR", tmp_path)
        c.set_cached("k1", "v1")
        c.set_cached("k2", "v2")
        count = c.clear_cache()
        assert count == 2


# ── config tests ──────────────────────────────────────────────────────────────

class TestConfig:
    def test_save_and_load(self, tmp_path, monkeypatch):
        from cli_anything.socialtrends.utils import config as cfg
        monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config.json")
        cfg.save_config({"youtube_api_key": "test123"})
        loaded = cfg.load_config()
        assert loaded["youtube_api_key"] == "test123"

    def test_get_missing_key(self, tmp_path, monkeypatch):
        from cli_anything.socialtrends.utils import config as cfg
        monkeypatch.setattr(cfg, "CONFIG_DIR", tmp_path)
        monkeypatch.setattr(cfg, "CONFIG_FILE", tmp_path / "config.json")
        assert cfg.get("nonexistent") is None
        assert cfg.get("nonexistent", "default") == "default"
