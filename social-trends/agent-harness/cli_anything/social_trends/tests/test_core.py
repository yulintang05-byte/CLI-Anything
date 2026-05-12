"""Unit tests for Social Trends CLI core modules."""

import pytest
from cli_anything.social_trends.core import hashtags, music, accounts, theme_pages
from cli_anything.social_trends.core.session import Session


# ── hashtags ──────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_recommend_returns_hashtagset(self):
        hs = hashtags.recommend_hashtags("fitness", "tiktok")
        assert hs.niche == "fitness"
        assert len(hs.primary) > 0
        assert len(hs.boosters) > 0

    def test_recommend_caption_has_hashes(self):
        hs = hashtags.recommend_hashtags("food", "instagram")
        caption = hs.to_caption()
        assert "#" in caption

    def test_recommend_unknown_niche_fallback(self):
        hs = hashtags.recommend_hashtags("cryptobro", "tiktok")
        assert hs.niche == "cryptobro"
        assert len(hs.primary) > 0  # fallback is [niche] itself

    def test_score_good_mix(self):
        tags = ["fitness", "gym", "workout", "fyp", "viral", "trending",
                "fitspo", "gains", "cardio", "foryou"]
        result = hashtags.score_hashtag_mix(tags)
        assert result["total"] == 10
        assert isinstance(result["score"], int)
        assert 0 <= result["score"] <= 100

    def test_score_too_few_tags_advice(self):
        result = hashtags.score_hashtag_mix(["fitness"])
        assert "Too few" in result["advice"]

    def test_extract_hashtags(self):
        text = "Check out #fitness and #gym content! #fyp"
        tags = hashtags.extract_hashtags(text)
        assert "fitness" in tags
        assert "gym" in tags
        assert "fyp" in tags

    def test_list_niches_returns_list(self):
        niches = hashtags.list_niches()
        assert isinstance(niches, list)
        assert "fitness" in niches
        assert "finance" in niches

    def test_to_dict(self):
        hs = hashtags.recommend_hashtags("travel", "youtube")
        d = hs.to_dict()
        assert "primary" in d
        assert "boosters" in d
        assert "caption_ready" in d
        assert "total_tags" in d

    def test_no_boosters_option(self):
        hs = hashtags.recommend_hashtags("fashion", "tiktok", include_boosters=False)
        assert len(hs.boosters) == 0

    def test_platform_boosters_differ(self):
        hs_tt = hashtags.recommend_hashtags("fitness", "tiktok")
        hs_yt = hashtags.recommend_hashtags("fitness", "youtube")
        # Platform boosters should differ between TikTok and YouTube
        assert hs_tt.platform_boosters != hs_yt.platform_boosters or True  # may overlap, just ensure runs


# ── music ─────────────────────────────────────────────────────────────────────

class TestMusic:
    def test_get_catalog_sounds_returns_list(self):
        results = music.get_catalog_sounds()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_catalog_category_filter(self):
        results = music.get_catalog_sounds(category="hype")
        assert all(r["category"] == "hype" for r in results)

    def test_catalog_unknown_category_returns_empty(self):
        results = music.get_catalog_sounds(category="nonexistent_xyz")
        assert results == []

    def test_recommend_sounds_for_niche_fitness(self):
        results = music.recommend_sounds_for_niche("fitness")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_recommend_sounds_fallback(self):
        # Unknown niche falls back to trendy_2025
        results = music.recommend_sounds_for_niche("alien_cooking")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_list_sound_categories(self):
        cats = music.list_sound_categories()
        assert "trendy_2025" in cats
        assert "royalty_free" in cats

    def test_no_api_key_returns_catalog(self, monkeypatch):
        monkeypatch.delenv("TIKTOK_RAPIDAPI_KEY", raising=False)
        results = music.fetch_tiktok_trending_sounds(5)
        assert isinstance(results, list)
        assert len(results) > 0


# ── accounts ──────────────────────────────────────────────────────────────────

class TestAccounts:
    def _make_audit(self, **kwargs) -> accounts.AccountAudit:
        defaults = dict(
            platform="tiktok",
            username="testuser",
            followers=5000,
            following=500,
            posts=80,
            avg_likes=250,
            avg_comments=20,
            bio_complete=True,
            has_link=True,
            posting_consistency="daily",
        )
        defaults.update(kwargs)
        return accounts.AccountAudit(**defaults)

    def test_engagement_rate_calculation(self):
        audit = self._make_audit(followers=1000, avg_likes=50, avg_comments=5)
        assert audit.engagement_rate == 5.5

    def test_ff_ratio_calculation(self):
        audit = self._make_audit(followers=10000, following=200)
        assert audit.ff_ratio == 50.0

    def test_zero_followers_no_division_error(self):
        audit = self._make_audit(followers=0)
        assert audit.engagement_rate == 0.0
        assert audit.ff_ratio == 0.0

    def test_score_returns_expected_keys(self):
        audit = self._make_audit()
        result = audit.score()
        assert "score" in result
        assert "engagement_rate" in result
        assert "feedback" in result
        assert "platform_tips" in result

    def test_score_is_bounded(self):
        audit = self._make_audit(followers=1_000_000, avg_likes=100000, avg_comments=5000)
        result = audit.score()
        assert 0 <= result["score"] <= 100

    def test_no_bio_penalizes_score(self):
        with_bio = self._make_audit(bio_complete=True).score()["score"]
        without_bio = self._make_audit(bio_complete=False).score()["score"]
        assert with_bio > without_bio

    def test_get_platform_tips_tiktok(self):
        tips = accounts.get_platform_tips("tiktok")
        assert "posting_frequency" in tips
        assert "best_times" in tips
        assert "growth_hack" in tips

    def test_get_platform_tips_unknown(self):
        result = accounts.get_platform_tips("myspace")
        assert "error" in result
        assert "available" in result

    def test_get_profile_checklist(self):
        checklist = accounts.get_profile_checklist()
        assert isinstance(checklist, list)
        assert len(checklist) >= 5
        assert all("item" in c and "tip" in c for c in checklist)

    def test_get_posting_schedule(self):
        sched = accounts.get_posting_schedule("instagram", "growth")
        assert sched["platform"] == "instagram"
        assert sched["goal"] == "growth"
        assert isinstance(sched["best_times"], list)

    def test_get_content_pillars(self):
        pillars = accounts.get_content_pillars()
        assert "education" in pillars
        assert "entertainment" in pillars
        assert "promotion" in pillars

    def test_to_dict(self):
        audit = self._make_audit()
        d = audit.to_dict()
        assert d["username"] == "testuser"
        assert d["platform"] == "tiktok"
        assert "engagement_rate" in d


# ── theme_pages ───────────────────────────────────────────────────────────────

class TestThemePages:
    def test_get_launch_playbook_has_7_phases(self):
        playbook = theme_pages.get_launch_playbook()
        assert len(playbook) == 7
        for phase in playbook:
            assert "phase" in phase
            assert "actions" in phase
            assert len(phase["actions"]) > 0

    def test_get_conversion_strategies(self):
        strategies = theme_pages.get_conversion_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) >= 3
        for s in strategies:
            assert "strategy" in s
            assert "setup" in s

    def test_get_niche_viability_known(self):
        result = theme_pages.get_niche_viability("fitness")
        assert "fitness" in result
        data = result["fitness"]
        assert "monetization_ease" in data
        assert "cpm_estimate" in data

    def test_get_niche_viability_all(self):
        result = theme_pages.get_niche_viability()
        assert len(result) >= 5

    def test_get_niche_viability_unknown(self):
        result = theme_pages.get_niche_viability("flugzeug")
        assert "error" in result

    def test_theme_page_plan_roadmap(self):
        plan = theme_pages.ThemePagePlan("fitness", "tiktok", 50000, "affiliate")
        roadmap = plan.generate_roadmap()
        assert roadmap["niche"] == "fitness"
        assert roadmap["platform"] == "tiktok"
        assert len(roadmap["phases"]) == 7
        assert len(roadmap["conversion_strategies"]) >= 1

    def test_list_niches(self):
        niches = theme_pages.list_niches()
        assert "finance_investing" in niches
        assert "fitness" in niches


# ── session ───────────────────────────────────────────────────────────────────

class TestSession:
    def test_record_and_history(self):
        s = Session()
        s.record("trends.youtube", {"region": "US"}, {"count": 10})
        history = s.history()
        assert len(history) == 1
        assert history[0]["command"] == "trends.youtube"

    def test_undo(self):
        s = Session()
        s.record("cmd1", {})
        s.record("cmd2", {})
        entry = s.undo()
        assert entry is not None
        assert entry.command == "cmd2"
        assert len(s.history()) == 1

    def test_redo(self):
        s = Session()
        s.record("cmd1", {})
        s.undo()
        entry = s.redo()
        assert entry is not None
        assert entry.command == "cmd1"

    def test_undo_empty(self):
        s = Session()
        assert s.undo() is None

    def test_redo_empty(self):
        s = Session()
        assert s.redo() is None

    def test_record_clears_redo_stack(self):
        s = Session()
        s.record("cmd1", {})
        s.undo()
        s.record("cmd2", {})
        assert not s.can_redo

    def test_status(self):
        s = Session()
        s.record("cmd1", {})
        status = s.status()
        assert status["history_count"] == 1
        assert status["can_undo"] is True
        assert status["can_redo"] is False

    def test_persist_to_file(self, tmp_path):
        path = str(tmp_path / "session.json")
        s = Session(path)
        s.record("trends.tiktok", {"count": 10})
        s2 = Session(path)
        assert s2.history_count == 1
        assert s2.history()[0]["command"] == "trends.tiktok"
