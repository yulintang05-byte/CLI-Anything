"""Unit tests for social-trends core modules.

All tests run without network access by mocking or using only internal data.
"""

import json
import pytest

# ── hashtags ──────────────────────────────────────────────────────────────────

from cli_anything.social_trends.core.hashtags import (
    recommend_hashtags,
    analyse_caption,
    merge_hashtags,
    list_niches,
    _normalise,
)


class TestHashtags:
    def test_recommend_returns_dict(self):
        result = recommend_hashtags("fitness")
        assert isinstance(result, dict)
        assert "hashtags" in result
        assert "copy_paste" in result
        assert result["count"] > 0

    def test_recommend_all_platforms(self):
        result = recommend_hashtags("food", platform="all", limit=15)
        assert result["count"] <= 15
        for h in result["hashtags"]:
            assert h["hashtag"].startswith("#")

    def test_recommend_tiktok_only(self):
        result = recommend_hashtags("fashion", platform="tiktok", limit=10)
        assert result["platform"] == "tiktok"
        assert result["count"] <= 10

    def test_recommend_unknown_niche_raises(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            recommend_hashtags("unicorn_farming")

    def test_analyse_caption_empty(self):
        result = analyse_caption("no hashtags here")
        assert result["hashtag_count"] == 0
        assert result["score"] < 50

    def test_analyse_caption_too_many(self):
        tags = " ".join(f"#tag{i}" for i in range(35))
        result = analyse_caption(tags)
        assert result["hashtag_count"] == 35
        recs = " ".join(result["recommendations"])
        assert "Too many" in recs

    def test_analyse_caption_with_universal(self):
        result = analyse_caption("#fyp #fitness #gym")
        assert "#fyp" in result["unique_hashtags"]
        assert result["universal_tags_present"]

    def test_analyse_caption_duplicates(self):
        result = analyse_caption("#fitness #fitness #gym")
        assert "#fitness" in result["duplicates"]

    def test_merge_hashtags(self):
        yt = [{"hashtag": "#viral", "view_count": 0}, {"hashtag": "#dance", "view_count": 0}]
        tt = [{"hashtag": "#fyp", "view_count": 50_000_000_000},
              {"hashtag": "#dance", "view_count": 7_500_000_000}]
        merged = merge_hashtags(yt, tt, limit=10)
        assert len(merged) >= 2
        tags = [m["hashtag"] for m in merged]
        assert "#dance" in tags  # present on both platforms

    def test_merge_cross_platform_flag(self):
        yt = [{"hashtag": "#dance", "view_count": 0}]
        tt = [{"hashtag": "#dance", "view_count": 1_000}]
        merged = merge_hashtags(yt, tt)
        dance = next(m for m in merged if m["hashtag"] == "#dance")
        assert dance["cross_platform"] is True

    def test_normalise(self):
        assert _normalise("  #FITNESS ") == "#fitness"
        assert _normalise("FYP") == "#fyp"

    def test_list_niches(self):
        niches = list_niches()
        assert "fitness" in niches
        assert "finance" in niches
        assert len(niches) >= 8


# ── music ─────────────────────────────────────────────────────────────────────

from cli_anything.social_trends.core.music import (
    list_trending_music,
    get_music_for_content_type,
    get_platform_music_guide,
    list_genres,
    list_moods,
)


class TestMusic:
    def test_list_trending_all(self):
        result = list_trending_music(limit=5)
        assert result["count"] <= 5
        assert len(result["tracks"]) <= 5
        for t in result["tracks"]:
            assert "title" in t
            assert "artist" in t

    def test_list_trending_by_genre(self):
        result = list_trending_music(genre="pop", limit=10)
        for t in result["tracks"]:
            assert t["genre"] == "pop"

    def test_list_trending_by_mood(self):
        result = list_trending_music(mood="energetic", limit=20)
        for t in result["tracks"]:
            assert "energetic" in t.get("mood", "")

    def test_music_for_content_dance(self):
        result = get_music_for_content_type("dance")
        assert result["count"] > 0
        for t in result["tracks"]:
            assert "dance" in t.get("best_for", [])

    def test_music_for_content_travel(self):
        result = get_music_for_content_type("travel")
        assert result["count"] > 0

    def test_platform_guide_tiktok(self):
        result = get_platform_music_guide("tiktok")
        assert "guidance" in result
        assert "recommended_tracks" in result
        assert result["platform"] == "tiktok"

    def test_platform_guide_shorts(self):
        result = get_platform_music_guide("shorts")
        assert result["platform"] == "youtube_shorts"

    def test_platform_guide_reels(self):
        result = get_platform_music_guide("reels")
        assert result["platform"] == "instagram_reels"

    def test_platform_guide_invalid(self):
        with pytest.raises(ValueError):
            get_platform_music_guide("myspace")

    def test_list_genres(self):
        genres = list_genres()
        assert "pop" in genres
        assert "hip-hop" in genres

    def test_list_moods(self):
        moods = list_moods()
        assert len(moods) > 3
        assert "energetic" in moods or "epic" in moods


# ── account ───────────────────────────────────────────────────────────────────

from cli_anything.social_trends.core.account import (
    audit_account,
    get_optimization_plan,
    get_posting_calendar,
    get_hook_formulas,
    list_platforms,
    _resolve_platform,
)


class TestAccount:
    def test_audit_tiktok_basic(self):
        result = audit_account("tiktok", follower_count=1000, avg_views=50, posts_per_week=1)
        assert "health_score" in result
        assert 0 <= result["health_score"] <= 100
        assert result["platform"] == "tiktok"
        assert len(result["action_items"]) > 0

    def test_audit_low_posting_frequency(self):
        result = audit_account("tiktok", follower_count=5000, avg_views=200, posts_per_week=0)
        priorities = [a["priority"] for a in result["action_items"]]
        assert "HIGH" in priorities

    def test_audit_youtube(self):
        result = audit_account("youtube")
        assert result["platform"] == "youtube"

    def test_audit_instagram_alias(self):
        result = audit_account("ig")
        assert result["platform"] == "instagram"

    def test_optimization_plan_tiktok(self):
        result = get_optimization_plan("tiktok")
        assert "algorithm_signals" in result
        assert "profile_checklist" in result
        assert "posting_schedule" in result
        assert "growth_tactics" in result

    def test_optimization_plan_youtube(self):
        result = get_optimization_plan("yt")
        assert result["platform"] == "youtube"

    def test_posting_calendar_default(self):
        result = get_posting_calendar()
        assert "calendar" in result
        assert len(result["calendar"]) == 7
        for day, posts in result["calendar"].items():
            assert isinstance(posts, list)

    def test_posting_calendar_single_platform(self):
        result = get_posting_calendar(["tiktok"])
        for day, posts in result["calendar"].items():
            for post in posts:
                assert post["platform"] == "tiktok"

    def test_hook_formulas_tiktok(self):
        result = get_hook_formulas("tiktok")
        assert len(result["formulas"]) > 0

    def test_hook_formulas_youtube(self):
        result = get_hook_formulas("youtube")
        assert len(result["formulas"]) > 0

    def test_resolve_platform_aliases(self):
        assert _resolve_platform("tt") == "tiktok"
        assert _resolve_platform("ig") == "instagram"
        assert _resolve_platform("yt") == "youtube"

    def test_resolve_platform_invalid(self):
        with pytest.raises(ValueError):
            _resolve_platform("snapchat")

    def test_list_platforms(self):
        platforms = list_platforms()
        assert "tiktok" in platforms
        assert "youtube" in platforms
        assert "instagram" in platforms


# ── theme_page ────────────────────────────────────────────────────────────────

from cli_anything.social_trends.core.theme_page import (
    list_niches as theme_list_niches,
    get_niche_deep_dive,
    get_launch_playbook,
    get_conversion_funnel,
    get_content_sourcing_guide,
    list_funnel_types,
    list_niche_keys,
)


class TestThemePage:
    def test_list_niches_all(self):
        result = theme_list_niches()
        assert result["count"] > 5
        for n in result["niches"]:
            assert "cpm" in n or "avg_cpm_usd" in n

    def test_list_niches_filter_monetisation(self):
        result = theme_list_niches(min_monetisation="high")
        for n in result["niches"]:
            assert n["monetisation_ceiling"] in ("high", "very_high")

    def test_list_niches_filter_platform(self):
        result = theme_list_niches(platform="youtube")
        for n in result["niches"]:
            assert "youtube" in n["platforms"]

    def test_niche_deep_dive_finance(self):
        result = get_niche_deep_dive("finance_investing")
        assert "shoutout_rate_card" in result
        assert "viral_hooks" in result
        assert len(result["viral_hooks"]) > 0

    def test_niche_deep_dive_normalise_dash(self):
        result = get_niche_deep_dive("tech-ai")
        assert result["niche_key"] == "tech_ai"

    def test_niche_deep_dive_invalid(self):
        with pytest.raises(ValueError, match="Unknown niche"):
            get_niche_deep_dive("knitting_for_cats")

    def test_launch_playbook_phases(self):
        result = get_launch_playbook()
        assert "phases" in result
        assert len(result["phases"]) >= 4
        for phase in result["phases"]:
            assert "phase" in phase
            assert "steps" in phase
            assert len(phase["steps"]) > 0

    def test_launch_playbook_key_rules(self):
        result = get_launch_playbook()
        assert len(result["key_rules"]) > 0

    def test_funnel_affiliate(self):
        result = get_conversion_funnel("affiliate")
        assert "stages" in result
        assert len(result["stages"]) >= 4

    def test_funnel_shoutout(self):
        result = get_conversion_funnel("shoutout")
        assert "stages" in result

    def test_funnel_digital_product(self):
        result = get_conversion_funnel("digital_product")
        assert "stages" in result

    def test_funnel_invalid(self):
        with pytest.raises(ValueError):
            get_conversion_funnel("pyramid_scheme")

    def test_content_sourcing_guide(self):
        result = get_content_sourcing_guide()
        assert "legal_methods" in result
        assert "reposting_best_practices" in result
        assert "automation_stack" in result

    def test_list_funnel_types(self):
        funnels = list_funnel_types()
        assert "affiliate" in funnels
        assert "shoutout" in funnels

    def test_list_niche_keys(self):
        keys = list_niche_keys()
        assert "luxury_lifestyle" in keys
        assert "finance_investing" in keys


# ── scraper utils (no-network) ────────────────────────────────────────────────

from cli_anything.social_trends.utils.scraper import shorten_number, extract_json_var


class TestScraper:
    def test_shorten_number_millions(self):
        assert shorten_number(1_500_000) == "1.5M"

    def test_shorten_number_thousands(self):
        assert shorten_number(45_000) == "45.0K"

    def test_shorten_number_small(self):
        assert shorten_number(999) == "999"

    def test_extract_json_var_simple(self):
        html = 'var myData = {"key": "value"}; var other'
        result = extract_json_var(html, "myData")
        assert result == {"key": "value"}

    def test_extract_json_var_missing(self):
        result = extract_json_var("<html>nothing here</html>", "missingVar")
        assert result is None


# ── tiktok fallbacks (no-network) ─────────────────────────────────────────────

from cli_anything.social_trends.core.tiktok import (
    _fallback_trending_hashtags,
    _fallback_trending_sounds,
    _parse_discover_html,
)


class TestTikTokNoNetwork:
    def test_fallback_hashtags_non_empty(self):
        tags = _fallback_trending_hashtags()
        assert len(tags) >= 10
        for t in tags:
            assert t["hashtag"].startswith("#")
            assert t["view_count"] > 0

    def test_fallback_sounds_non_empty(self):
        sounds = _fallback_trending_sounds()
        assert len(sounds) >= 5
        for s in sounds:
            assert "title" in s
            assert "artist" in s

    def test_parse_discover_html_href_pattern(self):
        html = '''
        <a href="https://www.tiktok.com/tag/fitness">Fitness</a>
        <a href="https://www.tiktok.com/tag/dance">Dance</a>
        '''
        tags = _parse_discover_html(html)
        tag_names = [t["hashtag"] for t in tags]
        assert "#fitness" in tag_names
        assert "#dance" in tag_names

    def test_parse_discover_html_json_pattern(self):
        html = '"hashtagName":"viraltrend"'
        tags = _parse_discover_html(html)
        assert any(t["hashtag"] == "#viraltrend" for t in tags)


# ── youtube (no-network) ──────────────────────────────────────────────────────

from cli_anything.social_trends.core.youtube import (
    _parse_video_renderer,
    extract_hashtags_from_videos,
    extract_music_from_videos,
)


class TestYouTubeNoNetwork:
    def _make_renderer(self, title="Test Video", channel="TestChannel", views="1,000,000 views"):
        return {
            "videoId": "abc123DEFGH",
            "title": {"runs": [{"text": title}]},
            "longBylineText": {"runs": [{"text": channel}]},
            "viewCountText": {"simpleText": views},
            "publishedTimeText": {"simpleText": "2 days ago"},
            "lengthText": {"simpleText": "10:30"},
        }

    def test_parse_video_renderer_basic(self):
        renderer = self._make_renderer()
        result = _parse_video_renderer(renderer)
        assert result is not None
        assert result["video_id"] == "abc123DEFGH"
        assert result["title"] == "Test Video"
        assert result["channel"] == "TestChannel"

    def test_parse_video_renderer_missing_title(self):
        result = _parse_video_renderer({"videoId": "abc"})
        # Should not crash; title defaults to empty string
        assert result is not None

    def test_extract_hashtags_from_videos(self):
        videos = [
            {"title": "Best #fitness tips", "description_snippet": "#gym workout #health"},
            {"title": "#fitness for beginners", "description_snippet": ""},
        ]
        tags = extract_hashtags_from_videos(videos)
        assert any(t["hashtag"] == "#fitness" for t in tags)
        # fitness appears in both → should have count 2
        fitness = next(t for t in tags if t["hashtag"] == "#fitness")
        assert fitness["mentions"] == 2

    def test_extract_music_from_videos(self):
        videos = [
            {"title": "Best workout music: Lose Control by Teddy Swims",
             "description_snippet": "Song: Lose Control", "video_id": "v1",
             "channel": "FitChan"},
        ]
        music = extract_music_from_videos(videos)
        assert len(music) > 0
