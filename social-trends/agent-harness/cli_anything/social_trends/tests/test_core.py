"""Unit tests for social-trends core modules.

All tests use synthetic data — no network calls are made.
"""

import pytest
from unittest.mock import patch, MagicMock


# ── youtube_trends ─────────────────────────────────────────────────────────────

class TestYouTubeVideo:
    def _make_video(self, **kwargs):
        from cli_anything.social_trends.core.youtube_trends import YouTubeVideo
        defaults = dict(
            video_id="abc123",
            title="Test Video",
            channel="TestChannel",
            view_count=1_000_000,
            like_count=50_000,
            comment_count=5_000,
            tags=["python", "tutorial", "coding"],
            description_snippet="A test video about Python.",
            published_at="2024-01-15T10:00:00Z",
            duration="10:23",
            category="education",
            thumbnail_url="https://img.youtube.com/vi/abc123/maxresdefault.jpg",
        )
        defaults.update(kwargs)
        return YouTubeVideo(**defaults)

    def test_url_built_from_video_id(self):
        v = self._make_video(video_id="xyz789")
        assert v.url == "https://www.youtube.com/watch?v=xyz789"

    def test_engagement_rate_calculated(self):
        v = self._make_video(view_count=1_000_000, like_count=50_000, comment_count=5_000)
        assert v.engagement_rate == pytest.approx(5.5, abs=0.1)

    def test_engagement_rate_zero_views(self):
        v = self._make_video(view_count=0, like_count=0, comment_count=0)
        assert v.engagement_rate == 0.0

    def test_to_dict_has_required_keys(self):
        v = self._make_video()
        d = v.to_dict()
        required = {"video_id", "title", "channel", "url", "view_count", "like_count",
                    "comment_count", "tags", "duration", "category"}
        assert required.issubset(d.keys())

    def test_to_dict_url_matches_property(self):
        v = self._make_video(video_id="vid001")
        assert v.to_dict()["url"] == v.url


class TestYouTubeHelpers:
    def test_category_id_all(self):
        from cli_anything.social_trends.core.youtube_trends import _category_id
        assert _category_id("all") == "0"

    def test_category_id_music(self):
        from cli_anything.social_trends.core.youtube_trends import _category_id
        assert _category_id("music") == "10"

    def test_category_id_unknown_returns_zero(self):
        from cli_anything.social_trends.core.youtube_trends import _category_id
        assert _category_id("does_not_exist") == "0"

    def test_format_duration_minutes_seconds(self):
        from cli_anything.social_trends.core.youtube_trends import _format_duration
        assert _format_duration("PT4M13S") == "4:13"

    def test_format_duration_hours(self):
        from cli_anything.social_trends.core.youtube_trends import _format_duration
        assert _format_duration("PT1H30M5S") == "1:30:05"

    def test_format_duration_only_seconds(self):
        from cli_anything.social_trends.core.youtube_trends import _format_duration
        assert _format_duration("PT45S") == "0:45"

    def test_extract_top_tags_counts(self):
        from cli_anything.social_trends.core.youtube_trends import YouTubeVideo, extract_top_tags

        def _v(tags):
            return YouTubeVideo(
                video_id="x", title="t", channel="c", view_count=0, like_count=0,
                comment_count=0, tags=tags, description_snippet="", published_at="",
                duration="1:00", category="all", thumbnail_url="",
            )

        videos = [_v(["python", "coding"]), _v(["python", "data"]), _v(["coding"])]
        top = extract_top_tags(videos, top_n=5)
        tag_dict = dict(top)
        assert tag_dict["python"] == 2
        assert tag_dict["coding"] == 2
        assert tag_dict["data"] == 1

    def test_list_categories_returns_list(self):
        from cli_anything.social_trends.core.youtube_trends import list_categories
        cats = list_categories()
        assert isinstance(cats, list)
        assert "music" in cats
        assert "gaming" in cats


# ── tiktok_trends ─────────────────────────────────────────────────────────────

class TestTikTokHashtag:
    def test_to_dict_structure(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokHashtag
        h = TikTokHashtag(name="fitness", post_count=5_000_000, view_count=100_000_000,
                          trend_score=95.0, rank=1, related_hashtags=["gym", "workout"])
        d = h.to_dict()
        assert d["name"] == "fitness"
        assert d["rank"] == 1
        assert "url" in d
        assert "tiktok.com/tag/fitness" in d["url"]


class TestTikTokSound:
    def test_to_dict_url(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokSound
        s = TikTokSound(id="12345", title="Song", artist="Artist", clip_count=200_000,
                        trend_score=90.0, rank=1, duration_seconds=30, cover_url="")
        d = s.to_dict()
        assert "12345" in d["url"]


class TestTikTokVideo:
    def _make_video(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokVideo
        return TikTokVideo(
            video_id="vid123",
            description="Amazing workout #gym",
            author="fitnessguru",
            play_count=500_000,
            like_count=50_000,
            comment_count=2_000,
            share_count=8_000,
            hashtags=["gym", "fitness"],
            music_title="Eye of the Tiger",
            music_artist="Survivor",
            cover_url="",
        )

    def test_engagement_rate(self):
        v = self._make_video()
        rate = v.engagement_rate
        assert rate > 0
        assert rate < 100

    def test_to_dict_url(self):
        v = self._make_video()
        d = v.to_dict()
        assert "fitnessguru" in d["url"]
        assert "vid123" in d["url"]

    def test_to_dict_music(self):
        v = self._make_video()
        d = v.to_dict()
        assert d["music"]["title"] == "Eye of the Tiger"


class TestTikTokHelpers:
    def test_list_regions(self):
        from cli_anything.social_trends.core.tiktok_trends import list_regions
        regions = list_regions()
        codes = [r[0] for r in regions]
        assert "US" in codes
        assert "GB" in codes

    def test_list_niches(self):
        from cli_anything.social_trends.core.tiktok_trends import list_niches
        niches = list_niches()
        assert "fitness" in niches
        assert "all" in niches


# ── hashtag_analyzer ──────────────────────────────────────────────────────────

class TestHashtagAnalyzer:
    def _make_tt_hashtags(self):
        from cli_anything.social_trends.core.tiktok_trends import TikTokHashtag
        return [
            TikTokHashtag(name="fitness", post_count=10_000_000, view_count=500_000_000, trend_score=90, rank=1),
            TikTokHashtag(name="gym", post_count=5_000_000, view_count=200_000_000, trend_score=80, rank=2),
            TikTokHashtag(name="homeworkout", post_count=500_000, view_count=20_000_000, trend_score=50, rank=3),
        ]

    def test_score_tiktok_hashtags_returns_scores(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_tiktok_hashtags
        tags = self._make_tt_hashtags()
        scores = score_tiktok_hashtags(tags)
        assert len(scores) == 3

    def test_scores_have_valid_range(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_tiktok_hashtags
        tags = self._make_tt_hashtags()
        scores = score_tiktok_hashtags(tags)
        for s in scores:
            assert 0 <= s.reach_score <= 100
            assert 0 <= s.competition_score <= 100

    def test_tags_prefixed_with_hash(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_tiktok_hashtags
        tags = self._make_tt_hashtags()
        scores = score_tiktok_hashtags(tags)
        assert all(s.tag.startswith("#") for s in scores)

    def test_recommended_marked(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_tiktok_hashtags
        # Need at least 10 tags for recommendations to kick in
        from cli_anything.social_trends.core.tiktok_trends import TikTokHashtag
        tags = [
            TikTokHashtag(name=f"tag{i}", post_count=i*100_000, view_count=i*1_000_000,
                          trend_score=float(i*5), rank=i)
            for i in range(1, 15)
        ]
        scores = score_tiktok_hashtags(tags)
        recommended = [s for s in scores if s.recommended]
        assert len(recommended) <= 10

    def test_build_caption_set_respects_count(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_tiktok_hashtags, build_caption_set
        tags = self._make_tt_hashtags()
        scores = score_tiktok_hashtags(tags)
        caption = build_caption_set(scores, platform="tiktok", count=2)
        assert len(caption) <= 2

    def test_build_caption_set_no_duplicates(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_tiktok_hashtags, build_caption_set
        from cli_anything.social_trends.core.tiktok_trends import TikTokHashtag
        tags = [
            TikTokHashtag(name=f"tag{i}", post_count=i*50_000, view_count=i*500_000,
                          trend_score=float(i), rank=i)
            for i in range(1, 20)
        ]
        scores = score_tiktok_hashtags(tags)
        caption = build_caption_set(scores, count=15)
        assert len(caption) == len(set(caption))

    def test_suggest_for_niche_fitness(self):
        from cli_anything.social_trends.core.hashtag_analyzer import suggest_for_niche
        tags = suggest_for_niche("fitness", count=10)
        assert len(tags) == 10
        assert any("fitness" in t or "gym" in t or "workout" in t for t in tags)

    def test_suggest_for_unknown_niche_returns_generic(self):
        from cli_anything.social_trends.core.hashtag_analyzer import suggest_for_niche
        tags = suggest_for_niche("unicorn_niche_xyz", count=5)
        assert len(tags) == 5

    def test_score_youtube_tags(self):
        from cli_anything.social_trends.core.hashtag_analyzer import score_youtube_tags
        tag_counts = [("python", 10), ("coding", 7), ("tutorial", 5)]
        scores = score_youtube_tags(tag_counts)
        assert len(scores) == 3
        assert all(s.platform == "youtube" for s in scores)

    def test_merge_platform_scores_cross_platform(self):
        from cli_anything.social_trends.core.hashtag_analyzer import (
            score_tiktok_hashtags, score_youtube_tags, merge_platform_scores,
            HashtagScore,
        )
        from cli_anything.social_trends.core.tiktok_trends import TikTokHashtag

        tt = [TikTokHashtag(name="fitness", post_count=10_000_000, view_count=500_000_000, trend_score=90, rank=1)]
        yt = [("fitness", 15), ("coding", 5)]
        tt_scores = score_tiktok_hashtags(tt)
        yt_scores = score_youtube_tags(yt)
        merged = merge_platform_scores(tt_scores, yt_scores)
        fitness_entry = next((s for s in merged if "fitness" in s.tag), None)
        assert fitness_entry is not None
        assert fitness_entry.platform == "both"
        assert fitness_entry.recommended is True


# ── music_tracker ─────────────────────────────────────────────────────────────

class TestMusicTracker:
    def _make_tracks(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry
        return [
            TrackEntry(title="Song A", artist="Artist 1", platform="tiktok",
                       clip_count=2_000_000, trend_score=95.0, duration_seconds=30,
                       cover_url="", track_url="https://tiktok.com/music/1", rank=1),
            TrackEntry(title="Song B", artist="Artist 2", platform="youtube",
                       clip_count=500_000, trend_score=80.0, duration_seconds=0,
                       cover_url="", track_url="https://youtube.com/watch?v=x", rank=2),
        ]

    def test_virality_label_mega(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry
        t = TrackEntry(title="X", artist="Y", platform="tiktok", clip_count=5_000_000,
                       trend_score=99, duration_seconds=30, cover_url="", track_url="", rank=1)
        assert t.virality_label == "MEGA VIRAL"

    def test_virality_label_viral(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry
        t = TrackEntry(title="X", artist="Y", platform="tiktok", clip_count=200_000,
                       trend_score=80, duration_seconds=30, cover_url="", track_url="", rank=1)
        assert t.virality_label == "VIRAL"

    def test_virality_label_trending(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry
        t = TrackEntry(title="X", artist="Y", platform="tiktok", clip_count=50_000,
                       trend_score=60, duration_seconds=30, cover_url="", track_url="", rank=1)
        assert t.virality_label == "TRENDING"

    def test_virality_label_rising(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry
        t = TrackEntry(title="X", artist="Y", platform="tiktok", clip_count=500,
                       trend_score=20, duration_seconds=30, cover_url="", track_url="", rank=1)
        assert t.virality_label == "RISING"

    def test_to_dict_has_rank(self):
        tracks = self._make_tracks()
        d = tracks[0].to_dict()
        assert d["rank"] == 1

    def test_merge_tracks_cross_platform_boost(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry, merge_tracks
        tt = [TrackEntry(title="Viral Song", artist="Big Artist", platform="tiktok",
                         clip_count=1_000_000, trend_score=90, duration_seconds=30,
                         cover_url="", track_url="", rank=1)]
        yt = [TrackEntry(title="Viral Song", artist="Big Artist", platform="youtube",
                         clip_count=5_000_000, trend_score=70, duration_seconds=0,
                         cover_url="", track_url="", rank=1)]
        merged = merge_tracks(tt, yt)
        cross = next((t for t in merged if t.title == "Viral Song"), None)
        assert cross is not None
        assert cross.platform == "both"
        assert cross.trend_score > 90  # boosted

    def test_merge_updates_ranks(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry, merge_tracks
        tt = [TrackEntry(title=f"Song {i}", artist="A", platform="tiktok",
                         clip_count=i*100_000, trend_score=float(i*10),
                         duration_seconds=30, cover_url="", track_url="", rank=i)
              for i in range(1, 4)]
        merged = merge_tracks(tt, [])
        ranks = [t.rank for t in merged]
        assert ranks == sorted(ranks)

    def test_identify_trending_genres_hip_hop(self):
        from cli_anything.social_trends.core.music_tracker import TrackEntry, identify_trending_genres
        tracks = [
            TrackEntry(title="Trap Beat", artist="Rapper", platform="tiktok",
                       clip_count=500_000, trend_score=80, duration_seconds=30,
                       cover_url="", track_url="", rank=1),
            TrackEntry(title="Drill Flow", artist="MC", platform="tiktok",
                       clip_count=300_000, trend_score=70, duration_seconds=30,
                       cover_url="", track_url="", rank=2),
        ]
        genres = identify_trending_genres(tracks)
        assert "hip_hop_rap" in genres


# ── account_optimizer ────────────────────────────────────────────────────────

class TestAccountOptimizer:
    def test_build_checklist_tiktok_not_empty(self):
        from cli_anything.social_trends.core.account_optimizer import build_checklist
        items = build_checklist(platform="tiktok", niche="fitness")
        assert len(items) > 5

    def test_build_checklist_has_critical(self):
        from cli_anything.social_trends.core.account_optimizer import build_checklist
        items = build_checklist(platform="tiktok", niche="gaming")
        priorities = {i.priority for i in items}
        assert "critical" in priorities

    def test_get_posting_schedule_tiktok_sorted(self):
        from cli_anything.social_trends.core.account_optimizer import get_posting_schedule
        slots = get_posting_schedule("tiktok")
        scores = [s.engagement_score for s in slots]
        assert scores == sorted(scores, reverse=True)

    def test_get_posting_schedule_youtube(self):
        from cli_anything.social_trends.core.account_optimizer import get_posting_schedule
        slots = get_posting_schedule("youtube")
        assert len(slots) == 7

    def test_generate_bio_has_templates(self):
        from cli_anything.social_trends.core.account_optimizer import generate_bio
        result = generate_bio(platform="tiktok", niche="fitness", handle="fitnessguru")
        assert len(result["templates"]) >= 1
        assert result["platform"] == "tiktok"
        assert result["niche"] == "fitness"

    def test_generate_bio_contains_niche_keyword(self):
        from cli_anything.social_trends.core.account_optimizer import generate_bio
        result = generate_bio(platform="tiktok", niche="travel")
        assert any("travel" in t.lower() for t in result["templates"])

    def test_optimization_item_to_dict(self):
        from cli_anything.social_trends.core.account_optimizer import OptimizationItem
        item = OptimizationItem(category="Content", action="Post daily",
                                priority="high", impact="Consistency matters")
        d = item.to_dict()
        assert d["category"] == "Content"
        assert d["priority"] == "high"


# ── theme_page ───────────────────────────────────────────────────────────────

class TestThemePage:
    def test_rank_niches_default_sort(self):
        from cli_anything.social_trends.core.theme_page import rank_niches
        niches = rank_niches()
        scores = [n.monetisation_score for n in niches]
        assert scores == sorted(scores, reverse=True)

    def test_rank_niches_by_name(self):
        from cli_anything.social_trends.core.theme_page import rank_niches
        niches = rank_niches(sort_by="name")
        names = [n.name for n in niches]
        assert names == sorted(names)

    def test_niche_database_has_entries(self):
        from cli_anything.social_trends.core.theme_page import NICHE_DATABASE
        assert len(NICHE_DATABASE) >= 5

    def test_niche_to_dict(self):
        from cli_anything.social_trends.core.theme_page import NICHE_DATABASE
        d = NICHE_DATABASE[0].to_dict()
        required = {"name", "monetisation_score", "growth_speed", "competition",
                    "avg_cpm_usd", "affiliate_potential", "shoutout_rate_range_usd",
                    "top_content_types", "best_platforms", "notes"}
        assert required.issubset(d.keys())

    def test_get_theme_page_roadmap_has_6_phases(self):
        from cli_anything.social_trends.core.theme_page import get_theme_page_roadmap
        steps = get_theme_page_roadmap(niche="fitness")
        assert len(steps) == 6

    def test_roadmap_phases_sequential(self):
        from cli_anything.social_trends.core.theme_page import get_theme_page_roadmap
        steps = get_theme_page_roadmap(niche="gaming")
        phases = [s.phase for s in steps]
        assert phases == list(range(1, 7))

    def test_roadmap_step_has_actions(self):
        from cli_anything.social_trends.core.theme_page import get_theme_page_roadmap
        steps = get_theme_page_roadmap(niche="travel")
        assert all(len(s.actions) > 0 for s in steps)

    def test_get_conversion_funnel_has_stages(self):
        from cli_anything.social_trends.core.theme_page import get_conversion_funnel
        funnel = get_conversion_funnel(niche="finance")
        assert len(funnel) >= 4
        stage_names = {f.name for f in funnel}
        assert "Awareness" in stage_names
        assert "Monetisation" in stage_names

    def test_conversion_funnel_has_tools(self):
        from cli_anything.social_trends.core.theme_page import get_conversion_funnel
        funnel = get_conversion_funnel(niche="fitness")
        assert all(len(f.tools) > 0 for f in funnel)

    def test_repost_ethics_guide_not_empty(self):
        from cli_anything.social_trends.core.theme_page import get_repost_ethics_guide
        guide = get_repost_ethics_guide()
        assert len(guide) >= 4
        assert all("rule" in g and "how" in g and "why" in g for g in guide)

    def test_roadmap_step_to_dict(self):
        from cli_anything.social_trends.core.theme_page import get_theme_page_roadmap
        steps = get_theme_page_roadmap(niche="beauty")
        d = steps[0].to_dict()
        assert "phase" in d and "title" in d and "actions" in d and "kpi" in d
