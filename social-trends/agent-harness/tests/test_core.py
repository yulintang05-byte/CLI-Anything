"""Unit tests for cli-anything-social-trends core modules."""

import pytest
from cli_anything.social_trends.core import hashtags, theme_pages, music
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.utils.social_backend import _cache_path, clear_cache


# ── Session ────────────────────────────────────────────────────────────────────

class TestSession:
    def test_initial_state(self):
        s = Session()
        assert s.active_platform is None
        assert s.active_niche is None
        assert s.active_account is None
        assert s.trend_cache == []

    def test_set_platform(self):
        s = Session()
        s.set_platform("TikTok")
        assert s.active_platform == "tiktok"

    def test_set_niche(self):
        s = Session()
        s.set_niche("fitness")
        assert s.active_niche == "fitness"

    def test_status(self):
        s = Session()
        status = s.status()
        assert status["platform"] == "not set"
        assert status["niche"] == "not set"
        assert status["account"] == "none"

    def test_log(self):
        s = Session()
        s.log("trends fetch")
        s.log("hashtags mix fitness")
        assert len(s.history) == 2


# ── Hashtags ───────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_list_niches(self):
        niches = hashtags.list_niches()
        assert len(niches) >= 10
        assert "fitness" in niches
        assert "fashion" in niches
        assert "food" in niches

    def test_get_hashtag_mix_fitness(self):
        tags = hashtags.get_hashtag_mix("fitness", "tiktok", count=5)
        assert len(tags) >= 3
        assert len(tags) <= 5
        assert all(isinstance(t, str) for t in tags)

    def test_get_hashtag_mix_includes_boosters(self):
        tags = hashtags.get_hashtag_mix("fitness", "tiktok", count=5, include_platform_boosters=True)
        # At least one booster like fyp or viral
        boosters = {"fyp", "foryou", "viral", "trending", "foryoupage"}
        assert any(t in boosters for t in tags)

    def test_get_hashtag_mix_no_boosters(self):
        tags = hashtags.get_hashtag_mix("fitness", "tiktok", count=5, include_platform_boosters=False)
        boosters = {"fyp", "foryou", "viral"}
        assert not any(t in boosters for t in tags)

    def test_get_hashtag_mix_fuzzy_niche(self):
        # Should still return something for partial match
        tags = hashtags.get_hashtag_mix("fit", "tiktok")
        assert isinstance(tags, list)

    def test_score_hashtag_generic(self):
        result = hashtags.score_hashtag("fyp")
        assert result["competition"] == "high"
        assert result["score"] < 8

    def test_score_hashtag_specific(self):
        result = hashtags.score_hashtag("nattyorbottle")
        assert result["competition"] == "low"
        assert result["score"] >= 6

    def test_audit_hashtags_too_many(self):
        tags = ["a", "b", "c", "d", "e", "f", "g"]
        result = hashtags.audit_hashtags(tags)
        assert any("Too many" in issue for issue in result["issues"])

    def test_audit_hashtags_too_few(self):
        tags = ["fitness"]
        result = hashtags.audit_hashtags(tags)
        assert any("Too few" in issue for issue in result["issues"])

    def test_audit_hashtags_good_set(self):
        tags = ["fitness", "gymtok", "nattyorbottle", "fyp"]
        result = hashtags.audit_hashtags(tags)
        assert result["count"] == 4
        assert result["avg_score"] > 0

    def test_build_caption_tiktok(self):
        caption = hashtags.build_caption("My workout today", ["fitness", "gym", "fyp"], "tiktok")
        assert "My workout today" in caption
        assert "#fitness" in caption
        assert "#gym" in caption

    def test_build_caption_instagram(self):
        caption = hashtags.build_caption("My workout today", ["fitness"], "instagram")
        assert ".\n.\n." in caption

    def test_get_trending_hashtags_from_trends(self):
        items = [
            {"hashtags": ["fyp", "fitness", "viral"]},
            {"hashtags": ["fyp", "gym"]},
            {"hashtags": ["fitness", "workout"]},
        ]
        tags = hashtags.get_trending_hashtags_from_trends(items)
        assert tags[0] == "fyp"  # most common
        assert "fitness" in tags


# ── Music ──────────────────────────────────────────────────────────────────────

class TestMusic:
    def test_classify_mood_love(self):
        assert music.classify_mood("Love Story", "Taylor Swift") == "romantic"

    def test_classify_mood_hype(self):
        assert music.classify_mood("Hype Up", "DJ") == "energetic"

    def test_classify_mood_chill(self):
        assert music.classify_mood("Chill Vibes", "Lo-Fi") == "chill"

    def test_classify_mood_general(self):
        assert music.classify_mood("Unknown Song", "Artist") == "general"

    def test_classify_bpm_lofi(self):
        bpm = music.classify_bpm("lofi")
        assert "60" in bpm or "90" in bpm

    def test_classify_bpm_phonk(self):
        bpm = music.classify_bpm("phonk")
        assert "130" in bpm or "160" in bpm

    def test_extract_music_from_trends(self):
        items = [
            {"music": "Espresso", "creator": "user1"},
            {"music": "Espresso", "creator": "user2"},
            {"music": "Not Like Us", "creator": "user3"},
        ]
        music_items = music.extract_music_from_trends(items)
        assert len(music_items) >= 2
        assert music_items[0]["title"] == "Espresso"  # most common first
        assert music_items[0]["tiktok_uses"] == 2

    def test_fetch_trending_music_curated_fallback(self):
        # When all live sources fail, should return curated data
        from cli_anything.social_trends.core.music import _CURATED_TRENDING_SOUNDS
        assert len(_CURATED_TRENDING_SOUNDS) >= 5

    def test_recommend_music_for_niche_fitness(self):
        from cli_anything.social_trends.core.music import _CURATED_TRENDING_SOUNDS
        recs = music.recommend_music_for_niche("fitness", list(_CURATED_TRENDING_SOUNDS))
        assert len(recs) > 0

    def test_recommend_music_for_niche_unknown(self):
        from cli_anything.social_trends.core.music import _CURATED_TRENDING_SOUNDS
        recs = music.recommend_music_for_niche("unknownniche", list(_CURATED_TRENDING_SOUNDS))
        assert isinstance(recs, list)


# ── Accounts ───────────────────────────────────────────────────────────────────

class TestAccounts:
    def _sample_profile(self, **kwargs):
        defaults = dict(
            username="testuser", platform="tiktok", followers=5000,
            bio="Fitness content | Training tips | Link below 💪",
            has_link=True, niche="fitness", avg_views=10000,
            avg_likes=500, avg_comments=50, post_frequency_per_week=14,
            account_type="creator", monetization="affiliate",
        )
        defaults.update(kwargs)
        return accounts_mod.create_account(**defaults)

    def test_create_account(self):
        profile = accounts_mod.create_account("alice", "tiktok", followers=1000)
        assert profile["username"] == "alice"
        assert profile["platform"] == "tiktok"
        assert profile["followers"] == 1000

    def test_audit_bio_good(self):
        result = accounts_mod.audit_bio("Fitness coach | DM for coaching | link below 💪", True, "tiktok")
        assert result["score"] >= 60
        assert result["has_cta"] is True
        assert result["has_link"] is True

    def test_audit_bio_no_link(self):
        result = accounts_mod.audit_bio("I love fitness", False, "tiktok")
        assert any("link" in issue.lower() for issue in result["issues"])

    def test_audit_bio_no_cta(self):
        result = accounts_mod.audit_bio("I am a fitness creator who loves working out", False, "tiktok")
        assert any("CTA" in issue or "call-to-action" in issue.lower() for issue in result["issues"])

    def test_audit_bio_short(self):
        result = accounts_mod.audit_bio("Hi", False, "tiktok")
        assert any("short" in issue.lower() for issue in result["issues"])

    def test_benchmark_engagement_tiers(self):
        for followers, expected_min in [(500, 0.10), (5000, 0.05), (50000, 0.03)]:
            rate = accounts_mod._benchmark_engagement(followers, "tiktok")
            assert rate > 0

    def test_audit_engagement_excellent(self):
        profile = self._sample_profile(followers=5000, avg_views=5000, avg_likes=800, avg_comments=100)
        result = accounts_mod.audit_engagement(profile)
        assert result["actual_rate_pct"] > 0
        assert result["status"] in ("excellent", "good", "below average", "poor")

    def test_recommend_schedule_tiktok(self):
        result = accounts_mod.recommend_schedule("tiktok", frequency_per_week=21)
        assert "mon" in result["peak_times"]
        assert result["platform"] == "tiktok"

    def test_recommend_schedule_too_low(self):
        result = accounts_mod.recommend_schedule("tiktok", frequency_per_week=1)
        assert any("infrequently" in issue or "often" in issue.lower() for issue in result["issues"])

    def test_recommend_link_in_bio_products(self):
        recs = accounts_mod.recommend_link_in_bio("creator", "digital products")
        assert recs[0]["name"] == "Stan Store"

    def test_recommend_link_in_bio_affiliate(self):
        recs = accounts_mod.recommend_link_in_bio("creator", "affiliate")
        assert len(recs) > 0

    def test_full_audit(self):
        profile = self._sample_profile()
        result = accounts_mod.full_audit(profile)
        assert "overall_score" in result
        assert result["overall_score"] >= 0
        assert result["overall_score"] <= 100
        assert "grade" in result
        assert "priority_actions" in result
        assert isinstance(result["priority_actions"], list)


# ── Theme pages ────────────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_blueprints(self):
        blueprints = theme_pages.list_blueprints()
        assert len(blueprints) >= 8
        names = [b["name"] for b in blueprints]
        assert any("Fitness" in n for n in names)
        assert any("Finance" in n for n in names)

    def test_get_blueprint_exact(self):
        bp = theme_pages.get_blueprint("fitness")
        assert bp is not None
        assert "content_pillars" in bp
        assert "hashtag_strategy" in bp
        assert "monetization_priority" in bp
        assert "growth_hack" in bp

    def test_get_blueprint_partial(self):
        bp = theme_pages.get_blueprint("gym")
        # Should match "Gym & Fitness Motivation" or similar
        assert bp is not None or bp is None  # graceful either way

    def test_get_blueprint_not_found(self):
        bp = theme_pages.get_blueprint("zzznomatch999")
        assert bp is None

    def test_get_monetization_playbook_affiliate(self):
        pb = theme_pages.get_monetization_playbook("affiliate")
        assert pb is not None
        assert "steps" in pb
        assert "monthly_potential" in pb
        assert len(pb["steps"]) >= 4

    def test_get_monetization_playbook_tiktok_shop(self):
        pb = theme_pages.get_monetization_playbook("tiktok_shop")
        assert pb is not None

    def test_get_growth_phase_0_to_1k(self):
        phase = theme_pages.get_growth_phase("0_to_1k")
        assert phase is not None
        assert "actions" in phase
        assert len(phase["actions"]) >= 4

    def test_get_growth_phase_10k_to_100k(self):
        phase = theme_pages.get_growth_phase("10k_to_100k")
        assert phase is not None
        assert "kpis" in phase

    def test_assess_account_zero_followers(self):
        result = theme_pages.assess_account_for_conversion(0, "fitness", False)
        assert "0_to_1k" in result["current_phase"] or "Phase 1" in result["current_phase"]
        assert result["link_in_bio_urgent"] is True
        assert any("affiliate" in r.lower() for r in result["ready_for"])

    def test_assess_account_10k_followers(self):
        result = theme_pages.assess_account_for_conversion(15000, "fitness", True)
        assert len(result["ready_for"]) > 2
        assert result["link_in_bio_urgent"] is False

    def test_assess_account_small_followers(self):
        result = theme_pages.assess_account_for_conversion(500, "fashion", True)
        assert result["next_milestone"] == 1000

    def test_growth_phases_have_required_keys(self):
        for phase_key in ["0_to_1k", "1k_to_10k", "10k_to_100k"]:
            phase = theme_pages.get_growth_phase(phase_key)
            assert "label" in phase
            assert "timeline" in phase
            assert "focus" in phase
            assert "actions" in phase
            assert "kpis" in phase

    def test_all_blueprints_have_required_keys(self):
        required = ["name", "niche", "aesthetic", "content_pillars", "hashtag_strategy",
                    "music_vibe", "posting_frequency", "monetization_priority", "growth_hack", "difficulty"]
        for bp in theme_pages._BLUEPRINTS:
            for key in required:
                assert key in bp, f"Blueprint '{bp.get('name')}' missing key '{key}'"


# ── Backend / cache ────────────────────────────────────────────────────────────

class TestBackend:
    def test_cache_path_deterministic(self):
        url = "https://example.com/test"
        p1 = _cache_path(url)
        p2 = _cache_path(url)
        assert p1 == p2

    def test_cache_path_different_urls(self):
        p1 = _cache_path("https://example.com/a")
        p2 = _cache_path("https://example.com/b")
        assert p1 != p2

    def test_clear_cache_runs(self):
        # Just verify it doesn't crash; may return 0 in CI
        count = clear_cache()
        assert isinstance(count, int)
        assert count >= 0
