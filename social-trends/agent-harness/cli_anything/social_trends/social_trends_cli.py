"""Social Trends CLI — Agent-native viral trend scraper & account optimizer.

Scrapes YouTube and TikTok for viral trends (hashtags, music, topics),
generates account optimization plans, and provides a complete converting
theme page playbook.

Usage:
    social-trends [--json] <command>
    social-trends  (launches REPL)

Commands:
    youtube trends      Scrape YouTube trending videos & hashtags
    tiktok trends       Scrape TikTok trending hashtags, music & videos
    tiktok music        Scrape TikTok trending sounds/music
    trends summary      Cross-platform trend analysis
    accounts optimize   Generate account optimization plan
    theme niches        List top converting theme page niches
    theme guide         Full theme page setup & monetization playbook
    theme repurpose     Content repurposing guide (1 video → 10+ assets)
    times best          Best posting times per platform
"""

import json
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything.social_trends.core import youtube as yt_mod
from cli_anything.social_trends.core import tiktok as tt_mod
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import accounts as acct_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.utils import display as disp

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            pass  # handled per-command
        elif isinstance(data, dict):
            _print_dict(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{pad}{k}: ({len(v)} items)")
            for item in v[:5]:
                if isinstance(item, str):
                    click.echo(f"{pad}  - {item}")
        else:
            click.echo(f"{pad}{k}: {v}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {type(e).__name__}: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON (machine-readable)")
@click.version_option("1.0.0", prog_name="social-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Social Trends — scrape viral trends and optimize your social accounts.

    \b
    Quick start:
      social-trends tiktok trends            # Top TikTok hashtags & music (US)
      social-trends youtube trends           # YouTube trending videos
      social-trends trends summary           # Cross-platform analysis
      social-trends accounts optimize        # Full account optimization plan
      social-trends theme guide              # Converting theme page playbook

    \b
    Set YOUTUBE_API_KEY env var for richer YouTube data.
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── youtube group ─────────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trend commands (trends, hashtags, categories)."""


@youtube.command("trends")
@click.option("--region", default="US", show_default=True, help="ISO country code (US, GB, CA…)")
@click.option("--category", default="0", show_default=True, help="Category ID. Use 'youtube categories' to list.")
@click.option("--limit", default=25, show_default=True, type=int, help="Max results (1–50)")
@click.option("--api-key", default=None, envvar="YOUTUBE_API_KEY", help="YouTube Data API v3 key")
@handle_error
def youtube_trends(region: str, category: str, limit: int, api_key: Optional[str]) -> None:
    """Scrape YouTube trending videos, hashtags and topics."""
    if not _json_output:
        click.echo(f"Fetching YouTube trending in {region}...")

    videos = yt_mod.fetch_trending(region=region, category=category, max_results=limit, api_key=api_key)

    if not videos:
        _err("No trending videos returned. Check network connectivity.")
        return

    hashtags = yt_mod.extract_trending_hashtags(videos)
    topics = yt_mod.extract_trending_topics(videos)
    seed_mode = videos[0].get("source") == "seed" if videos else False

    result = {
        "region": region,
        "category": yt_mod.CATEGORY_MAP.get(category, "Unknown"),
        "videos_fetched": len(videos),
        "source": videos[0].get("source", "unknown") if videos else "unknown",
        "top_videos": videos,
        "trending_hashtags": hashtags,
        "trending_topics": topics,
    }

    if _json_output:
        output(result)
        return

    disp.section(f"YouTube Trending — {region} ({yt_mod.CATEGORY_MAP.get(category, 'All')})")
    if seed_mode:
        click.echo("  [info] Live YouTube API unavailable — showing curated seed data.")
        click.echo("         Set YOUTUBE_API_KEY env var for live results.\n")
    disp.table(
        ["#", "Title", "Channel", "Views", "Hashtags"],
        [
            [
                str(i + 1),
                v["title"],
                v["channel"],
                disp.num(v["views"]),
                " ".join(v["hashtags"][:3]) or "(none)",
            ]
            for i, v in enumerate(videos[:15])
        ],
    )

    if hashtags:
        disp.section("Trending Hashtags (from video titles/tags)")
        disp.table(
            ["Hashtag", "Appears In"],
            [[h["hashtag"], str(h["count"])] for h in hashtags[:15]],
        )

    if topics:
        disp.section("Hot Topics")
        click.echo("  " + "  |  ".join(topics[:15]))


@youtube.command("categories")
def youtube_categories() -> None:
    """List YouTube video category IDs for use with --category."""
    cats = yt_mod.list_categories()
    if _json_output:
        output(cats)
        return
    disp.table(["ID", "Category"], [[c["id"], c["name"]] for c in cats])


# ── tiktok group ─────────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trend commands (trends, music, creators, videos)."""


@tiktok.command("trends")
@click.option("--region", default="US", show_default=True, help="Country code (US, GB, IN, BR…)")
@click.option("--period", default=7, type=click.Choice(["7", "30", "120"]), show_default=True, help="Days of trend data")
@click.option("--limit", default=20, show_default=True, type=int, help="Results per category")
@handle_error
def tiktok_trends(region: str, period: str, limit: int) -> None:
    """Scrape TikTok trending hashtags, music and videos (via Creative Center)."""
    p = int(period)
    if not _json_output:
        click.echo(f"Fetching TikTok trends in {region} (last {p} days)...")

    data = tt_mod.fetch_all(region=region, period=p)

    if _json_output:
        output(data)
        return

    hashtags = data.get("hashtags", [])
    music = data.get("music", [])
    videos = data.get("videos", [])
    errors = data.get("errors", [])

    if errors:
        for e in errors:
            click.echo(f"  [warn] {e}", err=True)

    seed_mode = hashtags and hashtags[0].get("source") == "seed"
    if seed_mode:
        click.echo("  [info] Live TikTok API unavailable — showing curated seed data.")
        click.echo("         Set TIKTOK_CC_COOKIE env var with your ads.tiktok.com session cookie for live results.\n")

    if hashtags:
        disp.section(f"TikTok Trending Hashtags — {region} ({p}d)")
        disp.table(
            ["Rank", "Hashtag", "Posts", "Views"],
            [
                [
                    str(h.get("rank") or i + 1),
                    h["hashtag"],
                    disp.num(h.get("posts", 0)),
                    disp.num(h.get("views", 0)),
                ]
                for i, h in enumerate(hashtags[:20])
            ],
        )

    if music:
        disp.section(f"TikTok Trending Sounds — {region} ({p}d)")
        disp.table(
            ["Rank", "Track", "Artist", "Used In"],
            [
                [
                    str(m.get("rank") or i + 1),
                    m.get("title", "")[:35],
                    m.get("artist", "")[:25],
                    disp.num(m.get("uses", 0)) + " videos",
                ]
                for i, m in enumerate(music[:15])
            ],
        )

    if videos:
        disp.section(f"Trending Videos — {region}")
        disp.table(
            ["Creator", "Caption", "Views", "Likes", "Music"],
            [
                [
                    v.get("creator", "")[:20],
                    v.get("caption", "")[:30],
                    disp.num(v.get("views", 0)),
                    disp.num(v.get("likes", 0)),
                    v.get("music", "")[:20],
                ]
                for v in videos[:10]
            ],
        )


@tiktok.command("music")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, type=click.Choice(["7", "30", "120"]), show_default=True)
@click.option("--limit", default=30, show_default=True, type=int)
@handle_error
def tiktok_music(region: str, period: str, limit: int) -> None:
    """Scrape trending TikTok music/sounds — perfect for timing your content."""
    p = int(period)
    if not _json_output:
        click.echo(f"Fetching TikTok trending music in {region} (last {p}d)...")

    music = tt_mod.fetch_trending_music(region=region, period=p, limit=limit)

    if _json_output:
        output(music)
        return

    disp.section(f"TikTok Trending Sounds — {region}")
    disp.table(
        ["Rank", "Track", "Artist", "Videos Using It", "Duration"],
        [
            [
                str(m.get("rank") or i + 1),
                m.get("title", "")[:35],
                m.get("artist", "")[:25],
                disp.num(m.get("uses", 0)),
                f"{m.get('duration', 0)}s",
            ]
            for i, m in enumerate(music)
        ],
    )
    click.echo("\n  TIP: Use sounds trending < 72 hours old for maximum algorithm boost.")


@tiktok.command("creators")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, type=click.Choice(["7", "30", "120"]), show_default=True)
@click.option("--limit", default=20, show_default=True, type=int)
@handle_error
def tiktok_creators(region: str, period: str, limit: int) -> None:
    """Scrape trending TikTok creators — find collaboration targets."""
    p = int(period)
    if not _json_output:
        click.echo(f"Fetching TikTok trending creators in {region}...")

    creators = tt_mod.fetch_trending_creators(region=region, period=p, limit=limit)

    if _json_output:
        output(creators)
        return

    disp.section(f"TikTok Trending Creators — {region}")
    disp.table(
        ["Rank", "Username", "Followers", "Avg Views", "Niche"],
        [
            [
                str(c.get("rank") or i + 1),
                c.get("username", "")[:25],
                disp.num(c.get("followers", 0)),
                disp.num(c.get("avg_views", 0)),
                c.get("niche", "")[:20],
            ]
            for i, c in enumerate(creators)
        ],
    )


@tiktok.command("regions")
def tiktok_regions() -> None:
    """List supported TikTok region codes."""
    regions = tt_mod.list_regions()
    if _json_output:
        output(regions)
        return
    disp.table(["Code", "Country"], [[r["code"], r["name"]] for r in regions])


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group("trends")
def trends_group():
    """Cross-platform trend analysis (summary, hashtags, music, times)."""


@trends_group.command("summary")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, type=click.Choice(["7", "30", "120"]), show_default=True)
@click.option("--yt-limit", default=25, type=int, show_default=True)
@click.option("--tt-limit", default=20, type=int, show_default=True)
@click.option("--api-key", default=None, envvar="YOUTUBE_API_KEY")
@handle_error
def trends_summary(region: str, period: str, yt_limit: int, tt_limit: int, api_key: Optional[str]) -> None:
    """Full cross-platform analysis: scrape both platforms and surface key insights."""
    p = int(period)
    if not _json_output:
        click.echo(f"Fetching YouTube + TikTok trends for {region} (last {p}d)...")
        click.echo("  [1/2] Scraping YouTube...")

    yt_videos = yt_mod.fetch_trending(region=region, max_results=yt_limit, api_key=api_key)

    if not _json_output:
        click.echo(f"  [2/2] Scraping TikTok Creative Center...")

    tt_data = tt_mod.fetch_all(region=region, period=p)

    summary = trends_mod.generate_summary(yt_videos, tt_data, region)

    if _json_output:
        output(summary)
        return

    disp.section(f"Cross-Platform Trend Summary — {region}")
    click.echo(f"  YouTube videos: {summary['youtube_videos_analyzed']}  |  TikTok hashtags: {summary['tiktok_hashtags_analyzed']}  |  TikTok videos: {summary['tiktok_videos_analyzed']}")

    if summary["cross_platform_hashtags"]:
        disp.section("Cross-Platform Hashtags (trending on BOTH YouTube + TikTok)")
        disp.table(
            ["Hashtag", "YT Count", "TT Posts", "TT Views"],
            [
                [
                    h["hashtag"],
                    str(h.get("youtube_count", 0)),
                    disp.num(h.get("tiktok_count", 0)),
                    disp.num(h.get("tiktok_views", 0)),
                ]
                for h in summary["cross_platform_hashtags"]
            ],
        )

    if summary["trending_music"]:
        disp.section("Top TikTok Sounds to Use NOW")
        disp.table(
            ["Track", "Artist", "Videos", "Opportunity"],
            [
                [
                    m.get("title", "")[:30],
                    m.get("artist", "")[:20],
                    disp.num(m.get("uses", 0)),
                    m.get("opportunity", "")[:40],
                ]
                for m in summary["trending_music"][:8]
            ],
        )

    if summary["content_opportunities"]:
        disp.section("Top Content Opportunities")
        for opp in summary["content_opportunities"][:6]:
            click.echo(f"\n  TOPIC: #{opp['topic']} (mentioned {opp['mention_count']}x)")
            click.echo(f"    YouTube angle : {opp['angle_youtube']}")
            click.echo(f"    TikTok angle  : {opp['angle_tiktok']}")
            click.echo(f"    Instagram angle: {opp['angle_instagram']}")

    disp.section("Best Posting Times (UTC)")
    times = summary["best_posting_times"]
    for platform, slots in times.items():
        click.echo(f"\n  {platform.upper()}:")
        for slot in slots:
            click.echo(f"    {slot['day']} {slot['time']} — {slot['note']}")


@trends_group.command("hashtags")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, type=click.Choice(["7", "30", "120"]))
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "both"]))
@click.option("--limit", default=30, type=int)
@handle_error
def trends_hashtags(region: str, period: str, platform: str, limit: int) -> None:
    """Get trending hashtags for a specific platform."""
    p = int(period)
    results = []

    if platform in ("tiktok", "both"):
        results.extend(tt_mod.fetch_trending_hashtags(region=region, period=p, limit=limit))

    if platform in ("youtube", "both"):
        vids = yt_mod.fetch_trending(region=region, max_results=limit)
        results.extend(yt_mod.extract_trending_hashtags(vids))

    if _json_output:
        output(results)
        return

    disp.section(f"Trending Hashtags — {platform.upper()} — {region}")
    if not results:
        click.echo("  No results. Check your network connection.")
        return

    if platform == "tiktok" or (platform == "both" and results and "posts" in results[0]):
        disp.table(
            ["Hashtag", "Posts", "Views", "Platform"],
            [
                [
                    h.get("hashtag", h.get("hashtag", "")),
                    disp.num(h.get("posts", h.get("count", 0))),
                    disp.num(h.get("views", 0)),
                    h.get("platform", ""),
                ]
                for h in results[:30]
            ],
        )
    else:
        disp.table(
            ["Hashtag", "Count", "Platform"],
            [[h.get("hashtag", ""), str(h.get("count", 0)), h.get("platform", "")] for h in results[:30]],
        )


# ── accounts group ────────────────────────────────────────────────────────────

@cli.group()
def accounts():
    """Account optimization commands (optimize, all, calendar)."""


@accounts.command("optimize")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram"]), help="Platform to optimize")
@click.option("--niche", required=True, help="Your content niche (e.g., 'fitness', 'personal finance')")
@click.option("--followers", default=0, type=int, show_default=True, help="Current follower count")
@click.option("--region", default="US", show_default=True)
@handle_error
def accounts_optimize(platform: str, niche: str, followers: int, region: str) -> None:
    """Generate a full optimization plan for one account using live trends."""
    if not _json_output:
        click.echo(f"Generating {platform} optimization plan for '{niche}' niche...")

    hashtags = tt_mod.fetch_trending_hashtags(region=region)
    music = tt_mod.fetch_trending_music(region=region)
    yt_vids = yt_mod.fetch_trending(region=region, max_results=20)
    opportunities = trends_mod.top_content_opportunities(yt_vids, hashtags, [])

    plan = acct_mod.optimize_account(
        platform=platform,
        niche=niche,
        trending_hashtags=hashtags,
        trending_music=music,
        opportunities=opportunities,
        current_followers=followers,
    )

    if _json_output:
        output(plan)
        return

    disp.section(f"{plan['platform']} Account Optimization — '{niche}' Niche")

    bio_line = plan.get("bio_formula") or plan.get("channel_art") or plan.get("about_section", "")
    if bio_line:
        click.echo(f"\n  BIO/CHANNEL: {bio_line}")
    if "bio_example" in plan:
        click.echo(f"  EXAMPLE    : {plan['bio_example']}")

    if "content_pillars" in plan:
        disp.section("Content Pillars")
        for pillar in plan["content_pillars"]:
            click.echo(f"  • {pillar}")

    hs = plan.get("hashtag_strategy", {})
    if hs:
        disp.section("Hashtag Strategy")
        click.echo(f"  Formula: {hs.get('formula', '')}")
        click.echo(f"  Niche tags: {' '.join(hs.get('niche_tags', []))}")
        click.echo(f"  Trending tags: {' '.join(hs.get('trending_tags', [])[:5])}")
        click.echo(f"  Broad tags: {' '.join(hs.get('broad_tags', []))}")
        if "caption_template" in hs:
            disp.section("Caption Template")
            click.echo(f"  {hs['caption_template']}")

    sched = plan.get("posting_schedule", {})
    if sched:
        disp.section("Posting Schedule")
        disp.kv_block(sched)

    tactics = plan.get("engagement_tactics", [])
    if tactics:
        disp.section("Engagement Tactics")
        disp.bullet_list(tactics)

    milestones = plan.get("growth_milestones", plan.get("monetization_path", []))
    if milestones:
        disp.section("Growth / Monetization Path")
        if isinstance(milestones, dict):
            for k, v in milestones.items():
                click.echo(f"  {k.replace('_', ' → ')}: {v}")
        else:
            disp.bullet_list(milestones)


@accounts.command("all")
@click.option("--tiktok-niche", default=None, help="TikTok account niche")
@click.option("--youtube-niche", default=None, help="YouTube account niche")
@click.option("--instagram-niche", default=None, help="Instagram account niche")
@click.option("--region", default="US", show_default=True)
@handle_error
def accounts_all(tiktok_niche: Optional[str], youtube_niche: Optional[str], instagram_niche: Optional[str], region: str) -> None:
    """Optimize ALL your accounts at once with live trend data + a weekly content calendar."""
    niches = {
        k: v for k, v in {
            "tiktok": tiktok_niche,
            "youtube": youtube_niche,
            "instagram": instagram_niche,
        }.items() if v
    }
    if not niches:
        _err("Specify at least one niche with --tiktok-niche, --youtube-niche, or --instagram-niche")
        return

    if not _json_output:
        click.echo(f"Fetching live trends and generating optimization for: {', '.join(niches.keys())}...")

    hashtags = tt_mod.fetch_trending_hashtags(region=region)
    music = tt_mod.fetch_trending_music(region=region)
    yt_vids = yt_mod.fetch_trending(region=region, max_results=20)
    opportunities = trends_mod.top_content_opportunities(yt_vids, hashtags, [])

    result = acct_mod.optimize_all_accounts(
        niches=niches,
        trending_hashtags=hashtags,
        trending_music=music,
        opportunities=opportunities,
    )

    if _json_output:
        output(result)
        return

    click.echo(f"\n  Cross-platform tip: {result['cross_platform_tip']}")

    disp.section("Weekly Content Calendar")
    disp.table(
        ["Day", "Content"],
        [[c["day"], c["content"]] for c in result["weekly_content_calendar"]],
    )

    for platform, plan in result.get("plans", {}).items():
        if "error" in plan:
            click.echo(f"\n  [{platform}] Error: {plan['error']}")
            continue
        disp.section(f"{platform.upper()} — {niches.get(platform, '')} niche")
        bio = plan.get("bio_formula") or plan.get("channel_art", "")
        click.echo(f"  Bio: {bio}")
        pillars = plan.get("content_pillars", [])
        if pillars:
            click.echo("  Content pillars:")
            for p in pillars[:3]:
                click.echo(f"    • {p}")


@accounts.command("calendar")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--region", default="US", show_default=True)
@handle_error
def accounts_calendar(niche: str, region: str) -> None:
    """Generate a 7-day content calendar based on live trending data."""
    if not _json_output:
        click.echo("Building content calendar from live trend data...")

    hashtags = tt_mod.fetch_trending_hashtags(region=region)
    music = tt_mod.fetch_trending_music(region=region)

    result = acct_mod._build_calendar({"tiktok": niche}, hashtags, music)

    if _json_output:
        output(result)
        return

    disp.section(f"7-Day Content Calendar — '{niche}'")
    disp.table(["Day", "Content Idea"], [[c["day"], c["content"]] for c in result])


# ── theme group ───────────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page playbook (niches, guide, repurpose)."""


@theme.command("niches")
@click.option("--tier", default="all", type=click.Choice(["all", "high", "medium", "low"]), help="Filter by monetization tier")
@handle_error
def theme_niches(tier: str) -> None:
    """List top converting theme page niches ranked by monetization potential."""
    niches = theme_mod.get_niches(tier)

    if _json_output:
        output(niches)
        return

    disp.section("Top Converting Theme Page Niches")
    for n in niches:
        click.echo(f"\n  {n['niche']}  {n['monetization_potential']}")
        click.echo(f"    Why: {n['why']}")
        click.echo(f"    Best platforms: {', '.join(n['best_platforms'])}")
        click.echo(f"    YouTube RPM: {n.get('avg_rpm_youtube', 'N/A')}")
        click.echo(f"    Affiliate programs: {', '.join(n.get('affiliate_programs', [])[:3])}")


@theme.command("guide")
@click.option("--niche", default="your niche", help="Your chosen niche (personalizes the guide)")
@handle_error
def theme_guide(niche: str) -> None:
    """Full converting theme page setup guide — from zero to monetized."""
    guide = theme_mod.get_setup_guide(niche)

    if _json_output:
        output(guide)
        return

    disp.section("Converting Theme Page Playbook")
    click.echo(f"\n  {guide['overview']}\n")

    for key in ["phase_1_setup", "phase_2_content", "phase_3_growth", "phase_4_convert"]:
        phase = guide.get(key, {})
        disp.section(phase.get("title", key))
        steps = phase.get("steps", [])
        for step in steps:
            click.echo(f"  {step}")

        # Phase-specific extras
        for sub_key in ["sourcing_tools", "tiktok", "instagram", "youtube", "funnel", "cta_templates", "link_in_bio_structure"]:
            sub = phase.get(sub_key, [])
            if sub:
                click.echo(f"\n  [{sub_key.replace('_', ' ').title()}]")
                disp.bullet_list(sub)

    disp.section("Monetization Stack")
    mon = guide["monetization"]
    for tier_key in ["tier_1_beginner", "tier_2_intermediate", "tier_3_advanced"]:
        click.echo(f"\n  {tier_key.replace('_', ' ').title()}:")
        for item in mon.get(tier_key, []):
            click.echo(f"    • {item}")

    disp.section("Income Projections")
    for followers, income in mon["income_projections"].items():
        click.echo(f"  {followers.replace('_', ' ')}: {income}")

    disp.section("Common Mistakes to Avoid")
    for mistake in guide["common_mistakes"]:
        click.echo(f"  ✗ {mistake}")

    disp.section("Tools Stack")
    for category, tools in guide["tools_stack"].items():
        click.echo(f"\n  {category.replace('_', ' ').title()}: {', '.join(tools)}")


@theme.command("repurpose")
@handle_error
def theme_repurpose() -> None:
    """Content repurposing guide — turn 1 video into 10+ assets across all platforms."""
    guide = theme_mod.get_content_repurposing_guide()

    if _json_output:
        output(guide)
        return

    disp.section("Content Repurposing Guide")
    click.echo(f"\n  {guide['core_concept']}\n")

    disp.section("The Repurposing Workflow")
    for step in guide["workflow"]:
        click.echo(f"  {step}")

    disp.section("Platform Specs Cheat Sheet")
    disp.table(
        ["Platform", "Spec"],
        [[k.replace("_", " ").title(), v] for k, v in guide["platform_specs"].items()],
    )

    click.echo(f"\n  Watermark removal: {guide['watermark_removal']}")


# ── times command ─────────────────────────────────────────────────────────────

@cli.command("times")
@handle_error
def best_times() -> None:
    """Show best posting times for TikTok, YouTube, and Instagram (evidence-based, UTC)."""
    times = trends_mod.best_posting_times()

    if _json_output:
        output(times)
        return

    disp.section("Best Posting Times (UTC)")
    for platform, slots in times.items():
        click.echo(f"\n  {platform.upper()}:")
        disp.table(
            ["Day", "Time (UTC)", "Why"],
            [[s["day"], s["time"], s["note"]] for s in slots],
        )


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.history import InMemoryHistory
        ps = PromptSession(history=InMemoryHistory(), auto_suggest=AutoSuggestFromHistory())

        def get_input():
            return ps.prompt("social-trends> ")
    except ImportError:
        def get_input():
            return input("social-trends> ")

    _print_banner()

    while True:
        try:
            raw = get_input()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break

        if not raw:
            continue
        cmd = raw.strip()
        if cmd in ("quit", "exit", "q"):
            click.echo("Goodbye!")
            break
        if cmd in ("help", "h", "?"):
            _print_help()
            continue

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            click.echo(f"  Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            click.echo(f"  Usage error: {e}")
        except Exception as e:
            click.echo(f"  Error: {e}")


def _print_banner():
    click.echo("""
  ╔══════════════════════════════════════════════════════════╗
  ║           Social Trends CLI  v1.0.0                     ║
  ║   YouTube + TikTok trend scraper & account optimizer    ║
  ╚══════════════════════════════════════════════════════════╝
  Type 'help' for commands or 'quit' to exit.
""")


def _print_help():
    click.echo("""
  TRENDING DATA
    youtube trends [--region US] [--category 10]   YouTube trending videos
    tiktok trends [--region US] [--period 7]        TikTok hashtags, music & videos
    tiktok music [--region US]                      Trending TikTok sounds
    tiktok creators [--region US]                   Trending TikTok creators
    trends summary [--region US]                    Cross-platform analysis
    trends hashtags [--platform both]               Hashtag rankings
    times                                           Best posting times (UTC)

  ACCOUNT OPTIMIZATION
    accounts optimize --platform tiktok --niche fitness    Single account plan
    accounts all --tiktok-niche fitness --youtube-niche finance   All accounts
    accounts calendar --niche fitness                       7-day content calendar

  THEME PAGES
    theme niches [--tier high]    Top converting niches
    theme guide [--niche finance] Full setup + monetization playbook
    theme repurpose               1 video → 10+ assets guide

  OPTIONS
    --json    Machine-readable JSON output
    --region  ISO country code (US, GB, CA, IN, BR…)
    --period  7, 30, or 120 days of trend data

  Set YOUTUBE_API_KEY env var for richer YouTube data.
""")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
