"""Social Trends CLI — main Click command group."""
import json
import sys
from typing import Optional

import click

from cli_anything.social.utils.output import (
    console, print_banner, print_json, print_table, print_section,
    print_success, print_warning, print_info, print_error,
)
from cli_anything.social.core.youtube_trends    import get_youtube_trends
from cli_anything.social.core.tiktok_trends     import get_tiktok_trends
from cli_anything.social.core.hashtag_analyzer  import (
    build_hashtag_set, cross_platform_trend_merge, generate_hashtag_calendar,
    analyze_competitor_hashtags,
)
from cli_anything.social.core.music_trends      import get_music_trends
from cli_anything.social.core.account_optimizer import (
    optimize_account, optimize_all_platforms, generate_content_calendar,
)
from cli_anything.social.core.theme_page_guide  import get_theme_page_guide


# ── root group ────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def cli(ctx, as_json):
    """Social Trends CLI — scrape viral trends, optimize accounts, and build theme pages."""
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if not as_json:
        print_banner()


# ── youtube group ─────────────────────────────────────────────────────────────

@cli.group()
def youtube():
    """YouTube trending content commands."""


@youtube.command("trends")
@click.option("--category", "-c", default="now",
              type=click.Choice(["now", "music", "gaming", "films"]),
              help="Trending category to scrape")
@click.option("--region", "-r", default="US", help="Country code (US, GB, IN, ...)")
@click.option("--max", "-n", "max_results", default=20, show_default=True,
              help="Max number of trending videos to fetch")
@click.option("--api-key", "-k", envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key (or set YOUTUBE_API_KEY env var)")
@click.pass_context
def youtube_trends(ctx, category, region, max_results, api_key):
    """Scrape YouTube trending videos, hashtags, and music."""
    as_json = ctx.obj.get("as_json")
    print_info(f"Scraping YouTube trending [{category}] for region {region}...")

    data = get_youtube_trends(
        category=category, region=region, max_results=max_results, api_key=api_key
    )

    if as_json:
        print_json(data)
        return

    if "error" in data:
        print_error(data["error"])
        return

    videos = data.get("videos", [])
    if videos:
        print_table(
            f"YouTube Trending — {category.title()} ({data.get('method','yt-dlp')})",
            videos[:10],
            columns=["title", "uploader", "view_count", "url"],
            styles={"title": "bold", "view_count": "cyan"},
        )

    hashtags = data.get("hashtags", [])
    if hashtags:
        print_section("Trending Hashtags", [f"{h['hashtag']} ({h['frequency']}x)" for h in hashtags[:15]], "yellow")

    music = data.get("music", [])
    if music:
        print_section("Trending Music / Artists", [f"{m['title']} by {m['uploader']}" for m in music[:10]], "magenta")

    print_success(f"Found {data.get('count', 0)} trending videos.")


# ── tiktok group ──────────────────────────────────────────────────────────────

@cli.group()
def tiktok():
    """TikTok trending content commands."""


@tiktok.command("trends")
@click.option("--hashtags", "-h", "max_hashtags", default=30, show_default=True,
              help="Max trending hashtags to return")
@click.option("--sounds", "-s", "max_sounds", default=20, show_default=True,
              help="Max trending sounds to return")
@click.pass_context
def tiktok_trends(ctx, max_hashtags, max_sounds):
    """Scrape TikTok trending hashtags and sounds."""
    as_json = ctx.obj.get("as_json")
    print_info("Scraping TikTok trending data (this may take a moment)...")

    data = get_tiktok_trends(max_hashtags=max_hashtags, max_sounds=max_sounds)

    if as_json:
        print_json(data)
        return

    hashtags = data.get("hashtags", [])
    if hashtags:
        print_table(
            "TikTok Trending Hashtags",
            hashtags,
            columns=["hashtag", "views", "source"],
            styles={"hashtag": "bold green", "views": "cyan"},
        )

    sounds = data.get("sounds", [])
    if sounds:
        print_table(
            "TikTok Trending Sounds",
            sounds,
            columns=["title", "artist", "source"],
            styles={"title": "bold magenta"},
        )

    insights = data.get("insights", [])
    if insights:
        print_section("TikTok Insights", insights, "blue")


@tiktok.command("hashtag")
@click.argument("hashtag")
@click.option("--max", "-n", "max_results", default=15, show_default=True)
@click.pass_context
def tiktok_hashtag(ctx, hashtag, max_results):
    """Scrape recent viral videos for a specific TikTok hashtag."""
    from cli_anything.social.core.tiktok_trends import scrape_hashtag_videos
    as_json = ctx.obj.get("as_json")
    print_info(f"Scraping TikTok videos for #{hashtag}...")

    videos = scrape_hashtag_videos(hashtag, max_results=max_results)

    if as_json:
        print_json(videos)
        return

    if videos:
        print_table(
            f"TikTok #{hashtag} — Recent Viral Videos",
            videos,
            columns=["author", "desc", "views", "likes"],
            styles={"views": "bold cyan", "likes": "green"},
        )
    else:
        print_warning(f"No videos found for #{hashtag}. Try without the # symbol.")


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag strategy and analysis commands."""


@hashtags.command("build")
@click.option("--niche",    "-n", default="general", help="Your content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter", "threads"]))
@click.option("--count",    "-c", type=int, default=None, help="Override number of hashtags")
@click.pass_context
def hashtags_build(ctx, niche, platform, count):
    """Build an optimized hashtag set for your niche and platform."""
    as_json = ctx.obj.get("as_json")
    result = build_hashtag_set(niche=niche, platform=platform, count=count)

    if as_json:
        print_json(result)
        return

    console.print(f"\n[bold]Optimized {platform.title()} Hashtags for [cyan]{niche}[/cyan][/bold]")
    console.print(f"Strategy: [dim]{result['strategy']}[/dim]\n")
    console.print("[bold green]Use these:[/bold green] " + "  ".join(result["hashtags"]))
    console.print(f"\n[dim]Count: {result['count']} (optimal: {result['optimal_count']}, max: {result['max_count']})[/dim]")

    breakdown = result.get("breakdown", {})
    for tier, tags in breakdown.items():
        if tags:
            console.print(f"  [dim]{tier:>10}:[/dim] {' '.join(tags)}")


@hashtags.command("calendar")
@click.option("--niche",     "-n", required=True, help="Your content niche")
@click.option("--platforms", "-p", multiple=True, default=["tiktok", "instagram"],
              help="Platforms to generate for (repeatable)")
@click.option("--days",      "-d", default=7, show_default=True, help="Days to generate")
@click.pass_context
def hashtags_calendar(ctx, niche, platforms, days):
    """Generate a 7-day hashtag rotation calendar to avoid shadowban."""
    as_json = ctx.obj.get("as_json")
    calendar = generate_hashtag_calendar(niche=niche, platforms=list(platforms), days=days)

    if as_json:
        print_json(calendar)
        return

    for entry in calendar:
        console.print(f"\n[bold]Day {entry['day']}[/bold]")
        for platform, tags in entry["tags"].items():
            console.print(f"  [cyan]{platform}[/cyan]: {' '.join(tags)}")


@hashtags.command("merge")
@click.pass_context
def hashtags_merge(ctx):
    """Pull live YouTube + TikTok trends and merge cross-platform hashtags."""
    as_json = ctx.obj.get("as_json")
    print_info("Fetching trends from both platforms...")

    yt_data = get_youtube_trends(max_results=20)
    tt_data = get_tiktok_trends(max_hashtags=30)

    merged = cross_platform_trend_merge(yt_data.get("hashtags", []), tt_data.get("hashtags", []))

    if as_json:
        print_json(merged)
        return

    cross  = [h for h in merged if h.get("cross_platform")]
    single = [h for h in merged if not h.get("cross_platform")]

    if cross:
        print_section(
            "Cross-Platform (YouTube + TikTok) — HIGHEST PRIORITY",
            [f"{h['hashtag']} | platforms: {', '.join(h['platforms'])}" for h in cross],
            "bold green",
        )
    print_section(
        "Single-Platform Trending",
        [f"{h['hashtag']} ({', '.join(h.get('platforms', []))})" for h in single[:15]],
        "yellow",
    )


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Trending music & audio analysis commands."""


@music.command("trends")
@click.pass_context
def music_trends(ctx):
    """Show trending music across YouTube and TikTok with action plan."""
    as_json = ctx.obj.get("as_json")
    print_info("Gathering music trends from YouTube + TikTok...")

    yt  = get_youtube_trends(category="music", max_results=20)
    tt  = get_tiktok_trends(max_sounds=20)
    data = get_music_trends(
        yt_music_data=yt.get("music", []),
        tt_sounds_data=tt.get("sounds", []),
    )

    if as_json:
        print_json(data)
        return

    tracks = data.get("trending_tracks", [])
    if tracks:
        print_table(
            "Trending Tracks (Cross-Platform Priority)",
            tracks[:12],
            columns=["title", "artist", "platforms", "cross_platform"],
            styles={"title": "bold magenta", "cross_platform": "bold green"},
        )

    genres = data.get("trending_genres", [])
    if genres:
        print_table(
            "Trending Genres",
            genres,
            columns=["genre", "platform", "use_case"],
        )

    sources = data.get("royalty_free_sources", [])
    if sources:
        print_table(
            "Royalty-Free Music Sources",
            sources,
            columns=["name", "cost", "use", "best_for"],
        )

    actions = data.get("action_items", [])
    if actions:
        print_section("Action Items", actions, "bold yellow")


# ── optimize group ────────────────────────────────────────────────────────────

@cli.group()
def optimize():
    """Account optimization commands."""


@optimize.command("account")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--niche",    "-n", required=True, help="Your content niche")
@click.option("--goal",     "-g", default="growth",
              type=click.Choice(["growth", "monetization", "theme_page"]))
@click.pass_context
def optimize_account_cmd(ctx, platform, niche, goal):
    """Get a full optimization report for one platform."""
    as_json = ctx.obj.get("as_json")
    data = optimize_account(platform=platform, niche=niche, goal=goal)

    if as_json:
        print_json(data)
        return

    sched = data.get("posting_schedule", {})
    console.print(f"\n[bold cyan]Account Optimization — {platform.title()} ({niche})[/bold cyan]")
    console.print(f"Goal: [yellow]{goal}[/yellow]  |  Frequency: [green]{sched.get('frequency','?')}[/green]")
    console.print(f"Best days: {', '.join(sched.get('best_days', []))}")
    for day, times_ in sched.get("best_times", {}).items():
        console.print(f"  {day}: {', '.join(times_)}")

    seo = data.get("seo_tips", [])
    if seo:
        print_section("SEO Tips", seo, "cyan")

    tactics = data.get("growth_tactics", [])
    if tactics:
        print_section("Growth Tactics", tactics, "green")

    quick_wins = data.get("quick_wins", [])
    if quick_wins:
        print_section("Quick Wins (Do These TODAY)", quick_wins, "bold yellow")

    bio = data.get("bio_template", {})
    if bio:
        console.print(f"\n[bold]Bio Formula:[/bold] [italic]{bio.get('formula','')}")
        for ex in bio.get("examples", [])[:2]:
            console.print(f"  [dim]Example:[/dim] {ex}")


@optimize.command("all")
@click.option("--niche", "-n", required=True, help="Your content niche")
@click.option("--goal",  "-g", default="growth",
              type=click.Choice(["growth", "monetization", "theme_page"]))
@click.pass_context
def optimize_all_cmd(ctx, niche, goal):
    """Run optimization across ALL platforms at once."""
    as_json = ctx.obj.get("as_json")
    data = optimize_all_platforms(niche=niche, goal=goal)

    if as_json:
        print_json(data)
        return

    for platform, report in data.items():
        sched = report.get("posting_schedule", {})
        bench = report.get("engagement_benchmarks", {})
        console.print(f"\n[bold cyan]═══ {platform.upper()} ═══[/bold cyan]")
        console.print(f"  Post {sched.get('frequency')} | Best: {', '.join(sched.get('best_days',[]))}")
        console.print(f"  Engagement: good={bench.get('good','?')} | viral={bench.get('viral','?')}")
        quick = report.get("quick_wins", [])
        if quick:
            console.print(f"  [yellow]Quick win:[/yellow] {quick[0]}")


@optimize.command("calendar")
@click.option("--niche",    "-n", required=True, help="Your content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--weeks",    "-w", default=4, show_default=True)
@click.option("--pillars",  "-l", default="4_pillar",
              type=click.Choice(["4_pillar", "3_pillar_growth", "theme_page"]))
@click.pass_context
def optimize_calendar(ctx, niche, platform, weeks, pillars):
    """Generate a content calendar with post ideas."""
    as_json = ctx.obj.get("as_json")
    calendar = generate_content_calendar(niche=niche, platform=platform, weeks=weeks, pillars=pillars)

    if as_json:
        print_json(calendar)
        return

    for entry in calendar[:14]:  # Show first 2 weeks in human mode
        console.print(f"\n[bold]Week {entry['week']} — {entry['day']}[/bold]")
        for post in entry["posts"]:
            console.print(
                f"  [cyan]{post['time']}[/cyan] | [{post['pillar']}] "
                f"[italic]{post['prompt']}[/italic] ({post['type']})"
            )


# ── theme group ───────────────────────────────────────────────────────────────

@cli.group()
def theme():
    """Theme page creation, growth, and monetization guide."""


@theme.command("guide")
@click.option("--niche", "-n", default="business", help="Target niche for recommendations")
@click.pass_context
def theme_guide(ctx, niche):
    """Full theme page blueprint: setup → growth → monetization."""
    as_json = ctx.obj.get("as_json")
    data = get_theme_page_guide(niche=niche)

    if as_json:
        print_json(data)
        return

    niche_info = data.get("niche_analysis", {})
    console.print(f"\n[bold cyan]Theme Page Blueprint — {niche_info.get('niche', niche)} Niche[/bold cyan]")
    console.print(f"  Difficulty:     [yellow]{niche_info.get('difficulty','?')}[/yellow]")
    console.print(f"  Monetization:   [green]{niche_info.get('monetization','?')}[/green]")
    console.print(f"  Avg CPM:        {niche_info.get('avg_cpm','?')}")
    console.print(f"  Best Platforms: {', '.join(niche_info.get('best_platforms', []))}")
    console.print(f"  Affiliate Cos:  {', '.join(niche_info.get('affiliate_cos', []))}")

    phases = data.get("growth_phases", [])
    for phase in phases:
        console.print(f"\n[bold green]{phase['phase']}[/bold green]")
        console.print(f"[dim]Goal:[/dim] {phase['goal']}")
        for action in phase["actions"]:
            console.print(f"  • {action}")

    plan = data.get("30_day_action_plan", [])
    if plan:
        print_table(
            "30-Day Action Plan",
            plan,
            columns=["days", "focus", "task"],
            styles={"focus": "bold yellow"},
        )

    rules = data.get("key_rules", [])
    if rules:
        print_section("Non-Negotiable Rules", rules, "bold red")


@theme.command("niches")
@click.pass_context
def theme_niches(ctx):
    """Compare all high-converting niches side by side."""
    as_json = ctx.obj.get("as_json")
    from cli_anything.social.core.theme_page_guide import HIGH_CONVERTING_NICHES

    if as_json:
        print_json(HIGH_CONVERTING_NICHES)
        return

    print_table(
        "High-Converting Theme Page Niches",
        HIGH_CONVERTING_NICHES,
        columns=["niche", "difficulty", "monetization", "avg_cpm", "best_platforms"],
        styles={"niche": "bold", "monetization": "green", "avg_cpm": "cyan"},
    )


@theme.command("rates")
@click.pass_context
def theme_rates(ctx):
    """Show shoutout rate card and monetization benchmarks."""
    as_json = ctx.obj.get("as_json")
    from cli_anything.social.core.theme_page_guide import MONETIZATION_RATE_CARD

    if as_json:
        print_json(MONETIZATION_RATE_CARD)
        return

    print_table(
        "Paid Shoutout Rate Card",
        MONETIZATION_RATE_CARD["paid_shoutouts"],
        columns=["followers", "tiktok", "instagram", "note"],
        styles={"tiktok": "green", "instagram": "magenta"},
    )

    console.print("\n[bold]Affiliate Commissions[/bold]")
    for brand, rate in MONETIZATION_RATE_CARD["affiliate_commissions"].items():
        console.print(f"  [cyan]{brand:<20}[/cyan] {rate}")

    console.print("\n[bold]Digital Products[/bold]")
    for product, price in MONETIZATION_RATE_CARD["digital_products"].items():
        console.print(f"  [magenta]{product:<30}[/magenta] {price}")


@theme.command("dm-templates")
@click.pass_context
def theme_dm_templates(ctx):
    """Print DM funnel templates for brand outreach and shoutout sales."""
    as_json = ctx.obj.get("as_json")
    from cli_anything.social.core.theme_page_guide import DM_FUNNEL_TEMPLATES

    if as_json:
        print_json(DM_FUNNEL_TEMPLATES)
        return

    for name, template in DM_FUNNEL_TEMPLATES.items():
        console.print(f"\n[bold yellow]{name.replace('_', ' ').title()}[/bold yellow]")
        console.print(f"[italic]{template}[/italic]")


@theme.command("resources")
@click.pass_context
def theme_resources(ctx):
    """List free + paid learning resources and tools for theme page creators."""
    as_json = ctx.obj.get("as_json")
    from cli_anything.social.core.theme_page_guide import LEARNING_RESOURCES

    if as_json:
        print_json(LEARNING_RESOURCES)
        return

    print_table(
        "Free Learning Resources",
        LEARNING_RESOURCES["free"],
        columns=["title", "url_hint", "what"],
    )
    print_table(
        "Essential Tools",
        LEARNING_RESOURCES["tools"],
        columns=["tool", "use"],
        styles={"tool": "bold cyan"},
    )


# ── full scan (all-in-one) ────────────────────────────────────────────────────

@cli.command("scan")
@click.option("--niche",    "-n", default="business", help="Your content niche")
@click.option("--platform", "-p", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.option("--region",   "-r", default="US")
@click.option("--api-key",  "-k", envvar="YOUTUBE_API_KEY")
@click.pass_context
def full_scan(ctx, niche, platform, region, api_key):
    """Run a FULL trend scan: YouTube + TikTok trends, hashtags, music, and account tips."""
    as_json = ctx.obj.get("as_json")
    print_info(f"Running full social media trend scan for niche=[{niche}] platform=[{platform}]...")

    yt   = get_youtube_trends(region=region, max_results=20, api_key=api_key)
    tt   = get_tiktok_trends(max_hashtags=25, max_sounds=15)
    musc = get_music_trends(yt.get("music", []), tt.get("sounds", []))
    optz = optimize_account(platform=platform, niche=niche)
    merged_tags = cross_platform_trend_merge(yt.get("hashtags", []), tt.get("hashtags", []))
    hs   = build_hashtag_set(niche=niche, platform=platform, trending=[t["hashtag"] for t in merged_tags[:5]])

    result = {
        "youtube":         yt,
        "tiktok":          tt,
        "music":           musc,
        "hashtag_set":     hs,
        "merged_hashtags": merged_tags[:20],
        "account_tips":    optz,
    }

    if as_json:
        print_json(result)
        return

    # ── YouTube summary
    console.print("\n[bold cyan]━━━ YOUTUBE TRENDS ━━━[/bold cyan]")
    for v in yt.get("videos", [])[:5]:
        console.print(f"  [{v.get('view_count','?')} views] {v.get('title','')}")

    # ── TikTok summary
    console.print("\n[bold green]━━━ TIKTOK TRENDS ━━━[/bold green]")
    for h in tt.get("hashtags", [])[:8]:
        console.print(f"  {h['hashtag']} ({h.get('views','?')} views)")

    # ── Music
    console.print("\n[bold magenta]━━━ TRENDING MUSIC ━━━[/bold magenta]")
    for t in musc.get("trending_tracks", [])[:5]:
        cross = "🔥 CROSS-PLATFORM" if t.get("cross_platform") else ""
        console.print(f"  \"{t.get('title','?')}\" — {t.get('artist','?')} {cross}")

    # ── Hashtags
    console.print("\n[bold yellow]━━━ YOUR HASHTAG SET ━━━[/bold yellow]")
    console.print("  " + "  ".join(hs.get("hashtags", [])))

    # ── Quick wins
    console.print("\n[bold red]━━━ QUICK WINS (DO TODAY) ━━━[/bold red]")
    for qw in optz.get("quick_wins", [])[:4]:
        console.print(f"  ✓ {qw}")

    print_success("Full scan complete. Run `social-trends --json scan` for machine-readable output.")
