"""Trend Scout CLI — YouTube & TikTok viral trend scraper, account optimizer, theme page strategist."""

import sys
import json
import click

from .core.youtube_scraper import YouTubeScraper
from .core.tiktok_scraper import TikTokScraper
from .core.analyzer import TrendAnalyzer
from .core.optimizer import AccountOptimizer
from .core.theme_pages import ThemePageStrategist
from .core.scheduler import ContentScheduler
from .utils.config import (
    load_config, save_config, get_api_key, set_api_key,
    load_accounts, add_account, remove_account, get_api_keys_status,
)
from .utils.output import print_json, print_section, print_hashtag_list, print_account_summary


def _make_analyzer(ctx_obj: dict | None = None) -> TrendAnalyzer:
    obj = ctx_obj or {}
    return TrendAnalyzer(
        youtube_api_key=obj.get("youtube_api_key") or get_api_key("YOUTUBE_API_KEY"),
        tiktok_ms_token=obj.get("tiktok_ms_token") or get_api_key("TIKTOK_MS_TOKEN"),
    )


def _make_optimizer(ctx_obj: dict | None = None) -> AccountOptimizer:
    obj = ctx_obj or {}
    return AccountOptimizer(
        youtube_api_key=obj.get("youtube_api_key") or get_api_key("YOUTUBE_API_KEY"),
        tiktok_ms_token=obj.get("tiktok_ms_token") or get_api_key("TIKTOK_MS_TOKEN"),
    )


# ======================================================================
# Root group
# ======================================================================

@click.group()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--youtube-api-key", envvar="YOUTUBE_API_KEY", help="YouTube Data API v3 key")
@click.option("--tiktok-ms-token", envvar="TIKTOK_MS_TOKEN", help="TikTok ms_token (from cookies)")
@click.option("--region", default="US", show_default=True, help="Region code (US, GB, AU, etc.)")
@click.pass_context
def cli(ctx, as_json, youtube_api_key, tiktok_ms_token, region):
    """Trend Scout — viral trend scraper, account optimizer & theme page strategist.

    Scrapes YouTube and TikTok for trending videos, hashtags, music, and
    sounds, then generates account optimization plans and content calendars.

    \b
    Quick start:
      trend-scout setup                    # configure API keys
      trend-scout trends --niche fitness   # get trending data for fitness
      trend-scout optimize tiktok fitness  # optimize TikTok account
      trend-scout theme-pages guide        # learn theme page strategy
      trend-scout schedule weekly          # generate a content calendar
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    ctx.obj["region"] = region
    ctx.obj["youtube_api_key"] = youtube_api_key
    ctx.obj["tiktok_ms_token"] = tiktok_ms_token


# ======================================================================
# setup
# ======================================================================

@cli.command()
@click.pass_context
def setup(ctx):
    """Configure API keys and check status."""
    status = get_api_keys_status()
    as_json = ctx.obj.get("as_json", False)

    if as_json:
        print_json({"api_keys_configured": status})
        return

    click.echo("\n=== Trend Scout Setup ===\n")
    for key, configured in status.items():
        icon = "✓" if configured else "✗"
        click.echo(f"  {icon} {key}: {'configured' if configured else 'NOT SET'}")

    click.echo("\n--- How to get API keys ---")
    click.echo("  YouTube Data API v3 (free, 10,000 units/day):")
    click.echo("    1. Go to console.cloud.google.com")
    click.echo("    2. Create project → Enable YouTube Data API v3")
    click.echo("    3. Create API key → restrict to YouTube Data API")
    click.echo("    4. Run: trend-scout config set YOUTUBE_API_KEY <your-key>")
    click.echo()
    click.echo("  TikTok ms_token (for live trend scraping):")
    click.echo("    1. Log in to TikTok in Chrome")
    click.echo("    2. DevTools (F12) → Application → Cookies → tiktok.com")
    click.echo("    3. Copy value of 'msToken' cookie")
    click.echo("    4. Run: trend-scout config set TIKTOK_MS_TOKEN <token>")
    click.echo()
    click.echo("  Note: Without API keys, trend-scout uses curated static data")
    click.echo("        which is still useful for hashtag strategies and optimization")


# ======================================================================
# config
# ======================================================================

@cli.group()
def config():
    """Manage configuration and API keys."""


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a configuration value (API key, preference, etc.)."""
    set_api_key(key, value)
    click.echo(f"✓ {key} saved to ~/.cli-anything-trend-scout/config.json")


@config.command("get")
@click.argument("key")
def config_get(key):
    """Get a configuration value."""
    val = get_api_key(key)
    if val:
        masked = val[:4] + "****" + val[-4:] if len(val) > 8 else "****"
        click.echo(f"{key}: {masked}")
    else:
        click.echo(f"{key}: not set")


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show all configuration."""
    status = get_api_keys_status()
    accounts = load_accounts()
    data = {"api_keys_configured": status, "accounts": accounts}
    if ctx.obj.get("as_json"):
        print_json(data)
    else:
        print_section("API Keys", {k: "✓ set" if v else "✗ not set" for k, v in status.items()})
        print_account_summary(accounts)


# ======================================================================
# account
# ======================================================================

@cli.group()
def account():
    """Manage social media accounts."""


@account.command("add")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram", "twitter"], case_sensitive=False))
@click.argument("username")
@click.option("--niche", required=True, help="Content niche (fitness, finance, fashion, etc.)")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--region", default="US", help="Account region")
def account_add(platform, username, niche, followers, region):
    """Add a social media account to manage."""
    acct = add_account(platform, username, niche, followers, region)
    click.echo(f"✓ Added [{platform.upper()}] @{username} ({niche} niche, {followers:,} followers)")


@account.command("list")
@click.pass_context
def account_list(ctx):
    """List all configured accounts."""
    accounts = load_accounts()
    if ctx.obj.get("as_json"):
        print_json(accounts)
    else:
        print_account_summary(accounts)


@account.command("remove")
@click.argument("platform")
@click.argument("username")
def account_remove(platform, username):
    """Remove an account."""
    if remove_account(platform, username):
        click.echo(f"✓ Removed [{platform.upper()}] @{username}")
    else:
        click.echo(f"Account not found: [{platform.upper()}] @{username}")


# ======================================================================
# trends
# ======================================================================

@cli.command()
@click.option("--niche", default="general", show_default=True, help="Content niche to analyze")
@click.option("--platform", type=click.Choice(["all", "youtube", "tiktok"], case_sensitive=False), default="all")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=20, show_default=True, type=int)
@click.pass_context
def trends(ctx, niche, platform, region, limit):
    """Scrape trending videos, hashtags, and music from YouTube and TikTok."""
    as_json = ctx.obj.get("as_json", False)
    region = region or ctx.obj.get("region", "US")
    analyzer = _make_analyzer(ctx.obj)

    click.echo(f"Fetching trends for '{niche}' in {region}...")

    if platform == "youtube":
        yt = YouTubeScraper(api_key=get_api_key("YOUTUBE_API_KEY"))
        data = {
            "trending_videos": yt.get_trending_videos(region=region, max_results=limit),
            "trending_hashtags": yt.get_trending_hashtags(region=region, limit=limit),
            "trending_music": yt.get_trending_music(region=region, limit=10),
        }
    elif platform == "tiktok":
        tt = TikTokScraper(ms_token=get_api_key("TIKTOK_MS_TOKEN"))
        data = {
            "trending_hashtags": tt.get_trending_hashtags(region=region, limit=limit),
            "trending_sounds": tt.get_trending_sounds(region=region, limit=10),
            "viral_patterns": tt.get_viral_content_patterns(region=region),
        }
    else:
        data = analyzer.get_unified_trends(niche=niche, region=region)

    if as_json:
        print_json(data)
    else:
        if platform in ("all", "youtube"):
            yt_data = data.get("youtube", data)
            print_section(f"YouTube Trending — {region}", {
                "top_videos": [v.get("title", "") for v in yt_data.get("trending_videos", [])[:5]],
                "top_hashtags": [h.get("hashtag", "") for h in yt_data.get("top_hashtags", yt_data.get("trending_hashtags", []))[:10]],
                "trending_music": [m.get("title", "") for m in yt_data.get("trending_music", [])[:5]],
            })
        if platform in ("all", "tiktok"):
            tt_data = data.get("tiktok", data)
            print_section(f"TikTok Trending — {region}", {
                "top_hashtags": [h.get("hashtag", "") for h in tt_data.get("top_hashtags", tt_data.get("trending_hashtags", []))[:10]],
                "trending_sounds": [s.get("title", "") for s in tt_data.get("trending_sounds", [])[:5]],
                "active_challenges": [c.get("challenge", "") for c in tt_data.get("active_challenges", [])[:5]],
                "hook_formulas": tt_data.get("hook_formulas", [])[:3],
            })
        if "cross_platform_trends" in data:
            print_section("Cross-Platform Opportunities", data["cross_platform_trends"])
        if "content_opportunities" in data:
            print_section("Content Opportunities", data["content_opportunities"])


# ======================================================================
# hashtags
# ======================================================================

@cli.command()
@click.argument("niche")
@click.option("--platform", type=click.Choice(["all", "youtube", "tiktok"], case_sensitive=False), default="all")
@click.option("--followers", default=0, type=int, help="Your follower count (affects hashtag strategy)")
@click.option("--region", default="US")
@click.pass_context
def hashtags(ctx, niche, platform, followers, region):
    """Get trending hashtag strategy for your niche and account size."""
    as_json = ctx.obj.get("as_json", False)
    analyzer = _make_analyzer(ctx.obj)

    click.echo(f"Building hashtag strategy for '{niche}'...")
    data = analyzer.get_hashtag_master_list(niche=niche, region=region, follower_count=followers)

    if as_json:
        print_json(data)
    else:
        print_section(f"Hashtag Strategy — {niche}", {
            "account_tier": data.get("follower_tier", ""),
            "TikTok_hashtags": data.get("tiktok_hashtags", {}).get("recommended", [])[:10],
            "YouTube_hashtags": data.get("youtube_hashtags", {}).get("recommended", [])[:5],
            "universal_always_use": data.get("universal_tags", []),
            "niche_specific": data.get("niche_specific", [])[:5],
            "caption_template": data.get("tiktok_hashtags", {}).get("caption_template") or "Not available",
        })
        click.echo(f"\n  TikTok note: {data.get('tiktok_hashtags', {}).get('note', '')}")
        click.echo(f"  YouTube note: {data.get('youtube_hashtags', {}).get('note', '')}")


# ======================================================================
# music
# ======================================================================

@cli.command()
@click.option("--region", default="US")
@click.option("--niche", default="", help="Filter by niche")
@click.pass_context
def music(ctx, region, niche):
    """Get trending music and sounds from YouTube and TikTok."""
    as_json = ctx.obj.get("as_json", False)
    analyzer = _make_analyzer(ctx.obj)

    click.echo(f"Fetching trending music for {region}...")
    data = analyzer.get_music_trends(region=region)

    if niche:
        tt = TikTokScraper(ms_token=get_api_key("TIKTOK_MS_TOKEN"))
        data["niche_sounds"] = tt.get_sound_for_niche(niche=niche)

    if as_json:
        print_json(data)
    else:
        yt_music = data.get("youtube_trending_music", [])
        tt_sounds = data.get("tiktok_trending_sounds", [])
        print_section(f"YouTube Trending Music — {region}", [
            f"{m.get('title', '')} — {m.get('artist', '')} ({m.get('views', 0):,} views)"
            for m in yt_music[:10]
        ])
        print_section(f"TikTok Trending Sounds — {region}", [
            f"{s.get('title', '')} — {s.get('artist', '')} ({s.get('video_count', 0):,} videos)"
            for s in tt_sounds[:10]
        ])
        if data.get("cross_platform_hits"):
            print_section("Cross-Platform Hits (use these!)", data["cross_platform_hits"])
        click.echo(f"\n  Tip: {data.get('tip', '')}")


# ======================================================================
# optimize
# ======================================================================

@cli.command()
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.argument("niche")
@click.option("--username", default="", help="Your account username")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--region", default="US")
@click.option("--issues", multiple=True, help="Known issues (e.g. --issues no_bio --issues inconsistent)")
@click.pass_context
def optimize(ctx, platform, niche, username, followers, region, issues):
    """Generate a full account optimization plan based on trending data."""
    as_json = ctx.obj.get("as_json", False)
    optimizer = _make_optimizer(ctx.obj)

    click.echo(f"Optimizing [{platform.upper()}] {('@' + username) if username else 'account'} for '{niche}'...")
    data = optimizer.optimize_account(
        platform=platform,
        niche=niche,
        username=username,
        follower_count=followers,
        region=region,
        current_issues=list(issues),
    )

    if as_json:
        print_json(data)
    else:
        print_section(f"Account Audit — {platform.upper()} | {niche}", data.get("audit", {}))
        print_section("Priority Fixes", data.get("priority_fixes", []))
        print_section("Profile Optimization", data.get("profile_optimization", []))
        print_section("Content Strategy", data.get("content_strategy", {}))
        print_section("Growth Roadmap", data.get("growth_roadmap", []))
        print_section("Trend Opportunities This Week", data.get("trend_opportunities", []))


@cli.command("optimize-all")
@click.option("--region", default="US")
@click.pass_context
def optimize_all(ctx, region):
    """Optimize all configured accounts at once."""
    as_json = ctx.obj.get("as_json", False)
    accounts = load_accounts()

    if not accounts:
        click.echo("No accounts configured. Run: trend-scout account add")
        return

    click.echo(f"Optimizing {len(accounts)} accounts...")
    optimizer = _make_optimizer(ctx.obj)
    data = optimizer.optimize_all_accounts(accounts=accounts, region=region)

    if as_json:
        print_json(data)
    else:
        for key, plan in data.get("accounts", {}).items():
            print_section(f"Optimization Plan — {key}", {
                "tier": plan.get("follower_tier", ""),
                "priority_fixes": plan.get("priority_fixes", [])[:3],
                "content_frequency": plan.get("content_strategy", {}).get("posting_frequency", ""),
            })
        print_section("Unified Cross-Platform Strategy", data.get("unified_strategy", {}))
        print_section("Content Repurposing Workflow", data.get("repurposing_workflow", []))


# ======================================================================
# bio
# ======================================================================

@cli.command()
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.argument("niche")
@click.pass_context
def bio(ctx, platform, niche):
    """Generate an optimized bio/about section for any platform."""
    as_json = ctx.obj.get("as_json", False)
    optimizer = _make_optimizer(ctx.obj)
    data = optimizer.get_bio_optimization(platform=platform, niche=niche)

    if as_json:
        print_json(data)
    else:
        print_section(f"Bio Template — {platform.upper()} | {niche}", {
            "structure": data.get("structure", ""),
            "character_limit": data.get("character_limit", ""),
            "keywords_tip": data.get("keywords_tip", ""),
        })
        click.echo("\n  Example bios:")
        for ex in data.get("examples", []):
            click.echo(f"    → {ex}")
        click.echo("\n  Call-to-action options:")
        for cta in data.get("cta_options", []):
            click.echo(f"    • {cta}")


# ======================================================================
# engagement
# ======================================================================

@cli.command()
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.argument("niche")
@click.option("--followers", default=0, type=int)
@click.pass_context
def engagement(ctx, platform, niche, followers):
    """Get an engagement boost plan with immediate and weekly tactics."""
    as_json = ctx.obj.get("as_json", False)
    optimizer = _make_optimizer(ctx.obj)
    data = optimizer.get_engagement_boost_plan(platform=platform, niche=niche, follower_count=followers)

    if as_json:
        print_json(data)
    else:
        print_section("Immediate Actions (do today)", data.get("immediate_actions", []))
        print_section("Weekly Habits", data.get("weekly_habits", []))
        print_section("Hook Formulas", data.get("content_hooks", []))
        click.echo(f"\n  Target engagement rate: {data.get('engagement_rate_target', '')}")


# ======================================================================
# theme-pages
# ======================================================================

@cli.group("theme-pages")
def theme_pages():
    """Theme page creation, strategy, and monetization guides."""


@theme_pages.command("guide")
@click.option("--niche", default="", help="Specific niche (optional)")
@click.pass_context
def theme_pages_guide(ctx, niche):
    """Complete guide to creating and monetizing a theme page."""
    as_json = ctx.obj.get("as_json", False)
    strategist = ThemePageStrategist()
    data = strategist.get_theme_page_guide(niche=niche)

    if as_json:
        print_json(data)
    else:
        what = data.get("what_is_a_theme_page", {})
        print_section("What Is a Theme Page?", {
            "definition": what.get("definition", ""),
            "why_it_works": what.get("why_it_works", []),
        })
        print_section("Setup Checklist", data.get("setup_checklist", []))
        print_section("Content Sourcing Methods", list(data.get("content_sourcing", {}).keys()))
        print_section("Growth Phases", [p.get("phase", "") + ": " + p.get("focus", "") for p in data.get("growth_phases", [])])
        print_section("Tools Stack", data.get("tools_stack", {}).get("free_tools", []))
        print_section("Common Mistakes", [m.get("mistake", "") + " → " + m.get("fix", "") for m in data.get("common_mistakes", [])])
        print_section("90-Day Action Plan", data.get("90_day_action_plan", {}))


@theme_pages.command("niches")
@click.pass_context
def theme_pages_niches(ctx):
    """List all profitable theme page niches ranked by earning potential."""
    as_json = ctx.obj.get("as_json", False)
    strategist = ThemePageStrategist()
    niches = strategist.get_all_profitable_niches()

    if as_json:
        print_json(niches)
    else:
        click.echo("\n  Profitable Theme Page Niches (ranked by RPM):\n")
        for i, n in enumerate(niches, 1):
            click.echo(
                f"  {i:2}. {n['niche']:<22} RPM: {n['avg_rpm']:<12} "
                f"Difficulty: {n['difficulty']:<12} "
                f"Best: {', '.join(n['best_platforms'][:2])}"
            )


@theme_pages.command("analyze")
@click.argument("niche")
@click.pass_context
def theme_pages_analyze(ctx, niche):
    """Deep analysis of a specific theme page niche."""
    as_json = ctx.obj.get("as_json", False)
    strategist = ThemePageStrategist()
    data = strategist.get_niche_analysis(niche=niche)

    if as_json:
        print_json(data)
    else:
        print_section(f"Niche Analysis — {niche}", {
            "description": data.get("description", ""),
            "difficulty": data.get("difficulty", ""),
            "avg_rpm": data.get("avg_rpm", ""),
            "best_platforms": data.get("best_platforms", []),
            "monetization": data.get("monetization", []),
        })
        print_section("Account Name Formulas", data.get("account_names_formula", []))
        print_section("Content Pillars", [f"{p['pillar']} ({p['percentage']}): {p['example']}" for p in data.get("content_pillars", [])])
        print_section("Monetization Path", data.get("monetization_path", []))
        print_section("Competitor Research Guide", data.get("competitor_research", {}))


@theme_pages.command("monetize")
@click.argument("niche")
@click.option("--followers", default=0, type=int)
@click.pass_context
def theme_pages_monetize(ctx, niche, followers):
    """Get a monetization playbook based on your follower count."""
    as_json = ctx.obj.get("as_json", False)
    strategist = ThemePageStrategist()
    data = strategist.get_conversion_playbook(niche=niche, followers=followers)

    if as_json:
        print_json(data)
    else:
        strategy = data.get("strategy", {})
        print_section(f"Monetization Playbook — {niche} ({followers:,} followers)", {
            "phase": data.get("phase", ""),
            "focus": strategy.get("focus", ""),
            "actions": strategy.get("actions", []),
            "expected_monthly": strategy.get("expected_monthly", "Build audience first"),
        })


@theme_pages.command("convert")
@click.option("--from-type", default="personal", help="Current account type")
@click.option("--to-type", default="theme_page", help="Target account type")
@click.pass_context
def theme_pages_convert(ctx, from_type, to_type):
    """Step-by-step checklist for converting an account into a theme page."""
    as_json = ctx.obj.get("as_json", False)
    strategist = ThemePageStrategist()
    data = strategist.get_account_conversion_checklist(from_type=from_type, to_type=to_type)

    if as_json:
        print_json(data)
    else:
        click.echo(f"\n  Converting: {from_type} → {to_type}\n")
        for step in data.get("conversion_steps", []):
            click.echo(f"  Step {step['step']}: {step['action']}")
            click.echo(f"          {step['detail']}\n")
        click.echo(f"  ⚠  Warning: {data.get('warning', '')}")
        click.echo(f"  Timeline: {data.get('timeline', '')}")


# ======================================================================
# schedule
# ======================================================================

@cli.group()
def schedule():
    """Generate content calendars and posting schedules."""


@schedule.command("weekly")
@click.option("--niche", required=True, help="Content niche")
@click.option("--platforms", default="tiktok,youtube,instagram", help="Comma-separated platforms")
@click.option("--posts-per-day", default=2, type=int, show_default=True)
@click.option("--region", default="US")
@click.option("--output", type=click.Choice(["pretty", "json", "csv", "notion"]), default="pretty")
@click.pass_context
def schedule_weekly(ctx, niche, platforms, posts_per_day, region, output):
    """Generate a 7-day content calendar with trending data integrated."""
    platform_list = [p.strip() for p in platforms.split(",")]
    analyzer = _make_analyzer(ctx.obj)
    scheduler = ContentScheduler()

    click.echo(f"Building weekly calendar for '{niche}' on {', '.join(platform_list)}...")

    trend_data = analyzer.get_niche_deep_dive(niche=niche, region=region)
    tt_hashtags = trend_data.get("tiktok", {}).get("niche_hashtags", [])
    tt_sounds = trend_data.get("tiktok", {}).get("best_sounds_for_niche", [])
    content_ideas = trend_data.get("content_ideas", [])

    calendar = scheduler.generate_weekly_calendar(
        platforms=platform_list,
        niche=niche,
        posts_per_day=posts_per_day,
        region=region,
        content_ideas=content_ideas,
        trending_hashtags=tt_hashtags,
        trending_sounds=tt_sounds,
    )

    if output == "json" or ctx.obj.get("as_json"):
        print_json(calendar)
    elif output == "csv":
        print(scheduler.export_to_csv(calendar))
    elif output == "notion":
        print(scheduler.export_to_notion_format(calendar))
    else:
        click.echo(f"\n  Week of {calendar['week_start']} — {niche} | {region}")
        click.echo(f"  Total posts planned: {calendar['total_posts_planned']}")
        click.echo(f"\n  {calendar['batch_recording_tip']}\n")
        for date_str, day in calendar.get("calendar", {}).items():
            click.echo(f"  {'─'*60}")
            click.echo(f"  {day['day'].upper()} {date_str}  ─  Tip: {day['tip']}")
            for post in day.get("posts", []):
                sound = f" | 🎵 {post['suggested_sound'][:30]}" if post.get("suggested_sound") else ""
                click.echo(
                    f"    [{post['post_time']}] [{post['platform'].upper()}] "
                    f"{post['content_type']}: {post['title_idea'][:45]}{sound}"
                )
                tags = " ".join(post.get("hashtags", [])[:4])
                click.echo(f"              Tags: {tags}")


@schedule.command("monthly")
@click.option("--niche", required=True)
@click.option("--platforms", default="tiktok,youtube,instagram")
@click.option("--posts-per-week", default=14, type=int)
@click.option("--region", default="US")
@click.pass_context
def schedule_monthly(ctx, niche, platforms, posts_per_week, region):
    """Generate a 30-day content plan."""
    as_json = ctx.obj.get("as_json", False)
    platform_list = [p.strip() for p in platforms.split(",")]
    scheduler = ContentScheduler()
    data = scheduler.generate_monthly_plan(
        platforms=platform_list, niche=niche, posts_per_week=posts_per_week, region=region
    )

    if as_json:
        print_json(data)
    else:
        click.echo(f"\n  30-Day Plan — {niche} | {data['month']}")
        click.echo(f"  Target: {data['total_posts_target']} total posts\n")
        for week in data.get("weekly_plans", []):
            click.echo(f"  Week {week['week']}: {week['theme']} — {week['content_focus']}")
            for goal in week.get("milestones", []):
                click.echo(f"    → {goal}")
        print_section("Month Goals", data.get("month_goals", []))
        print_section("Scheduling Tools", data.get("tools_for_scheduling", []))


@schedule.command("frequency")
@click.argument("platform", type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False))
@click.option("--niche", default="general")
@click.option("--followers", default=0, type=int)
@click.pass_context
def schedule_frequency(ctx, platform, niche, followers):
    """Get optimal posting frequency for your platform and growth stage."""
    as_json = ctx.obj.get("as_json", False)
    scheduler = ContentScheduler()
    data = scheduler.get_posting_frequency_recommendation(platform=platform, current_followers=followers, niche=niche)

    if as_json:
        print_json(data)
    else:
        print_section(f"Posting Frequency — {platform.upper()}", {
            "tier": data.get("tier", ""),
            "recommendation": data.get("recommendation", {}),
            "consistency_tip": data.get("consistency_tip", ""),
            "best_times": data.get("best_times", {}),
        })


# ======================================================================
# competitor
# ======================================================================

@cli.command()
@click.argument("url_or_username")
@click.option("--platform", type=click.Choice(["youtube", "tiktok"], case_sensitive=False), default="youtube")
@click.pass_context
def competitor(ctx, url_or_username, platform):
    """Analyze a competitor's YouTube channel or TikTok account."""
    as_json = ctx.obj.get("as_json", False)

    if platform == "youtube":
        yt = YouTubeScraper(api_key=get_api_key("YOUTUBE_API_KEY"))
        click.echo(f"Analyzing YouTube channel: {url_or_username}...")
        data = yt.analyze_competitor(channel_url=url_or_username)
    else:
        tt = TikTokScraper(ms_token=get_api_key("TIKTOK_MS_TOKEN"))
        click.echo(f"Analyzing TikTok creator: @{url_or_username}...")
        data = tt.analyze_creator(username=url_or_username)

    if as_json:
        print_json(data)
    else:
        print_section(f"Competitor Analysis — {url_or_username}", data)


# ======================================================================
# niche
# ======================================================================

@cli.command()
@click.argument("niche")
@click.option("--region", default="US")
@click.pass_context
def niche(ctx, niche, region):
    """Deep-dive analysis of a content niche across YouTube and TikTok."""
    as_json = ctx.obj.get("as_json", False)
    analyzer = _make_analyzer(ctx.obj)

    click.echo(f"Analyzing '{niche}' niche in {region}...")
    data = analyzer.get_niche_deep_dive(niche=niche, region=region)

    if as_json:
        print_json(data)
    else:
        print_section(f"Niche Deep Dive — {niche}", {
            "content_ideas": [i.get("title", "") for i in data.get("content_ideas", [])[:8]],
        })
        yt = data.get("youtube", {})
        tt = data.get("tiktok", {})
        print_section("YouTube", {
            "niche_videos": [v.get("title", "") for v in yt.get("niche_videos", [])[:5]],
            "trending_sounds": [m.get("title", "") for m in yt.get("trending_sounds", [])[:5]],
        })
        print_section("TikTok", {
            "hashtags": [h.get("hashtag", "") for h in tt.get("niche_hashtags", [])[:10]],
            "best_sounds": [s.get("title", "") for s in tt.get("best_sounds_for_niche", [])[:5]],
        })
        print_section("Posting Strategy", data.get("posting_strategy", {}))


# ======================================================================
# REPL
# ======================================================================

@cli.command()
@click.pass_context
def repl(ctx):
    """Start an interactive REPL session."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        session = PromptSession(history=InMemoryHistory())
        use_prompt_toolkit = True
    except ImportError:
        use_prompt_toolkit = False

    click.echo("Trend Scout REPL — type 'help' for commands, 'exit' to quit\n")
    accounts = load_accounts()
    if accounts:
        click.echo(f"  Loaded {len(accounts)} accounts: {', '.join('@' + a.get('username', '?') for a in accounts)}\n")

    while True:
        try:
            if use_prompt_toolkit:
                raw = session.prompt("trend-scout> ")
            else:
                raw = input("trend-scout> ")
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break

        raw = raw.strip()
        if not raw:
            continue
        if raw in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if raw == "help":
            click.echo(
                "  Commands:\n"
                "    trends [--niche NICHE] [--region US]\n"
                "    hashtags NICHE [--followers N]\n"
                "    music [--region US] [--niche NICHE]\n"
                "    optimize PLATFORM NICHE [--followers N]\n"
                "    optimize-all\n"
                "    bio PLATFORM NICHE\n"
                "    engagement PLATFORM NICHE [--followers N]\n"
                "    theme-pages guide [--niche NICHE]\n"
                "    theme-pages niches\n"
                "    theme-pages analyze NICHE\n"
                "    theme-pages monetize NICHE [--followers N]\n"
                "    theme-pages convert\n"
                "    schedule weekly --niche NICHE [--platforms tiktok,youtube,instagram]\n"
                "    schedule monthly --niche NICHE\n"
                "    schedule frequency PLATFORM [--followers N]\n"
                "    niche NICHE [--region US]\n"
                "    account list / add / remove\n"
                "    setup\n"
                "    exit"
            )
            continue

        # Delegate to Click CLI
        args = raw.split()
        try:
            cli.main(args=args, standalone_mode=False, obj=ctx.obj)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}")
