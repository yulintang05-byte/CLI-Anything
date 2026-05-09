"""Unit tests for social-trends core modules."""

import pytest
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import account as account_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import theme_page as theme_mod
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core.session import Session


# ── Hashtags ──────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_generate_tiktok_set_returns_hashtags(self):
        result = hashtags_mod.generate_hashtag_set("fitness", platform="tiktok")
        assert result["hashtags"]
        assert result["count"] > 0
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"

    def test_generate_instagram_set_has_more_tags_than_tiktok(self):
        tiktok = hashtags_mod.generate_hashtag_set("fitness", platform="tiktok")
        ig = hashtags_mod.generate_hashtag_set("fitness", platform="instagram")
        assert ig["count"] >= tiktok["count"]

    def test_caption_ready_contains_all_hashtags(self):
        result = hashtags_mod.generate_hashtag_set("food", platform="instagram")
        for tag in result["hashtags"]:
            assert tag in result["caption_ready"]

    def test_custom_tags_appended(self):
        result = hashtags_mod.generate_hashtag_set(
            "fitness", custom_tags=["myuniquetag", "#myothertag"]
        )
        tag_lower = [t.lower() for t in result["hashtags"]]
        assert "#myuniquetag" in tag_lower or "#myothertag" in tag_lower

    def test_all_hashtags_start_with_hash(self):
        result = hashtags_mod.generate_hashtag_set("finance", platform="tiktok")
        for tag in result["hashtags"]:
            assert tag.startswith("#"), f"{tag} does not start with #"

    def test_analyse_known_hashtag(self):
        result = hashtags_mod.analyse_hashtag("#fitness")
        assert result["tier"] in ("mega", "large", "niche")
        assert "advice" in result

    def test_analyse_unknown_hashtag(self):
        result = hashtags_mod.analyse_hashtag("#xyzveryuniquetag")
        assert result["tier"] == "unknown"

    def test_generate_multiple_sets(self):
        sets = hashtags_mod.generate_multiple_sets("beauty", platform="instagram", num_sets=3)
        assert len(sets) == 3
        for s in sets:
            assert "hashtags" in s
            assert "caption_ready" in s

    def test_hashtag_calendar_returns_days(self):
        cal = hashtags_mod.hashtag_calendar("food", platform="tiktok", days=7)
        assert len(cal) == 7
        for day in cal:
            assert "date" in day
            assert "hashtags" in day

    def test_unknown_niche_falls_back_to_general(self):
        result = hashtags_mod.generate_hashtag_set("nonexistentniche123", platform="tiktok")
        assert result["hashtags"]

    @pytest.mark.parametrize("niche", ["fitness", "food", "fashion", "beauty", "finance", "travel", "gaming"])
    def test_all_niches_produce_tags(self, niche):
        result = hashtags_mod.generate_hashtag_set(niche)
        assert result["count"] > 0

    @pytest.mark.parametrize("platform", ["tiktok", "instagram", "youtube", "reels"])
    def test_all_platforms_produce_tags(self, platform):
        result = hashtags_mod.generate_hashtag_set("fitness", platform=platform)
        assert result["count"] > 0


# ── Account ───────────────────────────────────────────────────────────────────

class TestAccount:
    def test_optimisation_report_structure(self):
        report = account_mod.generate_optimisation_report("tiktok", "fitness", handle="testuser", followers=5000)
        assert "bio_template" in report
        assert "content_pillars" in report
        assert "posting_schedule" in report
        assert "engagement_benchmarks" in report
        assert "profile_checklist" in report
        assert "growth_tactics" in report
        assert "monetisation_roadmap" in report

    def test_engagement_benchmarks_tiktok(self):
        result = account_mod.get_engagement_benchmarks("tiktok")
        assert "nano (1K–10K)" in result

    def test_engagement_benchmarks_instagram(self):
        result = account_mod.get_engagement_benchmarks("instagram")
        assert "micro (10K–50K)" in result

    def test_engagement_benchmarks_unknown_platform(self):
        result = account_mod.get_engagement_benchmarks("myspace")
        assert "note" in result

    def test_calculate_engagement_rate(self):
        result = account_mod.calculate_engagement_rate(
            likes=1000, comments=50, shares=25, views=20000, followers=5000
        )
        assert "engagement_rate_by_views" in result
        assert "engagement_rate_by_followers" in result
        assert "interpretation" in result

    def test_calculate_engagement_zero_views(self):
        result = account_mod.calculate_engagement_rate(100, 5, 2, 0, 1000)
        assert result["engagement_rate_by_views"] == "0.0%"

    def test_diagnose_growth_issues_known(self):
        result = account_mod.diagnose_growth_issues(["high views but low followers"])
        assert len(result) > 0
        assert "fix" in result[0]

    def test_diagnose_growth_issues_unknown(self):
        result = account_mod.diagnose_growth_issues(["xyzzy strange issue"])
        assert len(result) > 0

    def test_list_diagnostics(self):
        diag = account_mod.list_all_diagnostics()
        assert len(diag) >= 5
        for d in diag:
            assert "symptom" in d
            assert "cause" in d
            assert "fix" in d

    def test_content_pillars_all_niches(self):
        for niche in ["fitness", "food", "finance", "general"]:
            pillars = account_mod._CONTENT_PILLARS.get(niche, [])
            assert len(pillars) >= 4
            total_pct = sum(p["percentage"] for p in pillars)
            assert total_pct == 100

    def test_profile_checklist_tiktok(self):
        checklist = account_mod._profile_checklist("tiktok")
        items = [c["item"] for c in checklist]
        assert "Profile photo" in items

    def test_profile_checklist_youtube(self):
        checklist = account_mod._profile_checklist("youtube")
        items = [c["item"] for c in checklist]
        assert "Channel art/banner" in items

    def test_monetisation_roadmap_stages(self):
        roadmap = account_mod._monetisation_roadmap(1000, "fitness")
        stages = [r["stage"] for r in roadmap]
        assert "0–1K followers" in stages
        assert "100K+ followers" in stages


# ── Music ─────────────────────────────────────────────────────────────────────

class TestMusic:
    def test_trending_sounds_tiktok(self):
        result = music_mod.get_trending_sounds("fitness", "tiktok")
        assert result["platform"] == "tiktok"
        assert "royalty_free_sources" in result

    def test_trending_sounds_youtube(self):
        result = music_mod.get_trending_sounds("food", "youtube")
        assert result["platform"] == "youtube"
        assert "audio_strategy" in result

    def test_audio_strategy_known(self):
        result = music_mod.get_audio_strategy("tutorial")
        assert "strategy" in result
        assert "bpm_range" in result["strategy"]

    def test_audio_strategy_unknown_falls_back(self):
        result = music_mod.get_audio_strategy("unknowncontenttype")
        assert "strategy" in result
        assert "note" in result

    def test_royalty_free_sources_not_empty(self):
        sources = music_mod.list_royalty_free_sources()
        assert len(sources) >= 5
        for s in sources:
            assert "name" in s
            assert "url" in s
            assert "cost" in s

    def test_archetypes_for_niche(self):
        result = music_mod.analyse_trending_archetypes("fitness")
        assert len(result) > 0
        assert "name" in result[0]
        assert "engagement_boost" in result[0]


# ── Theme Page ────────────────────────────────────────────────────────────────

class TestThemePage:
    def test_niche_recommendations_default(self):
        result = theme_mod.get_niche_recommendations()
        assert len(result) > 0
        for n in result:
            assert n["growth_speed"] >= 7
            assert n["monetisation"] >= 7

    def test_niche_recommendations_high_threshold(self):
        result = theme_mod.get_niche_recommendations(min_growth=9, min_monetisation=9)
        for n in result:
            assert n["growth_speed"] >= 9
            assert n["monetisation"] >= 9

    def test_get_niche_details_fitness(self):
        result = theme_mod.get_niche_details("fitness")
        assert result is not None
        assert "sub_niches" in result
        assert "monetisation_methods" in result

    def test_get_niche_details_not_found(self):
        result = theme_mod.get_niche_details("quantumphysics123")
        assert result is None

    def test_score_niche_fitness(self):
        result = theme_mod.score_niche("fitness")
        assert "overall_score" in result
        assert "verdict" in result
        assert 0 <= result["overall_score"] <= 10

    def test_score_niche_not_found(self):
        result = theme_mod.score_niche("doesnotexist999")
        assert "error" in result

    def test_launch_playbook_has_six_phases(self):
        playbook = theme_mod.get_launch_playbook()
        assert len(playbook) == 6
        for phase in playbook:
            assert "phase" in phase
            assert "actions" in phase
            assert "deliverable" in phase

    def test_conversion_strategy_ordered(self):
        strategy = theme_mod.get_conversion_strategy()
        assert len(strategy) >= 5
        for step in strategy:
            assert "step" in step
            assert "how" in step
            assert "why" in step

    def test_ethical_guidelines_not_empty(self):
        guidelines = theme_mod.get_ethical_guidelines()
        assert len(guidelines) >= 5
        for g in guidelines:
            assert isinstance(g, str)
            assert len(g) > 10

    def test_content_plan_returns_days(self):
        plan = theme_mod.generate_content_plan("fitness", platform="tiktok", days=7)
        assert len(plan) == 7
        for day in plan:
            assert "date" in day
            assert "posts" in day

    def test_content_plan_unknown_niche(self):
        plan = theme_mod.generate_content_plan("xyzniche", platform="tiktok", days=3)
        assert "error" in plan[0]


# ── Trends ────────────────────────────────────────────────────────────────────

class TestTrends:
    def test_fetch_tiktok_returns_structure(self):
        result = trends_mod.fetch_platform_trends("tiktok", niche="fitness", region="US")
        assert result["platform"] == "tiktok"
        assert "trending_hashtags" in result
        assert "trending_sounds" in result

    def test_fetch_unknown_platform(self):
        result = trends_mod.fetch_platform_trends("myspace", niche="fitness")
        assert "error" in result

    def test_best_posting_times_known_niche(self):
        times = trends_mod._best_posting_times("fitness")
        assert len(times) >= 2

    def test_best_posting_times_unknown_niche(self):
        times = trends_mod._best_posting_times("quantumphysics")
        assert len(times) >= 2

    def test_cross_platform_insights(self):
        insights = trends_mod._cross_platform_insights({}, {}, "fitness")
        assert len(insights) >= 3


# ── Session ───────────────────────────────────────────────────────────────────

class TestSession:
    def test_add_and_retrieve_account(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        sess.add_account("tiktok", "testuser", niche="fitness")
        acc = sess.get_account("tiktok", "testuser")
        assert acc is not None
        assert acc["niche"] == "fitness"
        assert acc["platform"] == "tiktok"

    def test_list_accounts(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        sess.add_account("tiktok", "user1", niche="food")
        sess.add_account("instagram", "user2", niche="fashion")
        accounts = sess.list_accounts()
        assert len(accounts) == 2

    def test_remove_account(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        sess.add_account("tiktok", "testuser", niche="fitness")
        removed = sess.remove_account("tiktok", "testuser")
        assert removed is True
        assert sess.get_account("tiktok", "testuser") is None

    def test_remove_nonexistent_account(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        removed = sess.remove_account("tiktok", "ghost")
        assert removed is False

    def test_config_get_set(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        sess.set_config("default_niche", "finance")
        assert sess.get_config("default_niche") == "finance"

    def test_config_default(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        assert sess.get_config("missing_key", "default_val") == "default_val"

    def test_save_and_retrieve_snapshot(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        sess.save_trend_snapshot("tiktok", "fitness", {"hashtags": ["#fyp"]})
        snap = sess.get_latest_snapshot("tiktok", "fitness")
        assert snap is not None
        assert snap["data"]["hashtags"] == ["#fyp"]

    def test_snapshot_missing_returns_none(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        assert sess.get_latest_snapshot("tiktok", "nonexistent") is None

    def test_handle_with_at_symbol(self, tmp_path):
        sess = Session(config_path=tmp_path / "test_config.json")
        sess.add_account("instagram", "@myhandle", niche="beauty")
        acc = sess.get_account("instagram", "@myhandle")
        assert acc is not None
        assert acc["handle"] == "myhandle"
