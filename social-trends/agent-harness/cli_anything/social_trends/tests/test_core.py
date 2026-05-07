"""Unit tests for social-trends core modules."""

import pytest
from cli_anything.social_trends.core.youtube_scraper import (
    _extract_hashtags, _demo_trending, get_trending, get_search_trends, CATEGORIES,
)
from cli_anything.social_trends.core.tiktok_scraper import (
    _extract_hashtags as tt_extract, _demo_trending as tt_demo, get_trending as tt_get_trending, get_hashtag_info,
)
from cli_anything.social_trends.core.hashtag_analyzer import (
    analyze_hashtags, get_niche_hashtags, recommend_for_content, NICHE_HASHTAGS,
    _classify_tier, _build_optimal_set,
)
from cli_anything.social_trends.core.music_tracker import (
    get_trending_music, recommend_music_for_niche, _match_db_track, VIRAL_TRACKS_DB,
)
from cli_anything.social_trends.core.account_optimizer import (
    get_posting_schedule, optimize_bio, get_growth_playbook, audit_account, GROWTH_PLAYBOOKS,
)
from cli_anything.social_trends.core.theme_page_guide import (
    get_niche_guide, get_setup_checklist, get_content_transformation_guide,
    generate_brand_pitch, THEME_PAGE_NICHES, PAGE_SETUP_CHECKLIST,
)


# ===========================================================================
# YouTube Scraper Tests
# ===========================================================================

class TestYouTubeScraper:
    def test_extract_hashtags_from_text(self):
        text = "Check out #fitness and #motivation for your #morningroutine"
        tags = _extract_hashtags(text)
        assert "#fitness" in tags
        assert "#motivation" in tags
        assert "#morningroutine" in tags

    def test_extract_hashtags_empty(self):
        assert _extract_hashtags("") == []
        assert _extract_hashtags(None) == []

    def test_extract_hashtags_no_tags(self):
        assert _extract_hashtags("no hashtags here") == []

    def test_demo_trending_returns_list(self):
        result = _demo_trending(3)
        assert isinstance(result, list)
        assert len(result) == 3

    def test_demo_trending_structure(self):
        result = _demo_trending(1)
        video = result[0]
        assert "id" in video
        assert "title" in video
        assert "platform" in video
        assert video["platform"] == "youtube"
        assert "hashtags" in video

    def test_get_trending_returns_dict(self):
        result = get_trending(region="US", category="all", limit=5)
        assert isinstance(result, dict)
        assert result["platform"] == "youtube"
        assert "videos" in result
        assert "top_hashtags" in result
        assert "fetched_at" in result

    def test_get_trending_fallback_to_demo(self):
        result = get_trending(region="US", limit=5, api_key=None)
        assert len(result["videos"]) > 0

    def test_get_trending_top_hashtags_sorted(self):
        result = get_trending(region="US", limit=10)
        tags = result["top_hashtags"]
        if len(tags) >= 2:
            assert tags[0]["count"] >= tags[1]["count"]

    def test_get_trending_respects_limit(self):
        result = get_trending(region="US", limit=2)
        assert len(result["videos"]) <= 2

    def test_categories_dict_has_all_key(self):
        assert "all" in CATEGORIES
        assert "music" in CATEGORIES

    def test_get_search_trends_structure(self):
        result = get_search_trends("fitness", limit=3)
        assert "query" in result
        assert "results" in result
        assert isinstance(result["results"], list)


# ===========================================================================
# TikTok Scraper Tests
# ===========================================================================

class TestTikTokScraper:
    def test_extract_hashtags(self):
        text = "POV: #gymtok is #viral and #fyp #fitness"
        tags = tt_extract(text)
        assert "#gymtok" in tags
        assert "#viral" in tags

    def test_demo_trending_structure(self):
        result = tt_demo(3)
        assert len(result) == 3
        video = result[0]
        assert "platform" in video
        assert video["platform"] == "tiktok"
        assert "hashtags" in video
        assert "music_title" in video

    def test_get_trending_demo_mode(self):
        result = tt_get_trending(region="US", limit=5)
        assert result["platform"] == "tiktok"
        assert "videos" in result
        assert "top_hashtags" in result
        assert "trending_music" in result

    def test_get_trending_top_hashtags_sorted(self):
        result = tt_get_trending(limit=10)
        tags = result["top_hashtags"]
        if len(tags) >= 2:
            assert tags[0]["count"] >= tags[1]["count"]

    def test_get_hashtag_info_no_key(self):
        result = get_hashtag_info("#fitness", limit=5)
        assert "hashtag" in result
        assert "videos" in result
        assert isinstance(result["videos"], list)

    def test_trending_music_extracted(self):
        result = tt_get_trending(limit=10)
        assert "trending_music" in result
        assert isinstance(result["trending_music"], list)


# ===========================================================================
# Hashtag Analyzer Tests
# ===========================================================================

class TestHashtagAnalyzer:
    def test_analyze_hashtags_basic(self):
        tags = ["#fyp", "#fitness", "#fyp", "#gymtok", "#fitness", "#fitness"]
        result = analyze_hashtags(tags, platform="tiktok")
        assert "ranked_hashtags" in result
        assert result["unique_hashtags"] == 3
        assert result["total_analyzed"] == 6

    def test_analyze_hashtags_ranking(self):
        tags = ["#a", "#a", "#a", "#b", "#b", "#c"]
        result = analyze_hashtags(tags)
        ranked = result["ranked_hashtags"]
        assert ranked[0]["hashtag"] == "#a"
        assert ranked[0]["frequency"] == 3

    def test_analyze_hashtags_with_niche(self):
        tags = ["#fyp"]
        result = analyze_hashtags(tags, niche="fitness")
        assert len(result["suggested_additions"]) > 0

    def test_get_niche_hashtags_valid_niche(self):
        result = get_niche_hashtags("fitness")
        assert "hashtags" in result
        assert len(result["hashtags"]) > 0
        assert result["niche"] == "fitness"

    def test_get_niche_hashtags_invalid_niche(self):
        result = get_niche_hashtags("unknownniche123xyz")
        assert "error" in result
        assert "available_niches" in result

    def test_get_niche_hashtags_all_niches_valid(self):
        for niche in NICHE_HASHTAGS.keys():
            result = get_niche_hashtags(niche)
            assert "hashtags" in result
            assert len(result["hashtags"]) > 0, f"Empty hashtags for niche: {niche}"

    def test_recommend_for_content(self):
        result = recommend_for_content("morning gym workout routine", platform="tiktok")
        assert "recommended_hashtags" in result
        assert "copy_paste" in result
        assert len(result["recommended_hashtags"]) > 0

    def test_recommend_includes_universal_tags(self):
        result = recommend_for_content("random content")
        assert any("#fyp" in h or "#viral" in h for h in result["recommended_hashtags"])

    def test_classify_tier_mega(self):
        tier = _classify_tier("fyp")
        assert tier["name"] == "mega"

    def test_classify_tier_micro(self):
        tier = _classify_tier("veryspecificnichehashtag2024")
        assert tier["name"] == "micro"

    def test_build_optimal_set_length(self):
        ranked = [{"hashtag": f"#{i}", "frequency": 1, "tier": "mid", "recommended": True} for i in range(25)]
        result = _build_optimal_set(ranked, None)
        assert len(result) <= 20

    def test_strategy_tips_returned(self):
        result = get_niche_hashtags("fitness")
        assert "usage_strategy" in result
        assert len(result["usage_strategy"]) > 0


# ===========================================================================
# Music Tracker Tests
# ===========================================================================

class TestMusicTracker:
    def test_viral_tracks_db_not_empty(self):
        assert len(VIRAL_TRACKS_DB) > 0

    def test_all_tracks_have_required_fields(self):
        required = ["title", "artist", "platforms", "genre", "mood", "tiktok_uses"]
        for track in VIRAL_TRACKS_DB:
            for field in required:
                assert field in track, f"Missing field '{field}' in track: {track.get('title')}"

    def test_get_trending_music_all_platforms(self):
        result = get_trending_music(platform="all", limit=5)
        assert "tracks" in result
        assert len(result["tracks"]) <= 5

    def test_get_trending_music_tiktok(self):
        result = get_trending_music(platform="tiktok", limit=5)
        assert result["platform"] == "tiktok"
        assert "tracks" in result

    def test_get_trending_music_sorted_by_plays(self):
        result = get_trending_music(limit=10)
        tracks = result["tracks"]
        if len(tracks) >= 2:
            assert tracks[0]["tiktok_uses"] >= tracks[1]["tiktok_uses"]

    def test_get_trending_music_genre_filter(self):
        result = get_trending_music(genre="pop", limit=10)
        for track in result["tracks"]:
            assert "pop" in track["genre"].lower()

    def test_recommend_music_for_niche(self):
        result = recommend_music_for_niche("fitness")
        assert "recommended_tracks" in result
        assert len(result["recommended_tracks"]) > 0
        assert result["niche"] == "fitness"

    def test_recommend_music_has_pro_tip(self):
        result = recommend_music_for_niche("luxury")
        assert "pro_tip" in result
        assert len(result["pro_tip"]) > 10

    def test_match_db_track_found(self):
        track = _match_db_track("Espresso")
        assert track is not None
        assert track["artist"] == "Sabrina Carpenter"

    def test_match_db_track_not_found(self):
        track = _match_db_track("NonExistentSong12345XYZ")
        assert track is None

    def test_content_ideas_added_to_results(self):
        result = get_trending_music(limit=5)
        for track in result["tracks"]:
            assert "content_ideas" in track
            assert isinstance(track["content_ideas"], list)

    def test_usage_tips_in_result(self):
        result = get_trending_music(platform="tiktok")
        assert "usage_tips" in result
        assert len(result["usage_tips"]) > 0


# ===========================================================================
# Account Optimizer Tests
# ===========================================================================

class TestAccountOptimizer:
    def test_get_posting_schedule_structure(self):
        result = get_posting_schedule(platform="tiktok")
        assert "weekly_schedule" in result
        assert len(result["weekly_schedule"]) == 7
        assert "content_mix_percent" in result

    def test_posting_schedule_days(self):
        result = get_posting_schedule(platform="tiktok")
        days = [d["day"] for d in result["weekly_schedule"]]
        assert "Monday" in days
        assert "Sunday" in days

    def test_posting_schedule_all_platforms(self):
        for platform in ["tiktok", "youtube", "instagram"]:
            result = get_posting_schedule(platform=platform)
            assert result["platform"] == platform

    def test_optimize_bio_structure(self):
        result = optimize_bio(platform="tiktok", niche="fitness", followers=5000)
        assert "bio" in result
        assert "optimization_score" in result
        assert "checklist" in result
        assert 0 <= result["optimization_score"] <= 100

    def test_optimize_bio_character_limit(self):
        result = optimize_bio(platform="tiktok", niche="luxury")
        assert result["character_count"] > 0

    def test_get_growth_playbook_stages(self):
        stages = [(0, "0-1K"), (500, "0-1K"), (5000, "1K-10K"), (50000, "10K-100K"), (500000, "100K+")]
        for followers, expected_label in stages:
            result = get_growth_playbook(followers)
            assert expected_label in result["label"], f"Wrong label for {followers} followers: {result['label']}"

    def test_growth_playbook_has_actions(self):
        for stage in GROWTH_PLAYBOOKS.values():
            assert "daily_actions" in stage
            assert len(stage["daily_actions"]) > 0

    def test_audit_account_structure(self):
        result = audit_account(
            platform="tiktok", username="@test", follower_count=5000,
            following_count=500, post_count=60, avg_views=2000, avg_likes=150,
        )
        assert "health_score" in result
        assert "metrics" in result
        assert "recommendations" in result
        assert "strengths" in result
        assert "issues" in result
        assert 0 <= result["health_score"] <= 100

    def test_audit_high_engagement(self):
        result = audit_account(
            platform="tiktok", username="@power", follower_count=10000,
            following_count=500, post_count=100, avg_views=50000, avg_likes=5000,
        )
        assert result["metrics"]["engagement_rate_percent"] > 5.0
        assert len(result["strengths"]) > 0

    def test_audit_low_engagement(self):
        result = audit_account(
            platform="tiktok", username="@weak", follower_count=10000,
            following_count=5000, post_count=10, avg_views=100, avg_likes=2,
        )
        assert len(result["issues"]) > 0
        assert len(result["recommendations"]) > 0


# ===========================================================================
# Theme Page Guide Tests
# ===========================================================================

class TestThemePageGuide:
    def test_get_niche_guide_all(self):
        result = get_niche_guide()
        assert "niches" in result
        assert len(result["niches"]) > 0
        assert "total" in result

    def test_get_niche_guide_specific(self):
        result = get_niche_guide("luxury")
        assert "niche" in result
        assert result["niche"] == "Luxury Lifestyle"
        assert "monetization" in result

    def test_get_niche_guide_invalid(self):
        result = get_niche_guide("nonexistentniche99999")
        assert "error" in result
        assert "available_niches" in result

    def test_all_niches_have_required_fields(self):
        required = ["niche", "difficulty", "revenue_potential", "monetization", "content_ideas", "best_platforms"]
        for niche in THEME_PAGE_NICHES:
            for field in required:
                assert field in niche, f"Missing field '{field}' in niche: {niche.get('niche')}"

    def test_setup_checklist_all_phases(self):
        result = get_setup_checklist()
        assert "checklist" in result
        assert len(result["checklist"]) == len(PAGE_SETUP_CHECKLIST)

    def test_setup_checklist_specific_phase(self):
        result = get_setup_checklist(phase=1)
        assert "phase" in result
        assert "steps" in result["phase"]

    def test_setup_checklist_invalid_phase(self):
        result = get_setup_checklist(phase=999)
        assert "checklist" in result

    def test_content_transformation_guide(self):
        result = get_content_transformation_guide()
        assert "methods" in result
        assert len(result["methods"]) > 0
        assert "legal_disclaimer" in result

    def test_content_methods_have_legality(self):
        result = get_content_transformation_guide()
        for method in result["methods"]:
            assert "method" in method
            assert "legality" in method
            assert "effort" in method

    def test_generate_brand_pitch(self):
        result = generate_brand_pitch(
            handle="@mypage", brand_name="Nike", niche="fitness",
            followers=50000, platform="TikTok", avg_engagement=5.0,
            rate=500, name="Alex", email="alex@test.com"
        )
        assert "pitch_email" in result
        assert "Nike" in result["pitch_email"]
        assert "@mypage" in result["pitch_email"]
        assert "tips" in result
        assert len(result["tips"]) > 0

    def test_page_setup_checklist_completeness(self):
        for phase in PAGE_SETUP_CHECKLIST:
            assert "phase" in phase
            assert "steps" in phase
            assert len(phase["steps"]) >= 3
