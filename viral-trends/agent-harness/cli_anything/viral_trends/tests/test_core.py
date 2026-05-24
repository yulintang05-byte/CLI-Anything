"""Unit tests for viral-trends core modules (no network required)."""

import pytest
from cli_anything.viral_trends.core import trend_analyzer, account_optimizer, theme_page_guide


class TestTrendAnalyzer:
    def _sample_yt(self):
        return {
            "hashtags": [
                {"tag": "#finance", "count": 3},
                {"tag": "#money", "count": 2},
                {"tag": "#viral", "count": 5},
            ],
        }

    def _sample_tt(self):
        return {
            "hashtags": [
                {"tag": "#finance", "count": 4},
                {"tag": "#fyp", "count": 8},
                {"tag": "#viral", "count": 3},
            ],
        }

    def test_aggregate_hashtags_merges_counts(self):
        result = trend_analyzer.aggregate_hashtags(
            yt_data=self._sample_yt(), tt_data=self._sample_tt()
        )
        assert isinstance(result, list)
        assert len(result) > 0
        tags = {r["tag"] for r in result}
        assert "#finance" in tags

    def test_cross_platform_bonus(self):
        result = trend_analyzer.aggregate_hashtags(
            yt_data=self._sample_yt(), tt_data=self._sample_tt()
        )
        finance = next((r for r in result if r["tag"] == "#finance"), None)
        assert finance is not None
        assert finance["cross_platform"] is True
        # cross-platform bonus: (3+4)*2 = 14
        assert finance["total"] == 14

    def test_aggregate_hashtags_yt_only(self):
        result = trend_analyzer.aggregate_hashtags(yt_data=self._sample_yt())
        assert len(result) == 3

    def test_aggregate_hashtags_tt_only(self):
        result = trend_analyzer.aggregate_hashtags(tt_data=self._sample_tt())
        assert len(result) == 3

    def test_aggregate_music(self):
        yt_music = [{"track": "Song A", "artist": "Artist X", "video_url": "https://yt.com/a"}]
        tt_music = [{"title": "Song B", "author": "Artist Y", "id": "111", "video_count": 5}]
        result = trend_analyzer.aggregate_music(yt_music=yt_music, tt_music=tt_music)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_aggregate_music_cross_platform(self):
        yt_music = [{"track": "Hit Song", "artist": "Artist Z", "video_url": "https://yt.com/z"}]
        tt_music = [{"title": "Hit Song", "author": "Artist Z", "id": "222", "video_count": 10}]
        result = trend_analyzer.aggregate_music(yt_music=yt_music, tt_music=tt_music)
        assert len(result) == 1
        assert "tiktok" in result[0]["platforms"]
        assert "youtube" in result[0]["platforms"]

    def test_score_content_opportunity(self):
        tags = [{"tag": "#finance", "total": 14, "cross_platform": True, "yt_count": 3, "tt_count": 4}]
        music = [{"track": "Hit", "artist": "A", "platforms": ["youtube", "tiktok"], "tt_video_count": 5}]
        result = trend_analyzer.score_content_opportunity(tags, music)
        assert "content_opportunities" in result
        assert "top_hashtags" in result
        assert "top_sounds" in result

    def test_niche_hashtag_strategy(self):
        tags = [
            {"tag": "#financetips", "total": 10, "cross_platform": False, "yt_count": 5, "tt_count": 5},
            {"tag": "#viral", "total": 20, "cross_platform": True, "yt_count": 10, "tt_count": 10},
            {"tag": "#fyp", "total": 30, "cross_platform": True, "yt_count": 15, "tt_count": 15},
        ]
        result = trend_analyzer.niche_hashtag_strategy("finance", tags)
        assert result["niche"] == "finance"
        assert "strategy" in result
        assert "recommended_mix" in result["strategy"]


class TestAccountOptimizer:
    def test_generate_profile_audit_basic(self):
        result = account_optimizer.generate_profile_audit(
            platform="tiktok", account_type="theme_page", niche="finance"
        )
        assert "posting_schedule" in result
        assert "hashtag_strategy" in result
        assert "profile_checklist" in result
        assert "quick_wins" in result
        assert result["platform"] == "tiktok"

    def test_generate_profile_audit_long_bio_flagged(self):
        long_bio = "x" * 200
        result = account_optimizer.generate_profile_audit(
            platform="tiktok", account_type="theme_page", current_bio=long_bio
        )
        assert any("too long" in issue.lower() for issue in result["bio_issues"])

    def test_generate_profile_audit_missing_link(self):
        result = account_optimizer.generate_profile_audit(
            platform="tiktok", account_type="theme_page", current_bio="Just vibes no link"
        )
        assert any("link" in issue.lower() for issue in result["bio_issues"])

    def test_generate_content_calendar(self):
        result = account_optimizer.generate_content_calendar(
            niche="fitness", platforms=["tiktok", "youtube_shorts"], days=5
        )
        assert "week_calendar" in result
        assert len(result["week_calendar"]) == 5
        assert result["niche"] == "fitness"

    def test_generate_content_calendar_with_trends(self):
        tags = [{"tag": "#fitness", "total": 10}]
        music = [{"track": "Song", "artist": "X", "platforms": ["tiktok"], "tt_video_count": 3}]
        result = account_optimizer.generate_content_calendar(
            niche="fitness", platforms=["tiktok"], days=3,
            trending_hashtags=tags, trending_music=music
        )
        assert len(result["week_calendar"]) == 3

    def test_growth_hacks_tiktok(self):
        result = account_optimizer.growth_hacks("tiktok", "theme_page")
        assert "growth_hacks" in result
        assert len(result["growth_hacks"]) > 0
        assert "monetization_unlock_milestones" in result

    def test_growth_hacks_youtube(self):
        result = account_optimizer.growth_hacks("youtube", "personal_brand")
        assert "growth_hacks" in result

    def test_growth_hacks_theme_page_extras(self):
        result = account_optimizer.growth_hacks("tiktok", "theme_page")
        hack_names = [h["hack"] for h in result["growth_hacks"]]
        assert any("SFS" in h or "Repost" in h or "Username" in h for h in hack_names)


class TestThemePageGuide:
    def test_get_niche_recommendations(self):
        result = theme_page_guide.get_niche_recommendations()
        assert "top_niches" in result
        assert len(result["top_niches"]) > 0
        for niche in result["top_niches"]:
            assert "niche" in niche
            assert "cpm_range" in niche

    def test_get_full_roadmap_phase_detection(self):
        r0 = theme_page_guide.get_full_roadmap(current_followers=0)
        assert r0["current_phase"] == 1

        r1k = theme_page_guide.get_full_roadmap(current_followers=1000)
        assert r1k["current_phase"] == 2

        r10k = theme_page_guide.get_full_roadmap(current_followers=10000)
        assert r10k["current_phase"] == 3

        r100k = theme_page_guide.get_full_roadmap(current_followers=100000)
        assert r100k["current_phase"] == 4

    def test_get_full_roadmap_has_all_sections(self):
        result = theme_page_guide.get_full_roadmap(niche="finance", current_followers=0)
        assert "phases" in result
        assert "conversion_tactics" in result
        assert "account_sale_guide" in result
        assert "tools_stack" in result
        assert len(result["phases"]) == 4

    def test_conversion_tactics_structure(self):
        for tactic in theme_page_guide.CONVERSION_TACTICS:
            assert "tactic" in tactic
            assert "description" in tactic
            assert "conversion_rate" in tactic
            assert "works_on" in tactic

    def test_niches_by_cpm_sorted_high_to_low(self):
        niches = theme_page_guide.NICHES_BY_CPM
        assert niches[0]["niche"] == "Finance / Investing"

    def test_account_sale_calculator_examples(self):
        calc = theme_page_guide.ACCOUNT_SALE_CALCULATOR
        assert "examples" in calc
        assert len(calc["examples"]) >= 4
        assert "formula" in calc
