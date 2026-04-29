"""Unit tests for Social Trends core modules (no network, no API keys required)."""

import pytest
import responses as resp_lib

from cli_anything.social_trends.core import youtube, tiktok, account_optimizer, theme_pages
from cli_anything.social_trends.utils.social_backend import SocialSession, get_env_status


# ── YouTube helpers ───────────────────────────────────────────────────────────

class TestYouTubeHelpers:
    def test_extract_hashtags_basic(self):
        text = "Love this #trending video! Check out #fyp and #viral2024"
        result = youtube._extract_hashtags(text)
        assert result == ["trending", "fyp", "viral2024"]

    def test_extract_hashtags_empty(self):
        assert youtube._extract_hashtags("no hashtags here") == []

    def test_extract_hashtags_deduplication(self):
        text = "#cats #dogs #cats #pets"
        result = youtube._extract_hashtags(text)
        assert result.count("cats") == 1
        assert len(result) == 3

    def test_parse_music_title_dash(self):
        artist, track = youtube._parse_music_title("The Weeknd - Blinding Lights")
        assert artist == "The Weeknd"
        assert track == "Blinding Lights"

    def test_parse_music_title_no_separator(self):
        artist, track = youtube._parse_music_title("Some Random Title")
        assert artist == ""
        assert track == "Some Random Title"

    def test_parse_music_title_pipe(self):
        artist, track = youtube._parse_music_title("Bad Bunny | Tití Me Preguntó")
        assert artist == "Bad Bunny"
        assert track == "Tití Me Preguntó"

    def test_days_ago_iso_format(self):
        result = youtube._days_ago_iso(7)
        assert "T" in result
        assert result.endswith("Z")

    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
        with pytest.raises(RuntimeError, match="YOUTUBE_API_KEY"):
            youtube._get_api_key()


# ── TikTok helpers ────────────────────────────────────────────────────────────

class TestTikTokHelpers:
    def test_extract_hashtags(self):
        text = "#motivation #grind #hustle let's go"
        result = tiktok._extract_hashtags(text)
        assert "motivation" in result
        assert "grind" in result
        assert "hustle" in result

    def test_days_ago_str_format(self):
        result = tiktok._days_ago_str(7)
        assert len(result) == 8
        assert result.isdigit()

    def test_today_str_format(self):
        result = tiktok._today_str()
        assert len(result) == 8
        assert result.isdigit()

    def test_aggregate_hashtags_empty(self):
        result = tiktok._aggregate_hashtags_from_videos([])
        assert result == []

    def test_aggregate_hashtags_counts(self):
        videos = [
            {"hashtags": ["fitness", "gym"], "views": 100, "likes": 10},
            {"hashtags": ["fitness", "workout"], "views": 200, "likes": 20},
        ]
        result = tiktok._aggregate_hashtags_from_videos(videos)
        fitness = next(r for r in result if r["hashtag"] == "#fitness")
        assert fitness["video_count"] == 2
        assert fitness["total_views"] == 300

    def test_aggregate_sounds_empty(self):
        result = tiktok._aggregate_sounds_from_videos([])
        assert result == []

    def test_aggregate_sounds_counts(self):
        videos = [
            {"music_id": "123", "music_title": "Song A", "music_author": "Artist X", "views": 500},
            {"music_id": "123", "music_title": "Song A", "music_author": "Artist X", "views": 300},
            {"music_id": "456", "music_title": "Song B", "music_author": "Artist Y", "views": 100},
        ]
        result = tiktok._aggregate_sounds_from_videos(videos)
        assert result[0]["music_id"] == "123"
        assert result[0]["video_count"] == 2
        assert result[0]["total_views"] == 800

    def test_parse_tiktok_next_data_no_script(self):
        result = tiktok._parse_tiktok_next_data("<html><body>No data</body></html>")
        assert result == []

    def test_has_research_api_false(self, monkeypatch):
        monkeypatch.delenv("TIKTOK_API_KEY", raising=False)
        monkeypatch.delenv("TIKTOK_API_SECRET", raising=False)
        assert tiktok._has_research_api() is False

    def test_has_research_api_true(self, monkeypatch):
        monkeypatch.setenv("TIKTOK_API_KEY", "test_key")
        monkeypatch.setenv("TIKTOK_API_SECRET", "test_secret")
        assert tiktok._has_research_api() is True


# ── Account optimizer ─────────────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_posting_schedule_tiktok(self):
        sched = account_optimizer.get_posting_schedule("tiktok")
        assert "best_days" in sched
        assert "best_times_utc" in sched
        assert "frequency" in sched
        assert len(sched["best_days"]) >= 1

    def test_posting_schedule_youtube(self):
        sched = account_optimizer.get_posting_schedule("youtube")
        assert "Thursday" in sched["best_days"] or "Friday" in sched["best_days"]

    def test_posting_schedule_with_niche(self):
        sched = account_optimizer.get_posting_schedule("tiktok", "fitness")
        assert "niche_tip" in sched
        assert "fitness" in sched["niche_tip"].lower() or "workout" in sched["niche_tip"].lower()

    def test_content_mix_tiktok(self):
        mix = account_optimizer.get_content_mix("tiktok")
        total_share = sum(m["share"] for m in mix)
        assert total_share == 100
        assert len(mix) >= 4

    def test_content_mix_youtube(self):
        mix = account_optimizer.get_content_mix("youtube")
        total_share = sum(m["share"] for m in mix)
        assert total_share == 100

    def test_growth_roadmap_zero_followers(self):
        roadmap = account_optimizer.get_growth_roadmap(0)
        assert "0" in roadmap["phase"]

    def test_growth_roadmap_5k_followers(self):
        roadmap = account_optimizer.get_growth_roadmap(5000)
        assert "1K" in roadmap["phase"] or "10K" in roadmap["phase"]

    def test_growth_roadmap_100k_plus(self):
        roadmap = account_optimizer.get_growth_roadmap(500_000)
        assert "100K" in roadmap["phase"]

    def test_bio_template_tiktok(self):
        result = account_optimizer.get_bio_template("tiktok", "fitness")
        assert "bio" in result
        assert "fitness" in result["bio"].lower()
        assert "character_limits" in result
        assert result["character_limits"]["tiktok"] == 80

    def test_bio_template_youtube(self):
        result = account_optimizer.get_bio_template("youtube", "tech")
        assert "tech" in result["bio"].lower()

    def test_hashtag_strategy_tiktok(self):
        tip = account_optimizer._hashtag_strategy_tip("tiktok", None)
        assert "hashtag" in tip.lower() or "3" in tip

    def test_hashtag_strategy_youtube(self):
        tip = account_optimizer._hashtag_strategy_tip("youtube", None)
        assert "description" in tip.lower() or "hashtag" in tip.lower()

    def test_monetization_readiness_zero(self):
        result = account_optimizer._monetization_readiness({"followers": 0}, "tiktok")
        assert result["current_followers"] == 0
        assert all(not m["unlocked"] for m in result["milestones"])

    def test_monetization_readiness_10k(self):
        result = account_optimizer._monetization_readiness({"followers": 10_000}, "tiktok")
        unlocked = [m for m in result["milestones"] if m["unlocked"]]
        assert len(unlocked) >= 1

    def test_identify_issues_empty_bio(self):
        audit = {"bio": "", "followers": 1000, "video_count": 20, "avg_likes_per_video": 5}
        issues = account_optimizer._identify_issues(audit)
        assert any("bio" in i.lower() for i in issues)

    def test_identify_issues_low_videos(self):
        audit = {"bio": "some bio", "followers": 100, "video_count": 3}
        issues = account_optimizer._identify_issues(audit)
        assert any("video" in i.lower() for i in issues)

    def test_audit_unsupported_platform(self):
        with pytest.raises(ValueError, match="Unsupported platform"):
            account_optimizer.audit_account("twitter", "testuser")

    def test_parse_follower_range(self):
        low, high = account_optimizer._parse_follower_range("0–1K followers")
        assert low == 0
        assert high == 1000

    def test_parse_follower_range_millions(self):
        low, high = account_optimizer._parse_follower_range("1M+ followers")
        assert low == 1_000_000

    def test_generate_quick_wins_has_items(self):
        wins = account_optimizer._generate_quick_wins({}, "tiktok", "fitness")
        assert len(wins) >= 4

    def test_niche_posting_tip_finance(self):
        tip = account_optimizer._get_niche_posting_tip("finance", "tiktok")
        assert "monday" in tip.lower() or "finance" in tip.lower()

    def test_niche_posting_tip_food(self):
        tip = account_optimizer._get_niche_posting_tip("food recipes", "tiktok")
        assert "food" in tip.lower() or "thursday" in tip.lower()


# ── Theme pages ───────────────────────────────────────────────────────────────

class TestThemePages:
    def test_get_profitable_niches_returns_list(self):
        result = theme_pages.get_profitable_niches()
        assert isinstance(result, list)
        assert len(result) >= 5

    def test_get_profitable_niches_max_results(self):
        result = theme_pages.get_profitable_niches(max_results=3)
        assert len(result) <= 3

    def test_get_profitable_niches_filter_difficulty(self):
        result = theme_pages.get_profitable_niches(difficulty="Easy")
        assert all(n["difficulty"] == "Easy" for n in result)

    def test_get_profitable_niches_sort_growth_speed(self):
        result = theme_pages.get_profitable_niches(sort_by="growth_speed")
        speed_order = {"Very Fast": 0, "Fast": 1, "Medium": 2, "Slow": 3}
        speeds = [speed_order.get(n["growth_speed"], 99) for n in result]
        assert speeds == sorted(speeds)

    def test_get_profitable_niches_filter_platform(self):
        result = theme_pages.get_profitable_niches(platform="TikTok")
        for n in result:
            platforms_lower = [p.lower() for p in n["platforms"]]
            assert "tiktok" in platforms_lower

    def test_generate_strategy_returns_keys(self):
        result = theme_pages.generate_strategy("fitness", "tiktok")
        assert "content_pillars" in result
        assert "monetization_path" in result
        assert "first_30_days_plan" in result
        assert "hashtag_starter_pack" in result
        assert "recommended_username_formats" in result

    def test_generate_strategy_content_pillar_sum(self):
        result = theme_pages.generate_strategy("luxury", "tiktok")
        total = sum(p["share"] for p in result["content_pillars"])
        assert total == 100

    def test_generate_strategy_thirty_day_plan_four_weeks(self):
        result = theme_pages.generate_strategy("food", "tiktok")
        assert len(result["first_30_days_plan"]) == 4

    def test_get_conversion_guide_full(self):
        guide = theme_pages.get_conversion_guide()
        assert "phases" in guide
        assert len(guide["phases"]) == 5
        assert "common_mistakes" in guide
        assert "legal_considerations" in guide

    def test_get_conversion_guide_section(self):
        section = theme_pages.get_conversion_guide("Monetization")
        assert "monetization" in section.get("name", "").lower()

    def test_get_conversion_guide_invalid_section(self):
        result = theme_pages.get_conversion_guide("NonExistentSection")
        assert "error" in result

    def test_compare_niches_returns_comparison(self):
        result = theme_pages.compare_niches("fitness", "food")
        assert "comparison" in result
        assert "recommendation" in result
        assert len(result["comparison"]) >= 3

    def test_get_monetization_timeline(self):
        result = theme_pages.get_monetization_timeline("tech")
        assert "income_by_stage" in result
        assert "monetization_methods" in result
        assert "fastest_monetization" in result

    def test_starter_hashtags_structure(self):
        tags = theme_pages._starter_hashtags("fitness")
        assert "niche_specific" in tags
        assert "broad" in tags
        assert "community" in tags
        assert isinstance(tags["niche_specific"], list)
        assert len(tags["niche_specific"]) >= 2

    def test_find_niche_by_keyword(self):
        result = theme_pages._find_niche("dogs")
        assert "niche" in result

    def test_find_niche_unknown(self):
        result = theme_pages._find_niche("underwater basket weaving")
        assert "monetization" in result

    def test_content_pillars_sum_100(self):
        pillars = theme_pages._content_pillars("anything")
        assert sum(p["share"] for p in pillars) == 100

    def test_recommend_between(self):
        a = {"growth_speed": "Very Fast", "saturation": "Low", "difficulty": "Easy"}
        b = {"growth_speed": "Slow", "saturation": "Very High", "difficulty": "Hard"}
        result = theme_pages._recommend_between(a, b, "niche_a", "niche_b")
        assert "niche_a" in result


# ── Session / Utils ───────────────────────────────────────────────────────────

class TestSocialSession:
    def test_session_defaults(self):
        session = SocialSession()
        assert session.active_niche is None
        assert session.primary_platform == "tiktok"

    def test_session_set_niche(self):
        session = SocialSession()
        session.active_niche = "fitness"
        assert session.active_niche == "fitness"

    def test_session_add_account(self):
        session = SocialSession()
        session.add_account("tiktok", "testuser", {"followers": 1000})
        accounts = session.get_accounts("tiktok")
        assert "testuser" in accounts
        assert accounts["testuser"]["followers"] == 1000

    def test_session_cache_and_retrieve(self):
        session = SocialSession()
        session.cache_trends("test_key", [1, 2, 3])
        result = session.get_cached("test_key", max_age_minutes=60)
        assert result == [1, 2, 3]

    def test_session_cache_expired(self):
        session = SocialSession()
        session.data["cached_trends"]["old_key"] = {
            "data": "stale",
            "cached_at": "2020-01-01T00:00:00+00:00",
        }
        result = session.get_cached("old_key", max_age_minutes=60)
        assert result is None

    def test_session_round_trip(self):
        session = SocialSession()
        session.active_niche = "tech"
        session.primary_platform = "youtube"
        data = session.to_dict()
        session2 = SocialSession()
        session2.from_dict(data)
        assert session2.active_niche == "tech"
        assert session2.primary_platform == "youtube"

    def test_get_env_status_structure(self):
        status = get_env_status()
        assert "YOUTUBE_API_KEY" in status
        assert "TIKTOK_API_KEY" in status
        for k, v in status.items():
            assert "set" in v
            assert "required_for" in v
            assert "how_to_get" in v
