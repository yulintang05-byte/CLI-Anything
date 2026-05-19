"""social-trends CLI — viral trend scraping, account optimization, theme page playbook."""

import json
import sys

import click

from cli_anything.social_trends.core import tiktok, youtube, optimizer, theme_page
from cli_anything.social_trends.utils.output import (
    print_json,
    print_table,
    print_section,
    print_list,
)


def _json_flag(ctx_obj: dict) -> bool:
    return ctx_obj.get("json_output", False)


@click.group()
@click.option("--json", "json_output", is_flag=True, default=False, help="Output JSON for agent parsing")
@click.pass_context
def cli(ctx, json_output):
    """social-trends: scrape viral trends, optimize accounts, build theme pages."""
    ctx.ensure_object(dict)
    ctx.obj["json_output"] = json_output


# ════════════════════════════════════════════════════════════════
# TIKTOK COMMANDS
# ════════════════════════════════════════════════════════════════

@cli.group()
def tt():
    """TikTok trending data."""


@tt.command("trends")
@click.option("--count", default=20, show_default=True, help="Number of trending videos to fetch")
@click.pass_context
def tt_trends(ctx, count):
    """Fetch trending TikTok videos from For You Page."""
    videos = tiktok.get_trending_videos(count=count)
    if _json_flag(ctx.obj):
        print_json({"tiktok_trending_videos": videos})
    else:
        print_section("TikTok Trending Videos")
        print_table(
            videos,
            columns=["username", "view_count", "like_count", "share_count", "music_title"],
        )
        print(f"\nFetched {len(videos)} videos.")


@tt.command("hashtags")
@click.option("--count", default=30, show_default=True, help="Number of trending hashtags")
@click.pass_context
def tt_hashtags(ctx, count):
    """Fetch trending TikTok hashtag challenges."""
    tags = tiktok.get_trending_hashtags(count=count)
    if _json_flag(ctx.obj):
        print_json({"tiktok_trending_hashtags": tags})
    else:
        print_section("TikTok Trending Hashtags")
        print_table(tags, columns=["hashtag", "video_count", "view_count"])


@tt.command("sounds")
@click.option("--count", default=20, show_default=True, help="Number of trending sounds")
@click.pass_context
def tt_sounds(ctx, count):
    """Fetch trending TikTok music/sounds from FYP."""
    sounds = tiktok.get_trending_sounds(count=count)
    if _json_flag(ctx.obj):
        print_json({"tiktok_trending_sounds": sounds})
    else:
        print_section("TikTok Trending Sounds")
        print_table(sounds, columns=["title", "author", "video_count", "duration"])


@tt.command("report")
@click.option("--count", default=20, show_default=True)
@click.pass_context
def tt_report(ctx, count):
    """Full TikTok trend report: videos + hashtags + sounds."""
    videos = tiktok.get_trending_videos(count=count)
    hashtags = tiktok.get_trending_hashtags(count=30)
    sounds = tiktok.get_trending_sounds(count=20)
    top_tags = tiktok.extract_top_hashtags(videos, top_n=20)
    result = {
        "trending_videos": videos,
        "trending_hashtags": hashtags,
        "trending_sounds": sounds,
        "top_hashtags_from_videos": top_tags,
    }
    if _json_flag(ctx.obj):
        print_json(result)
    else:
        print_section("TikTok Full Trend Report")
        print("\n[Trending Sounds]")
        print_table(sounds[:10], columns=["title", "author", "video_count"])
        print("\n[Trending Hashtags]")
        print_table(hashtags[:15], columns=["hashtag", "view_count"])
        print("\n[Top Hashtags from Videos]")
        print_table(top_tags[:15], columns=["hashtag", "count"])
        print("\n[Top Videos]")
        print_table(videos[:10], columns=["username", "view_count", "like_count", "description"])


# ════════════════════════════════════════════════════════════════
# YOUTUBE COMMANDS
# ════════════════════════════════════════════════════════════════

@cli.group()
def yt():
    """YouTube trending data (requires YOUTUBE_API_KEY)."""


@yt.command("trends")
@click.option("--region", default="US", show_default=True, help="ISO 3166-1 country code")
@click.option("--count", default=25, show_default=True)
@click.pass_context
def yt_trends(ctx, region, count):
    """Fetch YouTube trending videos for a region."""
    videos = youtube.get_trending_videos(region_code=region, max_results=count)
    if _json_flag(ctx.obj):
        print_json({"youtube_trending_videos": videos})
    else:
        print_section(f"YouTube Trending Videos ({region})")
        print_table(videos, columns=["title", "channel", "view_count", "like_count"])


@yt.command("music")
@click.option("--region", default="US", show_default=True)
@click.option("--count", default=25, show_default=True)
@click.pass_context
def yt_music(ctx, region, count):
    """Fetch trending YouTube Music videos."""
    videos = youtube.get_trending_music(region_code=region, max_results=count)
    if _json_flag(ctx.obj):
        print_json({"youtube_trending_music": videos})
    else:
        print_section(f"YouTube Trending Music ({region})")
        print_table(videos, columns=["title", "channel", "view_count", "like_count"])


@yt.command("hashtags")
@click.option("--region", default="US", show_default=True)
@click.option("--count", default=25, show_default=True)
@click.pass_context
def yt_hashtags(ctx, region, count):
    """Extract top hashtags from trending YouTube videos."""
    videos = youtube.get_trending_videos(region_code=region, max_results=count)
    tags = youtube.extract_top_hashtags(videos, top_n=30)
    if _json_flag(ctx.obj):
        print_json({"youtube_top_hashtags": tags, "source_videos": len(videos)})
    else:
        print_section("YouTube Top Hashtags (from trending)")
        print_table(tags, columns=["hashtag", "count"])


@yt.command("search")
@click.argument("query")
@click.option("--count", default=20, show_default=True)
@click.pass_context
def yt_search(ctx, query, count):
    """Search YouTube for trending videos matching a keyword/hashtag."""
    videos = youtube.search_trending_hashtags(query=query, max_results=count)
    if _json_flag(ctx.obj):
        print_json({"youtube_search_results": videos, "query": query})
    else:
        print_section(f"YouTube Search: {query}")
        print_table(videos, columns=["title", "channel", "view_count", "like_count"])


@yt.command("report")
@click.option("--region", default="US", show_default=True)
@click.pass_context
def yt_report(ctx, region):
    """Full YouTube trend report: videos + music + hashtags."""
    videos = youtube.get_trending_videos(region_code=region, max_results=25)
    music = youtube.get_trending_music(region_code=region, max_results=25)
    tags = youtube.extract_top_hashtags(videos + music, top_n=30)
    result = {
        "region": region,
        "trending_videos": videos,
        "trending_music": music,
        "top_hashtags": tags,
    }
    if _json_flag(ctx.obj):
        print_json(result)
    else:
        print_section(f"YouTube Full Trend Report ({region})")
        print("\n[Trending Videos]")
        print_table(videos[:10], columns=["title", "channel", "view_count"])
        print("\n[Trending Music]")
        print_table(music[:10], columns=["title", "channel", "view_count"])
        print("\n[Top Hashtags]")
        print_table(tags[:20], columns=["hashtag", "count"])


# ════════════════════════════════════════════════════════════════
# ACCOUNT OPTIMIZER
# ════════════════════════════════════════════════════════════════

@cli.group()
def optimize():
    """Account optimization recommendations."""


@optimize.command("posting-times")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.pass_context
def opt_posting_times(ctx, platform):
    """Get best posting windows for a platform."""
    result = optimizer.get_best_posting_times(platform)
    if _json_flag(ctx.obj):
        print_json(result)
    else:
        print_section(f"Best Posting Times: {platform.upper()}")
        print(f"  Cadence:           {result['cadence']}")
        print(f"  Best hours (UTC):  {result['best_hours_utc']}")
        print(f"  Current UTC hour:  {result['current_utc_hour']}")
        print(f"  Next optimal slot: {result['next_optimal_slot_utc']}:00 UTC (in ~{result['hours_until_next_slot']}h)")


@optimize.command("checklist")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.pass_context
def opt_checklist(ctx, platform):
    """Profile optimization checklist for a platform."""
    items = optimizer.get_profile_checklist(platform)
    if _json_flag(ctx.obj):
        print_json({"platform": platform, "checklist": items})
    else:
        print_section(f"Profile Optimization: {platform.upper()}")
        print_list(items)


@optimize.command("caption-hooks")
@click.argument("topic")
@click.option("--count", default=5, show_default=True)
@click.pass_context
def opt_captions(ctx, topic, count):
    """Generate viral caption hooks for a topic."""
    hooks = optimizer.generate_caption_hooks(topic, count=count)
    if _json_flag(ctx.obj):
        print_json({"topic": topic, "hooks": hooks})
    else:
        print_section(f"Caption Hooks: {topic}")
        print_list(hooks)


@optimize.command("hashtag-set")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.option("--niche", multiple=True, help="Your niche hashtags (repeatable)")
@click.pass_context
def opt_hashtags(ctx, platform, niche):
    """Build optimal hashtag set blending trending + niche tags."""
    if platform == "tiktok":
        trending = tiktok.get_trending_hashtags(count=20)
    elif platform == "youtube":
        vids = youtube.get_trending_videos(max_results=20)
        trending = youtube.extract_top_hashtags(vids, top_n=20)
    else:
        trending = tiktok.get_trending_hashtags(count=20)

    result = optimizer.build_hashtag_set(trending, list(niche), platform)
    if _json_flag(ctx.obj):
        print_json({"platform": platform, "hashtag_set": result})
    else:
        print_section(f"Hashtag Set: {platform.upper()}")
        print("  " + "  ".join(result))


@optimize.command("full-report")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.argument("topic")
@click.option("--niche", multiple=True, help="Your niche hashtags (repeatable)")
@click.pass_context
def opt_full_report(ctx, platform, topic, niche):
    """Generate a complete account optimization report."""
    if platform in ("tiktok", "instagram"):
        vids = tiktok.get_trending_videos(count=20)
        tags = tiktok.get_trending_hashtags(count=30)
    else:
        vids = youtube.get_trending_videos(max_results=20)
        tags = youtube.extract_top_hashtags(vids, top_n=30)
        vids = [dict(v, view_count=v.get("view_count", 0)) for v in vids]

    report = optimizer.generate_optimization_report(platform, vids, tags, list(niche), topic)

    if _json_flag(ctx.obj):
        print_json(report)
    else:
        print_section(f"Full Optimization Report: {platform.upper()} / {topic}")
        ps = report["posting_schedule"]
        print(f"\n[Posting Schedule]")
        print(f"  Cadence:           {ps['cadence']}")
        print(f"  Best hours (UTC):  {ps['best_hours_utc']}")
        print(f"  Next slot:         {ps['next_optimal_slot_utc']}:00 UTC (~{ps['hours_until_next_slot']}h)")
        print(f"\n[Recommended Hashtags]")
        print("  " + "  ".join(report["recommended_hashtags"]))
        print(f"\n[Caption Hooks]")
        print_list(report["caption_hooks"])
        print(f"\n[Top Trending Videos]")
        print_table(
            report["top_trending_videos"][:5],
            columns=["username", "view_count", "engagement_rate"],
        )
        print(f"\n[Profile Checklist]")
        print_list(report["profile_checklist"])


# ════════════════════════════════════════════════════════════════
# THEME PAGE COMMANDS
# ════════════════════════════════════════════════════════════════

@cli.group()
def theme():
    """Theme page creation & monetization playbook."""


@theme.command("niches")
@click.option("--keyword", multiple=True, help="Filter niches by keyword (repeatable)")
@click.pass_context
def theme_niches(ctx, keyword):
    """List recommended niches for theme pages."""
    niches = theme_page.get_niche_recommendations(list(keyword)) if keyword else theme_page.NICHES
    if _json_flag(ctx.obj):
        print_json({"niches": niches})
    else:
        print_section("Theme Page Niches")
        print_table(
            niches,
            columns=["niche", "platforms", "avg_cpm", "competition", "growth_speed"],
        )


@theme.command("growth")
@click.pass_context
def theme_growth(ctx):
    """Step-by-step growth playbook for 0 → 100K followers."""
    playbook = theme_page.GROWTH_PLAYBOOK
    if _json_flag(ctx.obj):
        print_json({"growth_playbook": playbook})
    else:
        for phase in playbook:
            print_section(f"{phase['phase']} | {phase['duration']}")
            print(f"  Focus: {phase['focus']}")
            print(f"  Goal:  {phase['goal']}")
            print("  Tactics:")
            print_list(phase["tactics"])


@theme.command("monetize")
@click.pass_context
def theme_monetize(ctx):
    """Monetization methods with requirements and earnings estimates."""
    methods = theme_page.MONETIZATION_METHODS
    if _json_flag(ctx.obj):
        print_json({"monetization_methods": methods})
    else:
        print_section("Monetization Methods")
        for m in methods:
            print(f"\n  ▶ {m['method']}")
            print(f"    Minimum:  {m['minimum']}")
            print(f"    Earnings: {m['earnings']}")
            print(f"    Effort:   {m['effort']}")
            print(f"    Timeline: {m['timeline']}")


@theme.command("content-sources")
@click.pass_context
def theme_sources(ctx):
    """Free & royalty-free content sources for faceless pages."""
    sources = theme_page.CONTENT_SOURCING
    if _json_flag(ctx.obj):
        print_json({"content_sources": sources})
    else:
        print_section("Content Sources for Theme Pages")
        print_table(sources, columns=["source", "type", "license", "url"])


@theme.command("playbook")
@click.pass_context
def theme_playbook(ctx):
    """Complete theme page playbook (all sections)."""
    result = theme_page.get_full_playbook()
    if _json_flag(ctx.obj):
        print_json(result)
    else:
        # Niches
        print_section("Niches")
        print_table(
            result["niches"],
            columns=["niche", "avg_cpm", "competition", "growth_speed"],
        )
        # Growth
        print_section("Growth Phases")
        for phase in result["growth_playbook"]:
            print(f"\n  [{phase['phase']}] {phase['duration']} — Goal: {phase['goal']}")
            print_list(phase["tactics"][:4])
        # Monetize
        print_section("Monetization")
        for m in result["monetization_methods"][:4]:
            print(f"\n  ▶ {m['method']} — {m['earnings']} — {m['timeline']}")
        # Sources
        print_section("Free Content Sources")
        print_table(
            result["content_sourcing"],
            columns=["source", "type", "license"],
        )


# ════════════════════════════════════════════════════════════════
# ALL-PLATFORMS COMBINED REPORT
# ════════════════════════════════════════════════════════════════

@cli.command("all-trends")
@click.option("--region", default="US", show_default=True, help="YouTube region code")
@click.option("--yt/--no-yt", "include_yt", default=True, show_default=True, help="Include YouTube (needs API key)")
@click.pass_context
def all_trends(ctx, region, include_yt):
    """Combined cross-platform trend snapshot (TikTok + YouTube)."""
    result: dict = {}

    click.echo("Fetching TikTok trends...", err=True)
    result["tiktok"] = {
        "trending_videos": tiktok.get_trending_videos(count=20),
        "trending_hashtags": tiktok.get_trending_hashtags(count=30),
        "trending_sounds": tiktok.get_trending_sounds(count=20),
    }
    result["tiktok"]["top_hashtags"] = tiktok.extract_top_hashtags(
        result["tiktok"]["trending_videos"], top_n=20
    )

    if include_yt:
        try:
            click.echo("Fetching YouTube trends...", err=True)
            yt_vids = youtube.get_trending_videos(region_code=region, max_results=25)
            yt_music = youtube.get_trending_music(region_code=region, max_results=25)
            result["youtube"] = {
                "trending_videos": yt_vids,
                "trending_music": yt_music,
                "top_hashtags": youtube.extract_top_hashtags(yt_vids + yt_music, top_n=20),
            }
        except RuntimeError as e:
            result["youtube"] = {"error": str(e)}

    if _json_flag(ctx.obj):
        print_json(result)
    else:
        print_section("Cross-Platform Trend Snapshot")
        print("\n[TikTok Top Sounds]")
        print_table(result["tiktok"]["trending_sounds"][:8], columns=["title", "author", "video_count"])
        print("\n[TikTok Top Hashtags]")
        print_table(result["tiktok"]["trending_hashtags"][:10], columns=["hashtag", "view_count"])
        if "youtube" in result and "error" not in result["youtube"]:
            print("\n[YouTube Trending]")
            print_table(result["youtube"]["trending_videos"][:8], columns=["title", "channel", "view_count"])
            print("\n[YouTube Top Hashtags]")
            print_table(result["youtube"]["top_hashtags"][:10], columns=["hashtag", "count"])
        elif "youtube" in result:
            print(f"\n[YouTube] Skipped — {result['youtube']['error']}")


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
