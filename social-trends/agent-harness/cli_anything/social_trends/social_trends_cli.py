"""Social Trends CLI — Agent-native viral trend scraper and account optimizer.

Fetches trending content from YouTube and TikTok, provides account optimization
recommendations, and teaches theme page conversion strategies.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)

Commands:
    trends youtube     Fetch YouTube trending videos
    trends tiktok      Fetch TikTok trending videos
    trends hashtags    Get trending hashtags for a platform/niche
    trends music       Get trending music/sounds
    trends all         Aggregate trends from all platforms

    optimize bio       Get bio templates for your platform and niche
    optimize schedule  Get optimal posting schedule
    optimize hashtags  Get hashtag strategy for your niche
    optimize content-plan  Get a 7-day content plan
    optimize checklist     Profile optimization checklist

    theme niches       List profitable theme page niches
    theme strategy     Full strategy for a specific niche
    theme convert      Niche conversion guide
    theme monetize     Monetization strategies for a niche

    auth status        Show configured API keys
    auth set-youtube-key   Set YouTube Data API v3 key
    auth set-tiktok-key    Set TikTok RapidAPI key
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import optimizer as opt_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.utils import youtube_backend as yt
from cli_anything.social_trends.utils import tiktok_backend as tt

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if k in ("items", "content_plan", "checklist", "steps", "niches"):
            count = len(v) if isinstance(v, list) else "?"
            click.echo(f"{pad}{k}: [{count} items — use --json for full output]")
        elif isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst:
        if isinstance(item, dict):
            parts = [f"{k}={v}" for k, v in item.items() if not isinstance(v, (dict, list))]
            click.echo("  " + "  ".join(parts[:6]))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def _mode_badge(mode: str) -> str:
    return f"[{mode.upper()}]"


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RuntimeError, ValueError, KeyError, ImportError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI group ────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="social-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """social-trends — viral trend scraper and account optimizer.

    \b
    Scrape YouTube + TikTok trending videos, hashtags, and music.
    Optimize your social media accounts and learn theme page strategies.

    \b
    Quick start:
      social-trends trends all                        # All trends at once
      social-trends trends youtube --limit 10         # YouTube top 10
      social-trends trends tiktok --limit 10          # TikTok top 10
      social-trends trends music --platform tiktok    # Trending sounds
      social-trends optimize bio --platform tiktok --niche fitness
      social-trends optimize schedule --platform youtube
      social-trends theme niches                      # Profitable niches
      social-trends theme strategy --niche luxury     # Full strategy
      social-trends auth set-youtube-key <KEY>        # Enable live data
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend discovery (youtube, tiktok, hashtags, music, all)."""
    pass


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="Region code (US, GB, IN, etc.)")
@click.option("--category", default="all", show_default=True,
              help="Category: all, music, gaming, entertainment, news, sports, beauty, tech, food, howto")
@click.option("--limit", default=20, show_default=True, type=int, help="Number of results (max 50)")
@click.option("--api-key", default=None, help="YouTube Data API v3 key (overrides config)")
@handle_error
def trends_youtube(region: str, category: str, limit: int, api_key: Optional[str]) -> None:
    """Fetch YouTube trending videos.

    \b
    Examples:
      social-trends trends youtube
      social-trends trends youtube --region GB --category music --limit 10
      social-trends trends youtube --json
    """
    result = yt.fetch_trending_videos(region=region, category=category, limit=limit, api_key=api_key)
    mode = _mode_badge(result["mode"])

    if not _json_output:
        click.echo(f"\n{mode} YouTube Trending — {region} / {category} ({result['total']} results)\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Title", "Channel", "Views", "Likes", "Tags"],
            [
                [
                    str(item["rank"]),
                    item["title"][:40],
                    item["channel"][:20],
                    f"{item['views']:,}",
                    f"{item['likes']:,}",
                    " ".join(item.get("hashtags", [])[:2]),
                ]
                for item in result["items"]
            ]
        )
        if result.get("note"):
            click.echo(f"\n  ℹ  {result['note']}")
    else:
        output(result)


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--limit", default=20, show_default=True, type=int, help="Number of results (max 30)")
@click.option("--api-key", default=None, help="TikTok RapidAPI key (overrides config)")
@handle_error
def trends_tiktok(region: str, limit: int, api_key: Optional[str]) -> None:
    """Fetch TikTok trending videos.

    \b
    Examples:
      social-trends trends tiktok
      social-trends trends tiktok --limit 5 --json
    """
    result = tt.fetch_trending_videos(region=region, limit=limit, api_key=api_key)
    mode = _mode_badge(result["mode"])

    if not _json_output:
        click.echo(f"\n{mode} TikTok Trending — {region} ({result['total']} results)\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Description", "Author", "Plays", "Likes", "Music"],
            [
                [
                    str(item["rank"]),
                    item["desc"][:38],
                    item["author"][:18],
                    f"{item['plays']:,}",
                    f"{item['likes']:,}",
                    item.get("music", "")[:25],
                ]
                for item in result["items"]
            ]
        )
        if result.get("note"):
            click.echo(f"\n  ℹ  {result['note']}")
    else:
        output(result)


@trends.command("hashtags")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              help="Platform to fetch hashtags for")
@click.option("--niche", default=None, help="Niche filter (fitness, finance, beauty, food, travel)")
@click.option("--limit", default=15, show_default=True, type=int, help="Number of hashtags")
@handle_error
def trends_hashtags(platform: str, niche: Optional[str], limit: int) -> None:
    """Get trending hashtags for a platform and niche.

    \b
    Examples:
      social-trends trends hashtags --platform tiktok --niche fitness
      social-trends trends hashtags --platform youtube --niche finance --json
      social-trends trends hashtags --platform all
    """
    results = {}
    platforms = ["youtube", "tiktok"] if platform == "all" else [platform]

    for p in platforms:
        if p == "tiktok":
            results[p] = tt.fetch_trending_hashtags(niche=niche, limit=limit)
        else:
            results[p] = yt.fetch_trending_hashtags(niche=niche, limit=limit)

    if not _json_output:
        for p, data in results.items():
            mode = _mode_badge(data["mode"])
            niche_label = f" / {niche}" if niche else ""
            click.echo(f"\n{mode} {p.capitalize()} Trending Hashtags{niche_label}\n")
            from cli_anything.social_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()

            if p == "tiktok":
                skin.table(
                    ["Tag", "Weekly Posts", "Avg Plays", "Trend", "Competition", "Tip"],
                    [
                        [
                            item["tag"],
                            f"{item.get('weekly_posts', 0):,}",
                            f"{item.get('avg_plays', 0):,}",
                            item.get("trend", ""),
                            item.get("competition", ""),
                            item.get("advice", "")[:35],
                        ]
                        for item in data["items"]
                    ]
                )
            else:
                skin.table(
                    ["Tag", "Weekly Posts", "Avg Views", "Trend", "Competition"],
                    [
                        [
                            item["tag"],
                            f"{item.get('weekly_posts', 0):,}",
                            f"{item.get('avg_views', 0):,}",
                            item.get("trend", ""),
                            item.get("competition", ""),
                        ]
                        for item in data["items"]
                    ]
                )
    else:
        output(results if platform == "all" else results[platform])


@trends.command("music")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              help="Platform")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--limit", default=15, show_default=True, type=int, help="Number of results")
@handle_error
def trends_music(platform: str, region: str, limit: int) -> None:
    """Get trending music and sounds.

    \b
    Examples:
      social-trends trends music
      social-trends trends music --platform youtube --region GB
      social-trends trends music --platform all --limit 10
    """
    results = {}
    platforms = ["youtube", "tiktok"] if platform == "all" else [platform]

    for p in platforms:
        if p == "tiktok":
            results[p] = tt.fetch_trending_sounds(limit=limit)
        else:
            results[p] = yt.fetch_trending_music(region=region, limit=limit)

    if not _json_output:
        for p, data in results.items():
            mode = _mode_badge(data["mode"])
            click.echo(f"\n{mode} {p.capitalize()} Trending {'Sounds' if p == 'tiktok' else 'Music'}\n")
            from cli_anything.social_trends.utils.repl_skin import ReplSkin
            skin = ReplSkin()

            if p == "tiktok":
                skin.table(
                    ["#", "Title", "Artist", "Uses", "Trend", "Mood", "Best For"],
                    [
                        [
                            str(item["rank"]),
                            item["title"][:30],
                            item.get("author", "")[:20],
                            f"{item.get('uses', 0):,}",
                            item.get("trend", ""),
                            item.get("mood", "")[:15],
                            ", ".join(item.get("recommended_content", [])[:2]),
                        ]
                        for item in data["items"]
                    ]
                )
            else:
                skin.table(
                    ["#", "Title", "Artist", "Trend", "BPM", "Mood"],
                    [
                        [
                            str(item["rank"]),
                            item["title"][:30],
                            item.get("artist", "")[:20],
                            item.get("trend", ""),
                            str(item.get("bpm", "")) if item.get("bpm") else "N/A",
                            item.get("mood", "")[:20],
                        ]
                        for item in data["items"]
                    ]
                )
    else:
        output(results if platform == "all" else results[platform])


@trends.command("all")
@click.option("--region", default="US", show_default=True, help="Region code")
@click.option("--limit", default=10, show_default=True, type=int, help="Items per platform")
@handle_error
def trends_all(region: str, limit: int) -> None:
    """Fetch trending content from all platforms in one shot.

    \b
    Examples:
      social-trends trends all
      social-trends trends all --region GB --limit 5
      social-trends trends all --json
    """
    if not _json_output:
        click.echo("Fetching trends from YouTube + TikTok...")
    result = trends_mod.fetch_all_trends(region=region, limit=limit)

    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        click.echo(f"\n{'═'*60}")
        click.echo(f"  TREND REPORT — {region} — {result['fetched_at'][:10]}")
        click.echo(f"{'═'*60}\n")

        click.echo("  📺  YOUTUBE TOP TRENDS")
        skin.table(
            ["#", "Title", "Channel", "Views"],
            [[str(v["rank"]), v["title"][:38], v["channel"][:20], f"{v['views']:,}"]
             for v in result["youtube"]["trending_videos"][:5]]
        )

        click.echo("\n  🎵  YOUTUBE TRENDING MUSIC")
        if result["youtube"]["trending_music"] and isinstance(result["youtube"]["trending_music"][0], dict):
            music_items = result["youtube"]["trending_music"]
            if music_items and "artist" in music_items[0]:
                skin.table(
                    ["#", "Title", "Artist", "BPM", "Trend"],
                    [[str(m["rank"]), m["title"][:30], m.get("artist", "")[:18], str(m.get("bpm", "")), m.get("trend", "")]
                     for m in music_items[:5]]
                )

        click.echo("\n  📱  TIKTOK TOP TRENDS")
        skin.table(
            ["#", "Description", "Author", "Plays"],
            [[str(v["rank"]), v["desc"][:38], v["author"][:18], f"{v['plays']:,}"]
             for v in result["tiktok"]["trending_videos"][:5]]
        )

        click.echo("\n  🔊  TIKTOK TRENDING SOUNDS")
        sounds = result["tiktok"]["trending_sounds"]
        if sounds:
            skin.table(
                ["#", "Title", "Artist", "Uses", "Mood"],
                [[str(s["rank"]), s["title"][:28], s.get("author", "")[:18], f"{s.get('uses', 0):,}", s.get("mood", "")]
                 for s in sounds[:5]]
            )

        click.echo("\n  💡  INSIGHTS")
        for insight in result.get("insights", []):
            click.echo(f"\n  [{insight['type'].upper()}]")
            click.echo(f"  {insight['message']}")
            click.echo(f"  → {insight['action']}")

        click.echo(f"\n{'═'*60}\n")
    else:
        output(result)


# ── optimize group ────────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization (bio, schedule, hashtags, content-plan, checklist)."""
    pass


@optimize.command("bio")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              help="Your platform")
@click.option("--niche", required=True, help="Your content niche (fitness, finance, beauty, travel, etc.)")
@handle_error
def optimize_bio(platform: str, niche: str) -> None:
    """Get optimized bio templates for your platform and niche.

    \b
    Examples:
      social-trends optimize bio --platform tiktok --niche fitness
      social-trends optimize bio --platform youtube --niche finance --json
    """
    result = opt_mod.get_bio_templates(platform=platform, niche=niche)

    if not _json_output:
        click.echo(f"\n  Bio Templates — {platform.capitalize()} / {niche.capitalize()}\n")
        for i, tmpl in enumerate(result["templates"], 1):
            click.echo(f"  Template {i}:")
            click.echo(f"    {tmpl}\n")

        click.echo("  Placeholders:")
        for ph, desc in result["placeholders"].items():
            click.echo(f"    {ph} → {desc}")

        click.echo("\n  Bio Rules:")
        for rule in result["bio_rules"]:
            click.echo(f"    • {rule}")
    else:
        output(result)


@optimize.command("schedule")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              help="Platform")
@click.option("--timezone", default="EST", show_default=True, help="Your timezone abbreviation")
@handle_error
def optimize_schedule(platform: str, timezone: str) -> None:
    """Get the optimal posting schedule for your platform.

    \b
    Examples:
      social-trends optimize schedule --platform tiktok
      social-trends optimize schedule --platform youtube --timezone PST
    """
    result = opt_mod.get_posting_schedule(platform=platform, timezone=timezone)

    if not _json_output:
        click.echo(f"\n  Posting Schedule — {platform.capitalize()}\n")
        click.echo(f"  Frequency: {result['frequency']}")
        click.echo(f"  Best days: {', '.join(result['best_days'])}")
        click.echo(f"  Best times (UTC): {', '.join(result['best_times_utc'])}\n")
        click.echo(f"  Strategy: {result['cadence_tip']}\n")
        click.echo("  Recommended Slots:")
        for slot in result["recommended_slots"]:
            click.echo(f"    {slot['day']} {slot['time']} UTC — {slot['tz_note']}")
        click.echo(f"\n  Pro tip: {result['pro_tip']}")
    else:
        output(result)


@optimize.command("hashtags")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.option("--count", default=15, show_default=True, type=int, help="Number of hashtags")
@handle_error
def optimize_hashtags(niche: str, platform: str, count: int) -> None:
    """Get a hashtag strategy for your niche and platform.

    \b
    Examples:
      social-trends optimize hashtags --niche fitness --platform tiktok
      social-trends optimize hashtags --niche finance --platform youtube --count 20
    """
    result = opt_mod.get_hashtag_recommendations(niche=niche, platform=platform, count=count)

    if not _json_output:
        click.echo(f"\n  Hashtag Strategy — {platform.capitalize()} / {niche.capitalize()}\n")
        click.echo(f"  Recommended mix: {result['strategy']['recommended_mix']}\n")
        click.echo(f"  Low competition:    {', '.join(result['strategy']['low_competition'])}")
        click.echo(f"  Medium competition: {', '.join(result['strategy']['medium_competition'])}")
        click.echo(f"  High competition:   {', '.join(result['strategy']['high_competition'])}\n")
        click.echo("  Rules:")
        for rule in result["rules"]:
            click.echo(f"    • {rule}")
    else:
        output(result)


@optimize.command("content-plan")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="all", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "all"], case_sensitive=False))
@click.option("--days", default=7, show_default=True, type=int, help="Number of days to plan")
@handle_error
def optimize_content_plan(niche: str, platform: str, days: int) -> None:
    """Generate a content plan based on trending formats.

    \b
    Examples:
      social-trends optimize content-plan --niche fitness
      social-trends optimize content-plan --niche finance --platform youtube --days 14
    """
    result = opt_mod.get_content_plan(niche=niche, platform=platform, days=days)

    if not _json_output:
        click.echo(f"\n  {days}-Day Content Plan — {platform.capitalize()} / {niche.capitalize()}\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Day", "Format", "Hook", "Platform"],
            [
                [str(d["day"]), d["format"], d["hook"][:45], d["platform"]]
                for d in result["content_plan"]
            ]
        )
        click.echo("\n  Viral Hook Formulas:")
        for hook in result["viral_hooks"][:5]:
            click.echo(f"    • {hook}")
        click.echo("\n  Pro Tips:")
        for tip in result["pro_tips"][:3]:
            click.echo(f"    • {tip}")
    else:
        output(result)


@optimize.command("checklist")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              help="Platform to optimize")
@handle_error
def optimize_checklist(platform: str) -> None:
    """Get a profile optimization checklist for your platform.

    \b
    Examples:
      social-trends optimize checklist --platform tiktok
      social-trends optimize checklist --platform youtube --json
    """
    result = opt_mod.get_profile_checklist(platform=platform)

    if not _json_output:
        click.echo(f"\n  Profile Optimization Checklist — {platform.capitalize()}\n")
        for i, item in enumerate(result["checklist"], 1):
            click.echo(f"  {i:2d}. [ ] {item['item']}")
            click.echo(f"       → {item['tip']}\n")
        click.echo(f"  {result['impact_summary']}")
    else:
        output(result)


# ── theme group ───────────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page strategies (niches, strategy, convert, monetize)."""
    pass


@theme.command("niches")
@click.option("--filter", "filter_type", default="all", show_default=True,
              type=click.Choice(["all", "growing", "easy", "high_income"], case_sensitive=False),
              help="Filter niches by characteristic")
@handle_error
def theme_niches(filter_type: str) -> None:
    """List profitable theme page niches.

    \b
    Examples:
      social-trends theme niches
      social-trends theme niches --filter easy
      social-trends theme niches --filter high_income --json
    """
    result = theme_mod.list_niches(filter_type=filter_type)

    if not _json_output:
        click.echo(f"\n  Theme Page Niches ({filter_type}) — {result['total']} found\n")
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Difficulty", "Growth", "Monetization", "Avg/Month", "Best Platforms"],
            [
                [
                    n["name"],
                    n["difficulty"],
                    n["growth_speed"],
                    n["monetization_potential"],
                    n["avg_monthly_revenue"],
                    ", ".join(n["best_platforms"][:2]),
                ]
                for n in result["niches"]
            ]
        )
        click.echo("\n  Run: social-trends theme strategy --niche <name>  for a full strategy")
    else:
        output(result)


@theme.command("strategy")
@click.option("--niche", required=True, help="Niche name (e.g., luxury, fitness, finance, beauty)")
@click.option("--platform", default="all", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "all"], case_sensitive=False))
@handle_error
def theme_strategy(niche: str, platform: str) -> None:
    """Get a complete theme page strategy for a niche.

    \b
    Examples:
      social-trends theme strategy --niche luxury
      social-trends theme strategy --niche fitness --platform tiktok
      social-trends theme strategy --niche finance --json
    """
    result = theme_mod.get_niche_strategy(niche=niche, platform=platform)

    if "error" in result:
        _err(result["error"])
        return

    if not _json_output:
        niche_data = result["overview"]
        click.echo(f"\n  Strategy: {result['niche']} Theme Page\n")
        click.echo(f"  Difficulty:          {niche_data['difficulty']}")
        click.echo(f"  Growth speed:        {niche_data['growth_speed']}")
        click.echo(f"  Monetization:        {niche_data['monetization_potential']}")
        click.echo(f"  Avg monthly revenue: {niche_data['avg_monthly_revenue']}")
        click.echo(f"  Best platforms:      {', '.join(niche_data['best_platforms'])}")
        click.echo(f"  Target audience:     {niche_data['target_audience']}\n")

        click.echo("  Quick Start:")
        for step in result["quick_start"]:
            click.echo(f"    {step}")

        click.echo("\n  Content Sources:")
        for src in niche_data["content_sources"]:
            click.echo(f"    • {src}")

        click.echo("\n  Content Formats:")
        for fmt in niche_data["content_formats"]:
            click.echo(f"    • {fmt}")

        click.echo("\n  Top Hashtags:")
        click.echo(f"    {' '.join(niche_data['top_hashtags'])}")

        click.echo("\n  Monetization Roadmap:")
        for step in result["monetization_roadmap"]:
            click.echo(f"    {step}")

        click.echo("\n  Content Mix:")
        for content_type, pct in result["content_mix"].items():
            click.echo(f"    {content_type.capitalize()}: {pct}")

        if result.get("notes"):
            click.echo(f"\n  💡 Note: {result['notes']}")
    else:
        output(result)


@theme.command("convert")
@click.option("--from-niche", "from_niche", default=None, help="Current niche to convert FROM")
@click.option("--to-niche", "to_niche", default=None, help="Target niche to convert TO")
@handle_error
def theme_convert(from_niche: Optional[str], to_niche: Optional[str]) -> None:
    """Get a niche conversion guide (switching your theme page focus).

    \b
    Examples:
      social-trends theme convert                          # General guide
      social-trends theme convert --from-niche luxury --to-niche finance
      social-trends theme convert --json
    """
    result = theme_mod.get_conversion_guide(from_niche=from_niche, to_niche=to_niche)

    if not _json_output:
        if result["type"] == "specific_conversion":
            click.echo(f"\n  Niche Conversion: {from_niche} → {to_niche}\n")
            click.echo(f"  Difficulty:          {result['difficulty']}")
            click.echo(f"  Transition time:     {result['transition_time']}")
            click.echo(f"  Audience retention:  {result['audience_retention']}\n")
            click.echo("  Steps:")
            for i, step in enumerate(result["steps"], 1):
                click.echo(f"    {i}. {step}")
        else:
            guide = result["guide"]
            click.echo("\n  Theme Page Conversion Guide\n")
            click.echo("  Timeline:")
            for period, desc in guide["timeline"].items():
                click.echo(f"    {period.replace('_', ' ').upper()}: {desc}")

            click.echo("\n  Reality Check:")
            rc = guide["reality_check"]
            for k, v in rc.items():
                click.echo(f"    {k.replace('_', ' ').capitalize()}: {v}")

            click.echo(f"\n  {len(guide['steps'])} step guide available — run with --json for full detail")
            click.echo(f"  Or run: social-trends theme convert --json | python3 -m json.tool")
    else:
        output(result)


@theme.command("monetize")
@click.option("--niche", required=True, help="Your niche")
@handle_error
def theme_monetize(niche: str) -> None:
    """Get monetization strategies for a theme page niche.

    \b
    Examples:
      social-trends theme monetize --niche fitness
      social-trends theme monetize --niche finance --json
    """
    result = theme_mod.get_monetization_strategy(niche=niche)

    if "error" in result:
        _err(result["error"])
        return

    if not _json_output:
        click.echo(f"\n  Monetization: {result['niche']}\n")
        click.echo(f"  Potential:          {result['monetization_potential']}")
        click.echo(f"  Avg monthly rev:    {result['avg_monthly_revenue']}\n")

        click.echo("  Revenue Streams:")
        for stream in result["revenue_streams"]:
            click.echo(f"    • {stream}")

        click.echo("\n  Follower Milestones:")
        for milestone, desc in result["follower_milestones"].items():
            click.echo(f"    {milestone.replace('_', ' ').upper()}: {desc}")

        click.echo("\n  Platform Revenue:")
        for platform, desc in result["platform_revenue"].items():
            click.echo(f"    {platform.capitalize()}: {desc}")

        click.echo(f"\n  Fastest path: {result['fastest_monetization']}")
        click.echo(f"  Highest earner: {result['highest_earner']}")
    else:
        output(result)


# ── auth group ────────────────────────────────────────────────────────────────

@cli.group()
def auth():
    """API key management (status, set-youtube-key, set-tiktok-key)."""
    pass


@auth.command("status")
@handle_error
def auth_status() -> None:
    """Show configured API key status.

    \b
    Examples:
      social-trends auth status
      social-trends auth status --json
    """
    yt_key = yt.get_api_key()
    tt_key = tt.get_api_key()

    result = {
        "youtube": {
            "configured": bool(yt_key),
            "source": "env" if bool(yt.is_demo_mode(None) is False and yt_key == yt.get_api_key()) else "config",
            "mode": "live" if yt_key else "demo",
            "key_preview": f"{yt_key[:8]}..." if yt_key and len(yt_key) > 8 else None,
        },
        "tiktok": {
            "configured": bool(tt_key),
            "mode": "live" if tt_key else "demo",
            "key_preview": f"{tt_key[:8]}..." if tt_key and len(tt_key) > 8 else None,
        },
        "config_file": str(yt.CONFIG_FILE),
        "env_vars": {
            "YOUTUBE_API_KEY": "set" if yt_key else "not set",
            "TIKTOK_RAPIDAPI_KEY": "set" if tt_key else "not set",
        },
    }

    if not _json_output:
        click.echo("\n  API Key Status\n")
        click.echo(f"  YouTube Data API v3:  {'✓ Live mode' if yt_key else '✗ Demo mode (set key for live data)'}")
        click.echo(f"  TikTok RapidAPI:      {'✓ Live mode' if tt_key else '✗ Demo mode (set key for live data)'}")
        click.echo(f"\n  Config file: {result['config_file']}")
        click.echo("\n  To enable live data:")
        click.echo("    social-trends auth set-youtube-key <YOUR_YOUTUBE_API_KEY>")
        click.echo("    social-trends auth set-tiktok-key <YOUR_TIKTOK_RAPIDAPI_KEY>")
        click.echo("\n  Get YouTube API key: console.cloud.google.com → YouTube Data API v3")
        click.echo("  Get TikTok key:      rapidapi.com → search 'tiktok scraper'")
    else:
        output(result)


@auth.command("set-youtube-key")
@click.argument("key")
@handle_error
def auth_set_youtube_key(key: str) -> None:
    """Configure your YouTube Data API v3 key.

    \b
    Get your key at: console.cloud.google.com → YouTube Data API v3

    Example:
      social-trends auth set-youtube-key AIzaSyXXXXXXXXXXXXXXXXXX
    """
    yt.set_api_key(key)
    result = {"success": True, "message": "YouTube API key saved", "mode": "live"}
    output(result, "YouTube API key saved. Live mode enabled.")


@auth.command("set-tiktok-key")
@click.argument("key")
@handle_error
def auth_set_tiktok_key(key: str) -> None:
    """Configure your TikTok RapidAPI key.

    \b
    Get your key at: rapidapi.com — search for 'tiktok scraper'
    Recommended APIs: tiktok-scraper7 or tiktok-api6

    Example:
      social-trends auth set-tiktok-key abc123xxxx...
    """
    tt.set_api_key(key)
    result = {"success": True, "message": "TikTok RapidAPI key saved", "mode": "live"}
    output(result, "TikTok RapidAPI key saved. Live mode enabled.")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session.

    \b
    Example:
      social-trends repl
    """
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends youtube [--region US] [--limit 20]": "YouTube trending videos",
        "trends tiktok [--region US] [--limit 20]": "TikTok trending videos",
        "trends hashtags --platform tiktok [--niche fitness]": "Trending hashtags",
        "trends music [--platform tiktok]": "Trending sounds/music",
        "trends all [--region US]": "All trends in one shot",
        "optimize bio --platform tiktok --niche fitness": "Bio templates",
        "optimize schedule --platform tiktok": "Best posting times",
        "optimize hashtags --niche fitness": "Hashtag strategy",
        "optimize content-plan --niche finance": "7-day content plan",
        "optimize checklist --platform tiktok": "Profile optimization checklist",
        "theme niches [--filter easy]": "List profitable niches",
        "theme strategy --niche luxury": "Full niche strategy",
        "theme convert [--from-niche X --to-niche Y]": "Conversion guide",
        "theme monetize --niche fitness": "Monetization strategies",
        "auth status": "Show API key status",
        "auth set-youtube-key <KEY>": "Set YouTube API key",
        "auth set-tiktok-key <KEY>": "Set TikTok RapidAPI key",
        "help": "Show this help",
        "quit / exit": "Exit REPL",
    }

    while True:
        try:
            raw = skin.get_input(pt_session, "social-trends", False)
        except (KeyboardInterrupt, EOFError):
            skin.print_goodbye()
            break

        if not raw:
            continue

        cmd = raw.strip()

        if cmd in ("quit", "exit", "q"):
            skin.print_goodbye()
            break

        if cmd in ("help", "h", "?"):
            skin.help(_repl_commands)
            continue

        try:
            args = shlex.split(cmd)
        except ValueError as e:
            skin.error(f"Parse error: {e}")
            continue

        try:
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except click.exceptions.BadParameter as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
