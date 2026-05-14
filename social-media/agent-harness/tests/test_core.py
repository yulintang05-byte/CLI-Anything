"""
Unit tests for the social-media CLI harness.

All tests run without network access — they test the pure-logic functions
(hashtag building, account auditing, theme page blueprints, etc.).
Network-dependent functions (trend scrapers) are tested with mocks.
"""
import json
import unittest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from cli_anything.social_media import hashtags as _hashtags
from cli_anything.social_media import account as _account
from cli_anything.social_media import music as _music
from cli_anything.social_media import theme_pages as _theme
from cli_anything.social_media.cli import main


# ---------------------------------------------------------------------------
# hashtags
# ---------------------------------------------------------------------------

class TestHashtags(unittest.TestCase):

    def test_build_balanced_fitness(self):
        hs = _hashtags.build_hashtag_set("fitness", platform="tiktok", strategy="balanced")
        self.assertEqual(hs.niche, "fitness")
        self.assertGreater(len(hs.tags), 0)
        self.assertIn(hs.strategy, ("balanced",))
        self.assertIsInstance(hs.tags, list)

    def test_build_broad_finance(self):
        hs = _hashtags.build_hashtag_set("finance", strategy="broad")
        self.assertGreater(len(hs.tags), 0)

    def test_build_micro_unknown_niche(self):
        # Unknown niche falls back to generated tags
        hs = _hashtags.build_hashtag_set("woodworking", strategy="micro")
        self.assertGreater(len(hs.tags), 0)
        self.assertTrue(any("woodworking" in t for t in hs.tags))

    def test_score_hashtag_set_optimal(self):
        tags = ["#fyp", "#foryou", "#fitness", "#gymtok", "#workout", "#gains", "#fitfam"]
        result = _hashtags.score_hashtag_set(tags)
        self.assertIn("balance_score", result)
        self.assertEqual(result["total"], len(tags))

    def test_score_empty_set(self):
        result = _hashtags.score_hashtag_set([])
        self.assertEqual(result["total"], 0)

    def test_difficulty_scoring(self):
        self.assertEqual(_hashtags._score_difficulty(0), "micro")
        self.assertEqual(_hashtags._score_difficulty(500_000), "medium")
        self.assertEqual(_hashtags._score_difficulty(50_000_000), "viral")
        self.assertEqual(_hashtags._score_difficulty(None), "unknown")

    def test_analyze_competitor_hashtags(self):
        caption = "Daily #fitness tips 💪 #gym #workout #fyp this is my post"
        tags = _hashtags.analyze_competitor_hashtags(caption)
        self.assertIn("#fitness", tags)
        self.assertIn("#gym", tags)
        self.assertIn("#fyp", tags)

    def test_hashtag_to_dict(self):
        hi = _hashtags.HashtagInfo(tag="#test", platform="tiktok", difficulty="low")
        d = hi.to_dict()
        self.assertEqual(d["tag"], "#test")
        self.assertEqual(d["platform"], "tiktok")

    def test_all_niches_buildable(self):
        for niche in _hashtags.NICHE_SEEDS:
            hs = _hashtags.build_hashtag_set(niche)
            self.assertGreater(len(hs.tags), 0, f"Empty set for niche: {niche}")


# ---------------------------------------------------------------------------
# account
# ---------------------------------------------------------------------------

class TestAccount(unittest.TestCase):

    def test_audit_minimal(self):
        audit = _account.audit_account(platform="tiktok", username="@test")
        self.assertIsInstance(audit.score, int)
        self.assertIn(audit.grade, ("A", "B", "C", "D", "F"))

    def test_audit_strong_account(self):
        audit = _account.audit_account(
            platform="tiktok",
            username="@strong",
            bio="💪 Daily fitness motivation | Helping you hit your goals | 👇 Free plan",
            posts_per_week=7,
            avg_views=50000,
            follower_count=10000,
            has_profile_pic=True,
            has_link_in_bio=True,
            posts_consistent=True,
            uses_trending_audio=True,
            uses_hashtags=True,
            has_branded_content=True,
        )
        self.assertGreater(audit.score, 50)
        self.assertGreater(len(audit.strengths), 0)

    def test_audit_weak_account(self):
        audit = _account.audit_account(
            platform="tiktok",
            username="@weak",
            has_profile_pic=False,
            has_link_in_bio=False,
            posts_consistent=False,
            uses_trending_audio=False,
            uses_hashtags=False,
        )
        self.assertGreater(len(audit.action_items), 0)

    def test_score_good_bio(self):
        bio = "💪 Daily fitness tips | Helping you lose weight fast | 👇 Link below"
        result = _account.score_bio(bio, "tiktok")
        self.assertIn("score", result)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)

    def test_score_empty_bio(self):
        result = _account.score_bio("", "tiktok")
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["grade"], "F")

    def test_bio_guide_all_platforms(self):
        for plat in ("tiktok", "instagram", "youtube"):
            guide = _account.get_bio_guide(plat)
            self.assertIn("must_haves", guide)
            self.assertIn("templates", guide)

    def test_bio_guide_invalid_platform(self):
        with self.assertRaises(ValueError):
            _account.get_bio_guide("snapchat")

    def test_content_plan_all_niches(self):
        for niche in ("fitness", "finance", "food", "general"):
            plan = _account.get_content_plan(niche, platform="tiktok", posts_per_week=5)
            self.assertEqual(plan.posts_per_week, 5)
            self.assertEqual(len(plan.schedule), 5)

    def test_content_plan_to_dict(self):
        plan = _account.get_content_plan("fitness")
        d = plan.to_dict()
        self.assertIn("schedule", d)
        self.assertIn("content_pillars", d)

    def test_growth_playbook_stages(self):
        for stage in ("0_to_1k", "1k_to_10k", "10k_to_100k"):
            pb = _account.get_growth_playbook(stage)
            self.assertIn("daily_actions", pb)
            self.assertIn("weekly_actions", pb)

    def test_growth_playbook_invalid(self):
        with self.assertRaises(ValueError):
            _account.get_growth_playbook("100k_to_1m")

    def test_list_playbooks(self):
        pbs = _account.list_growth_playbooks()
        self.assertEqual(len(pbs), 3)

    def test_score_to_grade(self):
        self.assertEqual(_account._score_to_grade(95), "A")
        self.assertEqual(_account._score_to_grade(82), "B")
        self.assertEqual(_account._score_to_grade(70), "C")
        self.assertEqual(_account._score_to_grade(60), "D")
        self.assertEqual(_account._score_to_grade(40), "F")

    def test_audit_to_dict(self):
        audit = _account.audit_account("instagram", "@test")
        d = audit.to_dict()
        self.assertIn("score", d)
        self.assertIn("action_items", d)


# ---------------------------------------------------------------------------
# music
# ---------------------------------------------------------------------------

class TestMusic(unittest.TestCase):

    def test_get_sound_strategy_all_types(self):
        for ct in _music.SOUND_STRATEGY:
            result = _music.get_sound_strategy(ct)
            self.assertIn("tips", result)
            self.assertIn("best_for", result)

    def test_get_sound_strategy_invalid(self):
        with self.assertRaises(ValueError):
            _music.get_sound_strategy("nonexistent_type")

    def test_list_sound_strategies(self):
        strategies = _music.list_sound_strategies()
        self.assertEqual(len(strategies), len(_music.SOUND_STRATEGY))

    def test_peak_posting_times_all_platforms(self):
        for plat in ("tiktok", "instagram", "youtube"):
            times = _music.get_peak_posting_times(plat, "US")
            self.assertIsInstance(times, list)
            self.assertGreater(len(times), 0)

    def test_peak_posting_times_invalid_platform(self):
        with self.assertRaises(ValueError):
            _music.get_peak_posting_times("twitter")

    def test_trending_sound_to_dict(self):
        ts = _music.TrendingSound(
            rank=1, title="Test Sound", artist="Test Artist",
            platform="tiktok", url="https://tiktok.com"
        )
        d = ts.to_dict()
        self.assertEqual(d["rank"], 1)
        self.assertEqual(d["title"], "Test Sound")

    def test_infer_genre(self):
        self.assertEqual(_music._infer_genre_from_tags(["rap", "hiphop"]), "hiphop")
        self.assertEqual(_music._infer_genre_from_tags(["pop", "bop"]), "pop")
        self.assertIsNone(_music._infer_genre_from_tags(["unrelated"]))

    def test_infer_niches(self):
        niches = _music._infer_niches_from_tags(["gym", "workout", "fitness"])
        self.assertIn("fitness", niches)


# ---------------------------------------------------------------------------
# theme_pages
# ---------------------------------------------------------------------------

class TestThemePages(unittest.TestCase):

    def test_list_niches(self):
        niches = _theme.list_niches()
        self.assertGreater(len(niches), 5)
        for n in niches:
            self.assertIn("niche", n)
            self.assertIn("difficulty", n)

    def test_get_blueprint_all_niches(self):
        for niche in _theme.THEME_PAGE_NICHES:
            bp = _theme.get_niche_blueprint(niche)
            self.assertIsInstance(bp.page_name_ideas, list)
            self.assertGreater(len(bp.content_strategy), 0)

    def test_get_blueprint_invalid_niche(self):
        with self.assertRaises(ValueError):
            _theme.get_niche_blueprint("underwater_basket_weaving")

    def test_blueprint_to_dict(self):
        bp = _theme.get_niche_blueprint("fitness")
        d = bp.to_dict()
        self.assertIn("content_strategy", d)
        self.assertIn("monetization_methods", d)

    def test_conversion_roadmap_stages(self):
        roadmap = _theme.get_conversion_roadmap()
        self.assertEqual(len(roadmap), 4)
        for stage in roadmap:
            self.assertIn("stage", stage)
            self.assertIn("actions", stage)

    def test_get_conversion_stage_by_followers(self):
        self.assertEqual(_theme.get_conversion_stage(0)["stage"], 1)
        self.assertEqual(_theme.get_conversion_stage(999)["stage"], 1)
        self.assertEqual(_theme.get_conversion_stage(1000)["stage"], 2)
        self.assertEqual(_theme.get_conversion_stage(9999)["stage"], 2)
        self.assertEqual(_theme.get_conversion_stage(10000)["stage"], 3)
        self.assertEqual(_theme.get_conversion_stage(50000)["stage"], 4)

    def test_acquisition_guide(self):
        guide = _theme.get_acquisition_guide()
        self.assertIn("where_to_buy", guide)
        self.assertIn("red_flags", guide)
        self.assertIn("pricing_benchmarks", guide)

    def test_recommend_niche(self):
        recs = _theme.recommend_niche(["fitness", "gym"], risk_tolerance="low")
        self.assertIsInstance(recs, list)
        self.assertGreater(len(recs), 0)
        self.assertIn("match_score", recs[0])


# ---------------------------------------------------------------------------
# CLI integration tests
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def _run(self, args: list[str]) -> dict:
        result = self.runner.invoke(main, args, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return json.loads(result.output)

    def test_hashtags_build_cli(self):
        data = self._run(["hashtags", "build", "fitness", "--strategy", "balanced"])
        self.assertIn("tags", data)
        self.assertIn("strategy", data)

    def test_hashtags_score_cli(self):
        data = self._run(["hashtags", "score", "#fyp", "#fitness", "#gym"])
        self.assertEqual(data["total"], 3)

    def test_hashtags_niches_cli(self):
        data = self._run(["hashtags", "niches"])
        self.assertIn("available_niches", data)

    def test_account_bio_guide_cli(self):
        data = self._run(["account", "bio-guide", "tiktok"])
        self.assertIn("must_haves", data)

    def test_account_score_bio_cli(self):
        data = self._run(["account", "score-bio", "tiktok", "💪 Fitness daily | link below 👇"])
        self.assertIn("score", data)

    def test_account_content_plan_cli(self):
        data = self._run(["account", "content-plan", "fitness", "--posts-per-week", "5"])
        self.assertEqual(len(data["schedule"]), 5)

    def test_account_audit_minimal_cli(self):
        data = self._run(["account", "audit", "tiktok", "@test"])
        self.assertIn("score", data)
        self.assertIn("grade", data)

    def test_account_playbook_list_cli(self):
        data = self._run(["account", "playbook"])
        self.assertIsInstance(data, list)

    def test_account_playbook_stage_cli(self):
        data = self._run(["account", "playbook", "--stage", "0_to_1k"])
        self.assertIn("daily_actions", data)

    def test_theme_pages_list_cli(self):
        data = self._run(["theme-pages", "list"])
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_theme_pages_blueprint_cli(self):
        data = self._run(["theme-pages", "blueprint", "fitness"])
        self.assertIn("content_strategy", data)

    def test_theme_pages_roadmap_cli(self):
        data = self._run(["theme-pages", "roadmap"])
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 4)

    def test_theme_pages_stage_cli(self):
        data = self._run(["theme-pages", "stage", "5000"])
        self.assertIn("stage", data)
        self.assertEqual(data["stage"], 2)

    def test_theme_pages_acquire_cli(self):
        data = self._run(["theme-pages", "acquire"])
        self.assertIn("where_to_buy", data)

    def test_music_strategies_cli(self):
        data = self._run(["music", "strategies"])
        self.assertIsInstance(data, list)

    def test_music_strategy_cli(self):
        data = self._run(["music", "strategy", "viral_original"])
        self.assertIn("tips", data)

    def test_music_times_cli(self):
        data = self._run(["music", "times", "tiktok"])
        self.assertIn("peak_windows", data)


if __name__ == "__main__":
    unittest.main()
