#!/usr/bin/env python3
"""Social Trends CLI — TikTok + YouTube trend scraping, account optimization, theme pages.

QUICK START:
    # Set credentials (optional but recommended)
    export YOUTUBE_API_KEY=your_key_here
    export TIKTOK_SESSION_ID=your_session_id   # optional

    # Scan TikTok for viral trends
    cli-anything-social-trends tiktok scan

    # Scan YouTube for trending content
    cli-anything-social-trends youtube scan

    # Run full cross-platform analysis
    cli-anything-social-trends analyze --region US

    # Optimize your account
    cli-anything-social-trends optimize --handle @yourhandle --platform tiktok --followers 5000

    # Get theme page strategy for a niche
    cli-anything-social-trends theme-page --niche finance

    # Generate a 7-day content plan
    cli-anything-social-trends content-plan --niche fitness --platform tiktok --days 7

    # Interactive REPL
    cli-anything-social-trends repl
"""

import sys
import os
import json

import click

from cli_anything.social_trends.utils.helpers import load_env, save_json, timestamp_filename, format_number
from cli_anything.social_trends.utils.repl_skin import ReplSkin

# Load .env on startup
load_env()

_skin = ReplSkin("social-trends", "1.0.0")
_json_output = False


def _output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    _print_dict(item)
                    click.echo("")
                else:
                    click.echo(f"  • {item}")
        else:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            for item in v:
                if isinstance(item, dict):
                    _print_dict(item, indent + 2)
                else:
                    click.echo(f"{prefix}  • {item}")
        else:
            click.echo(f"{prefix}{k}: {v}")


# ── Root group ─────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON.")
@click.version_option("1.0.0", prog_name="cli-anything-social-trends")
def cli(json_out: bool):
    """Social Trends CLI — viral trend scraping, account optimization, theme pages."""
    global _json_output
    _json_output = json_out


# ── TikTok commands ────────────────────────────────────────────────────

@cli.group("tiktok")
def tiktok_group():
    """TikTok trend scraping commands."""


@tiktok_group.command("scan")
@click.option("--region", default="US", show_default=True, help="Region code (US, GB, IN, etc.).")
@click.option("--hashtags", default=30, show_default=True, help="Number of trending hashtags to fetch.")
@click.option("--sounds", default=20, show_default=True, help="Number of trending sounds to fetch.")
@click.option("--videos", default=30, show_default=True, help="Number of trending videos to analyze.")
@click.option("--save", is_flag=True, help="Save report to JSON file.")
@click.option("--session-id", default="", envvar="TIKTOK_SESSION_ID", help="TikTok session cookie (optional).")
def tiktok_scan(region, hashtags, sounds, videos, save, session_id):
    """Scan TikTok for viral trends, hashtags, and sounds."""
    from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper

    if not _json_output:
        _skin.print_banner()
        _skin.header(f"TikTok Trend Scan — {region}")

    scraper = TikTokScraper(region=region, session_id=session_id or None)
    report = scraper.build_trend_report(
        hashtag_count=hashtags,
        sound_count=sounds,
        video_count=videos,
    )

    if _json_output:
        _output(report.to_dict())
        return

    _skin.header("🔥 Trending Hashtags")
    headers = ["#", "Hashtag", "Views", "Videos"]
    rows = [
        [str(i + 1), f"#{h.name}", format_number(h.view_count), format_number(h.video_count)]
        for i, h in enumerate(report.trending_hashtags[:15])
    ]
    _skin.table(headers, rows)

    _skin.header("🎵 Trending Sounds")
    headers = ["#", "Title", "Artist", "Video Count"]
    rows = [
        [str(i + 1), s.title[:35], s.artist[:25], format_number(s.video_count or s.play_count)]
        for i, s in enumerate(report.trending_sounds[:10])
    ]
    _skin.table(headers, rows)

    _skin.header("📋 Recommended Hashtag Stack")
    click.echo("  " + " ".join(report.recommended_hashtags[:15]))

    _skin.header("🎬 Top Trending Video Hashtags")
    if report.trending_videos:
        all_vt_ht: dict[str, int] = {}
        for v in report.trending_videos:
            for ht in v.hashtags:
                all_vt_ht[ht.lower()] = all_vt_ht.get(ht.lower(), 0) + 1
        top = sorted(all_vt_ht.items(), key=lambda x: x[1], reverse=True)[:20]
        for ht, count in top:
            _skin.info(f"#{ht} — used in {count} trending videos")

    if save:
        fname = timestamp_filename("tiktok_trends")
        save_json(report.to_dict(), fname)
        _skin.success(f"Report saved → {fname}")


@tiktok_group.command("hashtags")
@click.option("--region", default="US", show_default=True)
@click.option("--count", default=30, show_default=True)
def tiktok_hashtags(region, count):
    """Fetch trending TikTok hashtags only."""
    from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
    scraper = TikTokScraper(region=region)
    hashtags = scraper.get_trending_hashtags(count)
    if _json_output:
        _output([h.to_dict() for h in hashtags])
        return
    _skin.header(f"Trending TikTok Hashtags — {region}")
    for i, h in enumerate(hashtags, 1):
        click.echo(f"  {i:2}. #{h.name:<30} {format_number(h.view_count)} views")


@tiktok_group.command("sounds")
@click.option("--region", default="US", show_default=True)
@click.option("--count", default=20, show_default=True)
def tiktok_sounds(region, count):
    """Fetch trending TikTok sounds/music."""
    from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
    scraper = TikTokScraper(region=region)
    sounds = scraper.get_trending_sounds(count)
    if _json_output:
        _output([s.to_dict() for s in sounds])
        return
    _skin.header(f"Trending TikTok Sounds — {region}")
    for i, s in enumerate(sounds, 1):
        click.echo(f"  {i:2}. {s.title:<35} — {s.artist:<25} ({format_number(s.video_count or s.play_count)} videos)")


@tiktok_group.command("search")
@click.argument("keyword")
@click.option("--count", default=10, show_default=True)
def tiktok_search(keyword, count):
    """Search TikTok for hashtags related to a keyword."""
    from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
    scraper = TikTokScraper()
    results = scraper.search_hashtag(keyword, count)
    if _json_output:
        _output([h.to_dict() for h in results])
        return
    _skin.header(f"TikTok Hashtag Search: '{keyword}'")
    for h in results:
        click.echo(f"  #{h.name:<35} {format_number(h.view_count)} views — {h.description[:60]}")


# ── YouTube commands ───────────────────────────────────────────────────

@cli.group("youtube")
def youtube_group():
    """YouTube trend scraping commands."""


@youtube_group.command("scan")
@click.option("--region", default="US", show_default=True, help="Region code.")
@click.option("--count", default=50, show_default=True, help="Number of trending videos.")
@click.option("--category", default="", help="Category ID (10=Music, 17=Sports, 24=Entertainment, etc.).")
@click.option("--save", is_flag=True)
@click.option("--api-key", default="", envvar="YOUTUBE_API_KEY")
def youtube_scan(region, count, category, save, api_key):
    """Scan YouTube for trending videos, music, and hashtags."""
    from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper

    if not _json_output:
        _skin.print_banner()
        _skin.header(f"YouTube Trend Scan — {region}")

    scraper = YouTubeScraper(api_key=api_key or None, region=region)
    report = scraper.build_trend_report(video_count=count)

    if _json_output:
        _output(report.to_dict())
        return

    _skin.header("🎬 Top Trending Videos")
    headers = ["#", "Title", "Channel", "Views", "Category"]
    rows = [
        [
            str(i + 1),
            v.title[:40],
            v.channel[:20],
            format_number(v.view_count),
            v.category_name[:15],
        ]
        for i, v in enumerate(report.trending_videos[:15])
    ]
    _skin.table(headers, rows)

    _skin.header("🎵 Trending Music")
    for i, m in enumerate(report.trending_music[:10], 1):
        click.echo(f"  {i:2}. {m.title:<40} — {m.artist:<25} ({format_number(m.view_count)} views)")

    _skin.header("📊 Trending Categories")
    for cat in report.trending_categories[:8]:
        click.echo(f"  • {cat}")

    _skin.header("🏷️  Top Hashtags")
    click.echo("  " + " ".join(f"#{h}" for h in report.top_hashtags[:20]))

    if save:
        fname = timestamp_filename("youtube_trends")
        save_json(report.to_dict(), fname)
        _skin.success(f"Report saved → {fname}")


@youtube_group.command("music")
@click.option("--region", default="US", show_default=True)
@click.option("--count", default=30, show_default=True)
@click.option("--api-key", default="", envvar="YOUTUBE_API_KEY")
def youtube_music(region, count, api_key):
    """Fetch trending YouTube music videos."""
    from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
    scraper = YouTubeScraper(api_key=api_key or None, region=region)
    music = scraper.get_trending_music(count)
    if _json_output:
        _output([m.to_dict() for m in music])
        return
    _skin.header(f"Trending YouTube Music — {region}")
    for i, m in enumerate(music, 1):
        click.echo(f"  {i:2}. {m.title:<40} — {m.artist:<25} ({format_number(m.view_count)} views)")


# ── Cross-platform analysis ────────────────────────────────────────────

@cli.command("analyze")
@click.option("--region", default="US", show_default=True)
@click.option("--platform", default="all", type=click.Choice(["all", "tiktok", "youtube"]))
@click.option("--save", is_flag=True)
@click.option("--yt-api-key", default="", envvar="YOUTUBE_API_KEY")
@click.option("--tt-session", default="", envvar="TIKTOK_SESSION_ID")
def analyze(region, platform, save, yt_api_key, tt_session):
    """Run cross-platform trend analysis (TikTok + YouTube).

    Identifies trends appearing on both platforms for maximum content impact.
    """
    from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
    from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
    from cli_anything.social_trends.core.trend_analyzer import TrendAnalyzer

    if not _json_output:
        _skin.print_banner()
        _skin.header(f"Cross-Platform Analysis — {region}")

    tt_report = None
    yt_report = None

    if platform in ("all", "tiktok"):
        _skin.info("Scanning TikTok...") if not _json_output else None
        tt_report = TikTokScraper(region=region, session_id=tt_session or None).build_trend_report()

    if platform in ("all", "youtube"):
        _skin.info("Scanning YouTube...") if not _json_output else None
        yt_report = YouTubeScraper(api_key=yt_api_key or None, region=region).build_trend_report()

    analyzer = TrendAnalyzer()
    analysis = analyzer.analyze(tt_report, yt_report)

    if _json_output:
        _output(analysis.to_dict())
        return

    _skin.header("🌍 Cross-Platform Trends")
    headers = ["Keyword", "Platforms", "Score", "Recommendation"]
    rows = [
        [t.keyword[:30], "+".join(t.platforms), f"{t.cross_platform_score:.0f}", t.recommendation[:40]]
        for t in analysis.top_trends[:20]
    ]
    _skin.table(headers, rows)

    _skin.header("🏷️  Best Hashtags to Use Now")
    click.echo("  " + " ".join(analysis.best_hashtags[:20]))

    _skin.header("🎵 Best Sounds to Use Now")
    for s in analysis.best_sounds[:10]:
        _skin.info(s)

    _skin.header("📅 Posting Strategy")
    for tip in analysis.posting_strategy:
        _skin.info(tip)

    _skin.header("💡 Content Ideas")
    for idea in analysis.content_ideas[:10]:
        click.echo(f"  • {idea}")

    if save:
        fname = timestamp_filename("trend_analysis")
        save_json(analysis.to_dict(), fname)
        _skin.success(f"Analysis saved → {fname}")


# ── Account optimizer ──────────────────────────────────────────────────

@cli.command("optimize")
@click.option("--handle", required=True, help="Account handle (e.g. @yourpage).")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--followers", default=0, type=int, help="Current follower count.")
@click.option("--following", default=0, type=int)
@click.option("--avg-views", default=0, type=int, help="Average video views.")
@click.option("--avg-likes", default=0, type=int)
@click.option("--avg-comments", default=0, type=int)
@click.option("--avg-shares", default=0, type=int)
@click.option("--posts-per-week", default=0.0, type=float)
@click.option("--niche", default="", help="Account niche (finance, fitness, luxury, etc.).")
@click.option("--has-link/--no-link", default=False, help="Has link in bio?")
@click.option("--save", is_flag=True)
def optimize(handle, platform, followers, following, avg_views, avg_likes,
             avg_comments, avg_shares, posts_per_week, niche, has_link, save):
    """Audit and optimize a social media account.

    Generates a scored optimization report with critical fixes, content strategy,
    hashtag plan, growth tactics, and monetization opportunities.
    """
    from cli_anything.social_trends.core.account_optimizer import AccountOptimizer, ProfileMetrics

    if not _json_output:
        _skin.print_banner()
        _skin.header(f"Account Optimization: {handle}")

    metrics = ProfileMetrics(
        handle=handle,
        platform=platform,
        followers=followers,
        following=following,
        avg_views=avg_views,
        avg_likes=avg_likes,
        avg_comments=avg_comments,
        avg_shares=avg_shares,
        niche=niche,
        has_link_in_bio=has_link,
        posting_frequency_per_week=posts_per_week,
    )

    optimizer = AccountOptimizer()
    report = optimizer.analyze(metrics)

    if _json_output:
        _output(report.to_dict())
        return

    grade_colors = {"A+": "🟢", "A": "🟢", "B": "🟡", "C": "🟡", "D": "🟠", "F": "🔴", "N/A": "⚪"}
    grade_icon = grade_colors.get(report.grade, "⚪")
    click.echo(f"\n  {grade_icon} OPTIMIZATION GRADE: {report.grade}  ({report.score}/100)\n")

    if report.critical_fixes:
        _skin.header("🚨 Critical Fixes (Do These First)")
        for fix in report.critical_fixes:
            click.echo(f"  {fix}")

    _skin.header("👤 Profile Optimizations")
    for opt in report.profile_optimizations:
        click.echo(f"  {opt}")

    _skin.header("📹 Content Strategy")
    for s in report.content_strategy:
        click.echo(f"  {s}")

    _skin.header("🏷️  Hashtag Strategy")
    for s in report.hashtag_strategy:
        click.echo(f"  {s}")

    _skin.header("📈 Growth Tactics")
    for t in report.growth_tactics:
        click.echo(f"  {t}")

    _skin.header("💰 Monetization Opportunities")
    for m in report.monetization_opportunities:
        click.echo(f"  {m}")

    _skin.header("📊 Estimated Growth")
    click.echo(f"  {report.estimated_growth}")

    if save:
        fname = timestamp_filename(f"optimize_{handle.lstrip('@')}")
        save_json(report.to_dict(), fname)
        _skin.success(f"Report saved → {fname}")


# ── Theme page guide ───────────────────────────────────────────────────

@cli.command("theme-page")
@click.option("--niche", required=True, help="Niche to build theme page around.")
@click.option("--followers", default=0, type=int, help="Current followers (0 = starting from scratch).")
@click.option("--save", is_flag=True)
def theme_page(niche, followers, save):
    """Get a complete strategy for building and monetizing a theme page.

    Covers: niche selection, setup, growth phases, content calendar,
    monetization (shoutouts, affiliate, brand deals, flipping),
    DM scripts, and account valuation.
    """
    from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide

    if not _json_output:
        _skin.print_banner()
        _skin.header(f"Theme Page Strategy: {niche.title()}")

    guide = ThemePageGuide()
    plan = guide.generate_plan(niche, followers)

    if _json_output:
        _output(plan.to_dict())
        return

    _skin.header("📊 Niche Overview")
    for k, v in plan.niche_info.items():
        if isinstance(v, list):
            click.echo(f"  {k}: {', '.join(str(x) for x in v)}")
        else:
            click.echo(f"  {k}: {v}")

    for section in [
        ("🛠️  Phase 1: Setup", plan.phase_1_setup),
        ("📈 Phase 2: Growth", plan.phase_2_growth),
        ("💰 Phase 3: Monetization", plan.phase_3_monetization),
        ("📅 Content Calendar", plan.content_calendar),
        ("💬 DM Scripts", plan.dm_scripts),
        ("⚠️  Red Flags to Avoid", plan.red_flags_to_avoid),
    ]:
        title, items = section
        _skin.header(title)
        for item in items:
            click.echo(f"  {item}")

    _skin.header("💵 Account Valuation")
    click.echo(f"  {plan.account_valuation}")

    if save:
        fname = timestamp_filename(f"theme_page_{niche}")
        save_json(plan.to_dict(), fname)
        _skin.success(f"Plan saved → {fname}")


@cli.command("list-niches")
def list_niches():
    """List all available high-converting theme page niches."""
    from cli_anything.social_trends.core.theme_page_guide import ThemePageGuide
    guide = ThemePageGuide()
    niches = guide.list_niches()
    if _json_output:
        _output(niches)
        return
    _skin.header("High-Converting Niches")
    headers = ["Niche", "Potential", "Difficulty", "Shoutout Rate", "Platforms"]
    rows = [
        [n["name"], n["monetization_potential"], n["difficulty"],
         n["shoutout_rate"], ", ".join(n["best_platforms"][:2])]
        for n in niches
    ]
    _skin.table(headers, rows)


# ── Content plan ───────────────────────────────────────────────────────

@cli.command("content-plan")
@click.option("--niche", required=True, help="Content niche.")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram", "all"]))
@click.option("--days", default=7, show_default=True, help="Days to plan.")
@click.option("--posts-per-day", default=2, show_default=True)
@click.option("--use-trends", is_flag=True, help="Fetch live trends and incorporate them.")
@click.option("--save", is_flag=True)
@click.option("--region", default="US", show_default=True)
@click.option("--yt-api-key", default="", envvar="YOUTUBE_API_KEY")
@click.option("--tt-session", default="", envvar="TIKTOK_SESSION_ID")
def content_plan(niche, platform, days, posts_per_day, use_trends, save, region, yt_api_key, tt_session):
    """Generate a multi-day content calendar with optimized captions and hashtags.

    Add --use-trends to fetch live TikTok/YouTube trends and incorporate them.
    """
    from cli_anything.social_trends.core.content_generator import ContentGenerator

    if not _json_output:
        _skin.print_banner()
        _skin.header(f"Content Plan: {niche.title()} — {days} days on {platform}")

    trending_hashtags = []
    trending_sounds = []

    if use_trends:
        if not _json_output:
            _skin.info("Fetching live trends...")
        try:
            from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
            tt = TikTokScraper(region=region, session_id=tt_session or None)
            tt_report = tt.build_trend_report(hashtag_count=20, sound_count=10)
            trending_hashtags = [h.name for h in tt_report.trending_hashtags[:15]]
            trending_sounds = [f"{s.title} — {s.artist}" for s in tt_report.trending_sounds[:10]]
        except Exception as e:
            if not _json_output:
                _skin.warning(f"Could not fetch TikTok trends: {e}")

    generator = ContentGenerator()
    plan = generator.generate_plan(
        niche=niche,
        platform=platform,
        days=days,
        posts_per_day=posts_per_day,
        trending_hashtags=trending_hashtags,
        trending_sounds=trending_sounds,
    )

    if _json_output:
        _output(plan.to_dict())
        return

    _skin.header("📅 Content Schedule")
    for post in plan.posts:
        click.echo(post.formatted())
        click.echo("")

    _skin.header("♻️  Repurpose Strategy")
    for tip in plan.repurpose_strategy:
        click.echo(f"  {tip}")

    _skin.header("📊 Weekly Tips")
    for tip in plan.weekly_tips:
        click.echo(f"  {tip}")

    if save:
        fname = timestamp_filename(f"content_plan_{niche}")
        save_json(plan.to_dict(), fname)
        _skin.success(f"Content plan saved → {fname}")


# ── Setup / credentials ────────────────────────────────────────────────

@cli.command("setup")
def setup():
    """Interactive setup — configure API keys and credentials."""
    _skin.print_banner()
    _skin.header("Setup — API Keys & Credentials")

    click.echo("""
  YOUTUBE DATA API v3 (free, 10,000 units/day):
    1. Go to: https://console.cloud.google.com/
    2. Create a project → Enable "YouTube Data API v3"
    3. Create API credentials (API Key)
    4. Set: export YOUTUBE_API_KEY=your_key_here
    5. Or add to .env file: YOUTUBE_API_KEY=your_key_here

  TIKTOK SESSION ID (optional, for enhanced scraping):
    1. Open TikTok in Chrome, log into your account
    2. Press F12 → Application → Cookies → www.tiktok.com
    3. Find "sessionid" cookie value
    4. Set: export TIKTOK_SESSION_ID=your_session_id
    5. Or add to .env file: TIKTOK_SESSION_ID=your_session_id

  .ENV FILE FORMAT (create .env in your working directory):
    YOUTUBE_API_KEY=AIzaSy...
    TIKTOK_SESSION_ID=abc123...
""")

    yt_key = os.environ.get("YOUTUBE_API_KEY", "")
    tt_session = os.environ.get("TIKTOK_SESSION_ID", "")

    _skin.status("YouTube API Key", "✓ configured" if yt_key else "✗ not set")
    _skin.status("TikTok Session ID", "✓ configured" if tt_session else "✗ not set (optional)")

    if yt_key:
        _skin.success("YouTube API ready — run: cli-anything-social-trends youtube scan")
    else:
        _skin.warning("Set YOUTUBE_API_KEY to enable YouTube trend scraping")

    _skin.info("Run 'cli-anything-social-trends tiktok scan' (works without credentials)")


# ── REPL ───────────────────────────────────────────────────────────────

@cli.command("repl")
def repl():
    """Launch interactive REPL session."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.completion import WordCompleter
    except ImportError:
        click.echo("prompt-toolkit not installed. Run: pip install prompt-toolkit")
        sys.exit(1)

    _skin.print_banner()
    click.echo("  Type a command or 'help'. Ctrl-C or 'exit' to quit.\n")

    commands = [
        "tiktok scan", "tiktok hashtags", "tiktok sounds", "tiktok search",
        "youtube scan", "youtube music",
        "analyze", "optimize", "theme-page", "list-niches",
        "content-plan", "setup", "help", "exit",
    ]
    completer = WordCompleter(commands, ignore_case=True)
    session: PromptSession = PromptSession(
        history=InMemoryHistory(),
        completer=completer,
    )

    while True:
        try:
            prompt_text = _skin.prompt("social-trends")
            line = session.prompt(prompt_text)
            line = line.strip()
            if not line:
                continue
            if line in ("exit", "quit", "q"):
                break
            if line == "help":
                click.echo(cli.get_help(click.Context(cli)))
                continue

            args = line.split()
            try:
                cli.main(args=args, standalone_mode=False)
            except SystemExit:
                pass
            except click.exceptions.UsageError as e:
                _skin.error(str(e))
            except Exception as e:
                _skin.error(str(e))

        except (KeyboardInterrupt, EOFError):
            break

    _skin.print_goodbye()


# ── Entry point ────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
