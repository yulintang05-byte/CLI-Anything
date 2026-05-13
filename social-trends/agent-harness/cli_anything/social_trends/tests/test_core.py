"""Core unit tests for Social Trends CLI modules."""
import pytest
from click.testing import CliRunner

from cli_anything.social_trends.social_trends_cli import main
from cli_anything.social_trends.core.hashtags import (
    generate_hashtag_set,
    analyze_hashtags,
    cross_platform_strategy,
    NICHE_HASHTAG_BANKS,
    PLATFORM_LIMITS,
    OPTIMAL_COUNTS,
)
from cli_anything.social_trends.core.music import (
    fetch_trending_music,
    recommend_music_for_content,
    music_content_calendar,
)
from cli_anything.social_trends.core.account import (
    generate_posting_schedule,
    audit_account,
    generate_bio,
    content_pillars,
)
from cli_anything.social_trends.core.theme_pages import (
    list_niches,
    get_niche_guide,
    conversion_funnel,
    theme_page_sop,
)
from cli_anything.social_trends.core.tiktok import (
    fetch_trending_hashtags,
    fetch_trending_sounds,
    TikTokHashtag,
    TikTokSound,
)
from cli_anything.social_trends.core.youtube import (
    extract_top_hashtags,
    extract_top_channels,
    YTVideo,
)


# ─── Hashtags ──────────────────────────────────────────────────────────────────

class TestHashtags:
    def test_generate_known_niche(self):
        result = generate_hashtag_set("fitness", "tiktok")
        assert result.platform == "tiktok"
        assert result.niche == "fitness"
        assert len(result.hashtags) > 0
        assert all(h.startswith("#") for h in result.hashtags)

    def test_generate_respects_platform_limit(self):
        for platform, limit in PLATFORM_LIMITS.items():
            result = generate_hashtag_set("fitness", platform)
            assert len(result.hashtags) <= limit, f"Exceeded limit for {platform}"

    def test_generate_unknown_niche_fallback(self):
        result = generate_hashtag_set("knitting", "tiktok")
        assert result.niche == "knitting"
        assert len(result.hashtags) > 0

    def test_generate_with_custom_tags(self):
        result = generate_hashtag_set("fitness", "tiktok", custom_tags=["#myCustomTag"])
        assert "#myCustomTag" in result.hashtags

    def test_generate_no_viral(self):
        result = generate_hashtag_set("fitness", "tiktok", include_viral=False)
        viral_tags = {"#fyp", "#foryou", "#foryoupage", "#viral", "#trending"}
        for tag in result.hashtags:
            assert tag not in viral_tags, f"Viral tag found when include_viral=False: {tag}"

    def test_analyze_returns_analysis(self):
        results = analyze_hashtags(["#fyp", "#fitness", "#gym"], "tiktok")
        assert len(results) == 3
        assert all(r.tag.startswith("#") for r in results)
        assert all(r.platform == "tiktok" for r in results)

    def test_cross_platform_strategy_all_platforms(self):
        result = cross_platform_strategy("beauty")
        assert "platforms" in result
        for platform in ["tiktok", "instagram", "youtube", "twitter", "linkedin"]:
            assert platform in result["platforms"]

    def test_cross_platform_has_pro_tips(self):
        result = cross_platform_strategy("food")
        assert len(result["pro_tips"]) >= 5

    def test_mix_contains_expected_keys(self):
        result = generate_hashtag_set("gaming", "instagram")
        assert "high_volume" in result.mix
        assert "mid_volume" in result.mix
        assert "niche_specific" in result.mix


# ─── Music ─────────────────────────────────────────────────────────────────────

class TestMusic:
    def test_fetch_trending_returns_tracks(self):
        tracks = fetch_trending_music(limit=5)
        assert len(tracks) == 5
        for t in tracks:
            assert t.title
            assert t.artist
            assert t.rank >= 1

    def test_fetch_filtered_by_platform(self):
        tracks = fetch_trending_music(platform="tiktok", limit=10)
        for t in tracks:
            assert "tiktok" in t.platform

    def test_fetch_filtered_by_genre(self):
        tracks = fetch_trending_music(genre="Pop", limit=10)
        for t in tracks:
            assert "Pop" in t.genre

    def test_recommend_returns_results(self):
        tracks = recommend_music_for_content("workout")
        assert len(tracks) >= 1

    def test_recommend_grwm(self):
        tracks = recommend_music_for_content("GRWM")
        assert len(tracks) >= 1

    def test_calendar_has_seven_days(self):
        calendar = music_content_calendar("fitness")
        days = {entry["day"] for entry in calendar}
        assert len(days) == 7

    def test_calendar_default_niche(self):
        calendar = music_content_calendar("unknown_niche")
        assert len(calendar) == 7
        for entry in calendar:
            assert "sound" in entry
            assert "format" in entry

    def test_tracks_have_content_types(self):
        tracks = fetch_trending_music(limit=5)
        for t in tracks:
            assert len(t.best_content_types) >= 1


# ─── Account ───────────────────────────────────────────────────────────────────

class TestAccount:
    def test_schedule_tiktok(self):
        slots = generate_posting_schedule("tiktok", 7)
        assert len(slots) == 7
        for s in slots:
            assert s.engagement_score >= 1
            assert ":" in s.time_utc

    def test_schedule_respects_limit(self):
        slots = generate_posting_schedule("instagram", 3)
        assert len(slots) == 3

    def test_schedule_sorted_by_day(self):
        slots = generate_posting_schedule("tiktok", 7)
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i in range(len(slots) - 1):
            assert day_order.index(slots[i].day) <= day_order.index(slots[i + 1].day)

    def test_audit_missing_everything(self):
        result = audit_account("tiktok", followers=100, posts=5, avg_views=10,
                               bio_filled=False, profile_pic=False, link_in_bio=False,
                               posts_per_week=0.5, uses_hashtags=False, uses_trending_audio=False)
        assert len(result.issues) >= 5
        assert len(result.quick_wins) >= 5

    def test_audit_fully_optimized(self):
        result = audit_account("tiktok", followers=50000, posts=200, avg_views=40000,
                               bio_filled=True, profile_pic=True, link_in_bio=True,
                               posts_per_week=7, uses_hashtags=True, uses_trending_audio=True)
        assert len(result.wins) >= 4
        assert result.estimated_improvement

    def test_bio_generation(self):
        bio = generate_bio("tiktok", "fitness", cta_type="link")
        assert bio.platform == "tiktok"
        assert bio.niche == "fitness"
        assert bio.character_count > 0
        assert len(bio.tips) >= 3

    def test_bio_unknown_niche(self):
        bio = generate_bio("tiktok", "taxidermy")
        assert bio.niche == "taxidermy"

    def test_content_pillars_sum_close_to_posts(self):
        result = content_pillars("fitness", 7)
        total = sum(p["posts_this_week"] for p in result["pillars"])
        assert abs(total - 7) <= 2  # Allow slight rounding variance

    def test_content_pillars_default_niche(self):
        result = content_pillars("quilting", 5)
        assert len(result["pillars"]) >= 4


# ─── Theme Pages ───────────────────────────────────────────────────────────────

class TestThemePages:
    def test_list_niches_returns_all(self):
        niches = list_niches()
        assert len(niches) >= 6

    def test_list_niches_sorted_by_monetization(self):
        niches = list_niches(sort_by="monetization")
        money_map = {"$": 1, "$$": 2, "$$$": 3}
        scores = [money_map[n.monetization_potential] for n in niches]
        assert scores == sorted(scores, reverse=True)

    def test_list_niches_filter_difficulty(self):
        niches = list_niches(difficulty="Beginner")
        assert all(n.difficulty == "Beginner" for n in niches)

    def test_get_niche_guide_found(self):
        result = get_niche_guide("Luxury")
        assert "error" not in result
        assert result["name"] == "Luxury & Cars"

    def test_get_niche_guide_not_found(self):
        result = get_niche_guide("Underwater Basket Weaving")
        assert "error" in result

    def test_conversion_funnel_has_five_stages(self):
        stages = conversion_funnel("fitness")
        assert len(stages) == 5

    def test_conversion_funnel_has_tactics(self):
        stages = conversion_funnel()
        for stage in stages:
            assert len(stage.tactics) >= 3
            assert len(stage.kpis) >= 2

    def test_sop_has_workflows(self):
        sop = theme_page_sop("beauty")
        assert "daily_workflow" in sop
        assert "weekly_workflow" in sop
        assert "content_rules" in sop
        assert "monetization_timeline" in sop

    def test_sop_monetization_timeline_has_milestones(self):
        sop = theme_page_sop()
        timeline = sop["monetization_timeline"]
        assert "0-1K followers" in timeline
        assert "50K+ followers" in timeline


# ─── TikTok ────────────────────────────────────────────────────────────────────

class TestTikTok:
    def test_trending_hashtags_returns_results(self):
        tags = fetch_trending_hashtags(limit=10)
        assert len(tags) == 10
        for t in tags:
            assert isinstance(t, TikTokHashtag)
            assert t.name.startswith("#")

    def test_trending_hashtags_niche_filter(self):
        tags = fetch_trending_hashtags(niche="fitness", limit=15)
        assert len(tags) >= 5
        # Fitness niche tags should include gym/fitness terms
        names = [t.name for t in tags]
        assert any("fitness" in n or "gym" in n or "workout" in n for n in names)

    def test_trending_sounds_returns_results(self):
        sounds = fetch_trending_sounds(limit=5)
        assert len(sounds) == 5
        for s in sounds:
            assert isinstance(s, TikTokSound)
            assert s.title
            assert s.author

    def test_trending_sounds_ranked(self):
        sounds = fetch_trending_sounds(limit=10)
        ranks = [s.trending_rank for s in sounds]
        assert ranks == list(range(1, 11))


# ─── YouTube ───────────────────────────────────────────────────────────────────

class TestYouTube:
    def _make_videos(self) -> list[YTVideo]:
        return [
            YTVideo(1, "abc", "Gym Tips", "FitChannel", "1M", "10:00",
                    ["#fitness", "#gym"], "", "https://yt.com/watch?v=abc", "", "now"),
            YTVideo(2, "def", "Workout Plan", "FitChannel", "500K", "8:00",
                    ["#workout", "#gym"], "", "https://yt.com/watch?v=def", "", "now"),
            YTVideo(3, "ghi", "Diet Guide", "NutriPro", "200K", "15:00",
                    ["#fitness", "#diet"], "", "https://yt.com/watch?v=ghi", "", "now"),
        ]

    def test_extract_top_hashtags(self):
        videos = self._make_videos()
        tags = extract_top_hashtags(videos, top_n=5)
        assert len(tags) <= 5
        tag_map = {t["hashtag"]: t["occurrences"] for t in tags}
        assert tag_map.get("#fitness") == 2
        assert tag_map.get("#gym") == 2

    def test_extract_top_channels(self):
        videos = self._make_videos()
        channels = extract_top_channels(videos, top_n=5)
        assert channels[0]["channel"] == "FitChannel"
        assert channels[0]["trending_videos"] == 2


# ─── CLI Integration ───────────────────────────────────────────────────────────

class TestCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Social Trends CLI" in result.output

    def test_hashtags_suggest_json(self):
        result = self.runner.invoke(main, ["--json", "hashtags", "suggest", "fitness"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert "hashtags" in data
        assert data["platform"] == "tiktok"

    def test_hashtags_analyze(self):
        result = self.runner.invoke(main, ["hashtags", "analyze", "#fyp", "#fitness"])
        assert result.exit_code == 0

    def test_music_trending(self):
        result = self.runner.invoke(main, ["music", "trending", "--limit", "5"])
        assert result.exit_code == 0

    def test_music_trending_json(self):
        result = self.runner.invoke(main, ["--json", "music", "trending", "--limit", "3"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert len(data) == 3

    def test_account_schedule(self):
        result = self.runner.invoke(main, ["account", "schedule", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_account_audit(self):
        result = self.runner.invoke(main, [
            "account", "audit", "--platform", "tiktok",
            "--followers", "5000", "--posts", "40",
            "--posts-per-week", "2.5",
        ])
        assert result.exit_code == 0

    def test_account_bio(self):
        result = self.runner.invoke(main, ["account", "bio", "fitness", "--platform", "tiktok"])
        assert result.exit_code == 0

    def test_theme_page_niches(self):
        result = self.runner.invoke(main, ["theme-page", "niches"])
        assert result.exit_code == 0

    def test_theme_page_niches_json(self):
        result = self.runner.invoke(main, ["--json", "theme-page", "niches"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.output)
        assert len(data) >= 6

    def test_theme_page_funnel(self):
        result = self.runner.invoke(main, ["theme-page", "funnel", "--niche", "fitness"])
        assert result.exit_code == 0

    def test_theme_page_sop(self):
        result = self.runner.invoke(main, ["theme-page", "sop", "--niche", "beauty"])
        assert result.exit_code == 0

    def test_music_calendar(self):
        result = self.runner.invoke(main, ["music", "calendar", "fitness"])
        assert result.exit_code == 0

    def test_tiktok_sounds(self):
        result = self.runner.invoke(main, ["trends", "tiktok", "--sounds", "--limit", "5"])
        assert result.exit_code == 0
