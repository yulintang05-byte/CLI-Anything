"""Social Trend Scout CLI — viral trend analysis, account optimization, theme pages."""

import json
import sys
from datetime import datetime

import click

from cli_anything.social_trend_scout.core.session import Session
from cli_anything.social_trend_scout.core.youtube_trends import YouTubeTrends, YOUTUBE_CATEGORIES
from cli_anything.social_trend_scout.core.tiktok_trends import TikTokTrends, NICHE_SEEDS
from cli_anything.social_trend_scout.core.trend_analyzer import TrendAnalyzer
from cli_anything.social_trend_scout.core.account_optimizer import AccountOptimizer, BEST_POSTING_TIMES
from cli_anything.social_trend_scout.core.theme_pages import ThemePageStrategy, NICHE_DATABASE
from cli_anything.social_trend_scout.core.content_calendar import ContentCalendar
from cli_anything.social_trend_scout.utils.output import (
    print_json, print_table, to_csv_string,
    format_video_table, format_hashtag_table,
)

SESSION = Session()
PLATFORMS = ["tiktok", "youtube", "instagram"]
NICHES = list(NICHE_DATABASE.keys())


# ======================================================================
# Root CLI
# ======================================================================

@click.group()
@click.version_option("1.0.0", prog_name="social-trend-scout")
def cli():
    """Social Trend Scout — scrape viral trends, optimize accounts, build theme pages."""


# ======================================================================
# Config group
# ======================================================================

@cli.group()
def config():
    """Manage API keys and account settings."""


@config.command("set-key")
@click.argument("platform", type=click.Choice(["youtube", "tiktok_ms_token", "tiktok_research"]))
@click.argument("key")
def config_set_key(platform, key):
    """Store an API key for a platform.

    \b
    Platforms:
      youtube          YouTube Data API v3 key (console.cloud.google.com)
      tiktok_ms_token  TikTok ms_token cookie (from browser devtools on tiktok.com)
      tiktok_research  TikTok Research API token (developers.tiktok.com)
    """
    SESSION.set_api_key(platform, key)
    click.echo(f"✅ API key for '{platform}' saved.")


@config.command("show")
@click.option("--json", "as_json", is_flag=True)
def config_show(as_json):
    """Show current configuration and cached data."""
    status = SESSION.status()
    if as_json:
        print_json(status)
    else:
        click.echo("\n=== Social Trend Scout Config ===")
        click.echo(f"API keys set: {list(status['api_keys'].keys()) or 'none'}")
        click.echo(f"Accounts registered: {status['accounts']}")
        click.echo(f"Cached platforms: {status['cached_platforms'] or 'none'}")


@config.command("add-account")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.argument("handle")
@click.argument("niche")
def config_add_account(platform, handle, niche):
    """Register a social media account to track and optimize."""
    SESSION.register_account(platform, handle, niche)
    click.echo(f"✅ Account @{handle} on {platform} registered (niche: {niche})")


@config.command("list-accounts")
@click.option("--platform", type=click.Choice(PLATFORMS), default=None)
@click.option("--json", "as_json", is_flag=True)
def config_list_accounts(platform, as_json):
    """List all registered accounts."""
    accounts = SESSION.list_accounts(platform)
    if as_json:
        print_json(accounts)
        return
    for plt, accts in accounts.items():
        click.echo(f"\n{plt.upper()}")
        for a in accts:
            click.echo(f"  @{a['handle']} — niche: {a['niche']} — added: {a['added'][:10]}")


@config.command("clear-cache")
@click.option("--platform", default=None, help="Clear cache for specific platform, or all if omitted")
def config_clear_cache(platform):
    """Clear cached trend data."""
    SESSION.clear_cache(platform)
    target = platform or "all platforms"
    click.echo(f"🗑 Cache cleared for {target}.")


# ======================================================================
# Trends group
# ======================================================================

@cli.group()
def trends():
    """Fetch viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="ISO 3166-1 alpha-2 country code")
@click.option("--category", default="0", show_default=True,
              type=click.Choice(list(YOUTUBE_CATEGORIES.keys())), help="YouTube category ID")
@click.option("--limit", default=50, show_default=True, type=click.IntRange(1, 200))
@click.option("--type", "trend_type", default="videos",
              type=click.Choice(["videos", "hashtags", "music", "all"]))
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
def trends_youtube(region, category, limit, trend_type, as_json, no_cache):
    """Fetch trending content from YouTube Data API v3.

    \b
    Examples:
      social-trend-scout trends youtube --region US --type all
      social-trend-scout trends youtube --category 10 --type music
      social-trend-scout trends youtube --type hashtags --json
    """
    api_key = SESSION.get_api_key("youtube")
    if not api_key:
        click.echo("❌ YouTube API key not set. Run: social-trend-scout config set-key youtube YOUR_KEY", err=True)
        click.echo("   Get your key at: https://console.cloud.google.com → YouTube Data API v3", err=True)
        sys.exit(1)

    cache_key = f"youtube_{region}_{category}"
    if not no_cache:
        cached = SESSION.get_cached_trends(cache_key)
        if cached:
            click.echo("ℹ Using cached data (run with --no-cache to refresh)", err=True)
            data = cached
        else:
            data = None
    else:
        data = None

    yt = YouTubeTrends(api_key)
    analyzer = TrendAnalyzer()

    if trend_type == "videos" or trend_type == "all":
        if data is None:
            click.echo(f"⏳ Fetching YouTube trending videos ({region}, category={YOUTUBE_CATEGORIES[category]})…", err=True)
            videos = yt.get_trending_videos(region=region, category_id=category, limit=limit)
            ranked = yt.rank_by_viral_score(videos)
            ranked = analyzer.classify_trend_velocity(ranked)
            SESSION.cache_trends(cache_key, {"videos": ranked})
        else:
            ranked = data.get("videos", [])

        if as_json:
            print_json(ranked[:20])
        else:
            click.echo(f"\n🔥 YouTube Trending Videos — {region} | {YOUTUBE_CATEGORIES[category]}\n")
            print_table(format_video_table(ranked[:20]))
            click.echo(f"\n📊 Viral patterns: {analyzer.extract_viral_patterns(ranked[:20])}")

    if trend_type == "hashtags" or trend_type == "all":
        click.echo("\n⏳ Analysing trending hashtags…", err=True)
        hashtags = yt.get_trending_hashtags(region=region, category_id=category, limit=limit)
        if as_json:
            print_json(hashtags[:30])
        else:
            click.echo(f"\n#️⃣  YouTube Trending Hashtags — {region}\n")
            rows = [["Rank", "Hashtag", "Frequency"]]
            for i, h in enumerate(hashtags[:30], 1):
                rows.append([i, h["hashtag"], h["frequency"]])
            print_table(rows)

    if trend_type == "music" or trend_type == "all":
        click.echo("\n⏳ Fetching trending music…", err=True)
        music = yt.get_trending_music(region=region, limit=30)
        if as_json:
            print_json(music)
        else:
            click.echo(f"\n🎵 YouTube Trending Music — {region}\n")
            rows = [["Rank", "Title", "Channel", "Views", "Engagement"]]
            from cli_anything.social_trend_scout.utils.output import format_number
            for i, m in enumerate(music[:20], 1):
                rows.append([i, m["title"][:40], m["channel"][:20],
                              format_number(m["views"]), f"{m['engagement_pct']:.1f}%"])
            print_table(rows)


@trends.command("tiktok")
@click.option("--type", "trend_type", default="hashtags",
              type=click.Choice(["hashtags", "sounds", "niche", "all"]))
@click.option("--niche", default=None, type=click.Choice(NICHES + ["custom"]),
              help="Niche for niche-specific trends")
@click.option("--limit", default=30, show_default=True, type=click.IntRange(1, 100))
@click.option("--json", "as_json", is_flag=True)
@click.option("--no-cache", is_flag=True)
def trends_tiktok(trend_type, niche, limit, as_json, no_cache):
    """Fetch trending content from TikTok.

    \b
    Note: TikTok uses Playwright (unofficial API). Install with:
      pip install TikTokApi playwright
      playwright install chromium

    Optional: set ms_token for better results:
      social-trend-scout config set-key tiktok_ms_token YOUR_TOKEN

    \b
    Examples:
      social-trend-scout trends tiktok --type hashtags
      social-trend-scout trends tiktok --type sounds --limit 20
      social-trend-scout trends tiktok --type niche --niche fitness
    """
    ms_token = SESSION.get_api_key("tiktok_ms_token")
    research_token = SESSION.get_api_key("tiktok_research")
    tt = TikTokTrends(ms_token=ms_token, research_api_token=research_token)

    cache_key = f"tiktok_{trend_type}_{niche or 'general'}"
    cached = None if no_cache else SESSION.get_cached_trends(cache_key)

    if trend_type == "hashtags" or trend_type == "all":
        if cached and "hashtags" in cached:
            hashtags = cached["hashtags"]
            click.echo("ℹ Using cached hashtag data", err=True)
        else:
            click.echo("⏳ Fetching TikTok trending hashtags…", err=True)
            hashtags = tt.get_trending_hashtags(limit=limit)
            SESSION.cache_trends(cache_key, {"hashtags": hashtags})

        if as_json:
            print_json(hashtags)
        else:
            click.echo("\n#️⃣  TikTok Trending Hashtags\n")
            rows = [["Rank", "Hashtag", "Frequency", "Total Views"]]
            from cli_anything.social_trend_scout.utils.output import format_number
            for i, h in enumerate(hashtags[:30], 1):
                rows.append([i, h.get("hashtag", ""), h.get("frequency", "—"),
                              format_number(h.get("total_views", 0)) if h.get("total_views") else "—"])
            print_table(rows)

    if trend_type == "sounds" or trend_type == "all":
        click.echo("\n⏳ Fetching TikTok trending sounds…", err=True)
        sounds = tt.get_trending_sounds(limit=limit)
        if as_json:
            print_json(sounds)
        else:
            click.echo("\n🎵 TikTok Trending Sounds\n")
            rows = [["Rank", "Title", "Author", "Duration", "Used In (videos)", "Original"]]
            for i, s in enumerate(sounds[:20], 1):
                if "error" in s:
                    click.echo(f"⚠ {s['error']}", err=True)
                    break
                rows.append([i, s.get("title", "")[:35], s.get("author", "")[:20],
                              f"{s.get('duration', 0)}s", s.get("frequency", "—"),
                              "✅" if s.get("original") else "—"])
            print_table(rows)

    if (trend_type == "niche" or trend_type == "all") and niche:
        click.echo(f"\n⏳ Fetching TikTok trends for niche: {niche}…", err=True)
        niche_videos = tt.get_niche_trends(niche, limit=limit)
        niche_tags = tt.get_niche_hashtags(niche)
        if as_json:
            print_json({"niche_videos": niche_videos, "niche_hashtags": niche_tags})
        else:
            click.echo(f"\n🎯 TikTok {niche.title()} Niche Trends\n")
            click.echo(f"Recommended hashtags: {' '.join(niche_tags)}\n")
            rows = [["Rank", "Description", "Author", "Plays", "Likes", "Shares", "Music"]]
            from cli_anything.social_trend_scout.utils.output import format_number
            for i, v in enumerate(niche_videos[:15], 1):
                if "error" in v:
                    click.echo(f"⚠ {v['error']}", err=True)
                    break
                rows.append([i, v.get("desc", "")[:35], v.get("author", "")[:15],
                              format_number(v.get("plays", 0)), format_number(v.get("likes", 0)),
                              format_number(v.get("shares", 0)), v.get("music", "")[:25]])
            print_table(rows)


@trends.command("cross-platform")
@click.option("--region", default="US", show_default=True)
@click.option("--niche", default=None, type=click.Choice(NICHES))
@click.option("--json", "as_json", is_flag=True)
def trends_cross_platform(region, niche, as_json):
    """Merge YouTube + TikTok trends into a unified cross-platform report.

    \b
    Example:
      social-trend-scout trends cross-platform --niche fitness
    """
    yt_key = SESSION.get_api_key("youtube")
    ms_token = SESSION.get_api_key("tiktok_ms_token")

    if not yt_key:
        click.echo("❌ YouTube API key required. Run: social-trend-scout config set-key youtube KEY", err=True)
        sys.exit(1)

    click.echo("⏳ Fetching YouTube trends…", err=True)
    yt = YouTubeTrends(yt_key)
    yt_hashtags = yt.get_trending_hashtags(region=region, limit=50)

    click.echo("⏳ Fetching TikTok trends…", err=True)
    tt = TikTokTrends(ms_token=ms_token)
    tt_hashtags = tt.get_trending_hashtags(limit=30)

    click.echo("⏳ Analysing cross-platform patterns…", err=True)
    analyzer = TrendAnalyzer()
    merged = analyzer.merge_hashtags(yt_hashtags, tt_hashtags)

    yt_videos = yt.get_trending_videos(region=region, limit=50)
    patterns = analyzer.extract_viral_patterns(yt_videos)
    action_plan = analyzer.generate_action_plan(merged, patterns, niche)

    result = {
        "region": region,
        "niche": niche,
        "merged_hashtags": merged[:20],
        "viral_patterns": patterns,
        "action_plan": action_plan,
    }

    if as_json:
        print_json(result)
    else:
        click.echo("\n🌐 Cross-Platform Trend Report\n")
        click.echo("=== TOP MERGED HASHTAGS (cross-platform first) ===\n")
        print_table(format_hashtag_table(merged[:15]))

        click.echo("\n=== VIRAL PATTERNS ===")
        click.echo(f"Avg viral video duration: {patterns.get('avg_viral_duration', 'N/A')}")
        click.echo(f"Hook patterns: {', '.join(patterns.get('hook_patterns', []))}")
        click.echo(f"Content angles: {', '.join(patterns.get('content_angles', []))}")
        click.echo(f"Top title words: {', '.join(w for w, _ in patterns.get('top_title_words', [])[:8])}")

        click.echo("\n=== ACTION PLAN ===")
        for action in action_plan.get("immediate_actions", []):
            click.echo(f"  • {action}")
        click.echo(f"\n📅 Post frequency: {action_plan['content_strategy']['post_frequency']}")


# ======================================================================
# Optimize group
# ======================================================================

@cli.group()
def optimize():
    """Optimize your social media accounts."""


@optimize.command("profile")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.option("--niche", default=None, help="Your content niche")
@click.option("--json", "as_json", is_flag=True)
def optimize_profile(platform, niche, as_json):
    """Get a profile optimization checklist for a platform.

    \b
    Example:
      social-trend-scout optimize profile tiktok --niche fitness
      social-trend-scout optimize profile youtube --niche finance
    """
    optimizer = AccountOptimizer()
    result = optimizer.get_profile_checklist(platform, niche)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n✅ Profile Optimization — {platform.title()} | {niche or 'general'}\n")
    for i, item in enumerate(result["checklist"], 1):
        click.echo(f"  {i}. {item}")
    if result.get("niche_specific_tips"):
        click.echo(f"\n🎯 Niche-specific tips for {niche}:")
        for tip in result["niche_specific_tips"]:
            click.echo(f"  • {tip}")
    click.echo(f"\n⚡ Priority: {result['priority']}")


@optimize.command("posting-times")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.option("--timezone", default="UTC", show_default=True, help="Your local timezone (e.g. US/Eastern, Europe/London)")
@click.option("--json", "as_json", is_flag=True)
def optimize_posting_times(platform, timezone, as_json):
    """Get optimal posting times for maximum reach.

    \b
    Example:
      social-trend-scout optimize posting-times tiktok --timezone US/Eastern
      social-trend-scout optimize posting-times youtube --timezone Europe/London
    """
    optimizer = AccountOptimizer()
    result = optimizer.get_best_posting_times(platform, timezone)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n⏰ Best Posting Times — {platform.title()} ({timezone})\n")
    rows = [["Day", "Best Times (local)"]]
    for day, times in result.get("schedule", {}).items():
        rows.append([day, "  |  ".join(times)])
    print_table(rows)
    click.echo(f"\n💡 {result.get('note', '')}")


@optimize.command("hashtags")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.argument("niche")
@click.option("--json", "as_json", is_flag=True)
def optimize_hashtags(platform, niche, as_json):
    """Generate an optimized hashtag set for a post.

    Pulls trending hashtags from cache and merges with niche-specific tags.

    \b
    Example:
      social-trend-scout optimize hashtags tiktok fitness
      social-trend-scout optimize hashtags instagram beauty
    """
    optimizer = AccountOptimizer()
    tt = TikTokTrends(ms_token=SESSION.get_api_key("tiktok_ms_token"))
    niche_hashtags = tt.get_niche_hashtags(niche)

    cached = SESSION.get_cached_trends(f"tiktok_hashtags_general")
    trending = cached.get("hashtags", []) if cached else []

    result = optimizer.optimize_hashtags(platform, niche, trending, niche_hashtags)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n#️⃣  Optimized Hashtags — {platform.title()} | {niche}\n")
    click.echo(" ".join(result["recommended_hashtags"]))
    click.echo(f"\n💡 {result['usage_tip']}")


@optimize.command("bio")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.argument("niche")
@click.argument("handle")
@click.option("--cta", default="link in bio", show_default=True)
@click.option("--json", "as_json", is_flag=True)
def optimize_bio(platform, niche, handle, cta, as_json):
    """Generate an optimized bio for a platform.

    \b
    Example:
      social-trend-scout optimize bio tiktok fitness myhandle --cta "DM for program"
    """
    optimizer = AccountOptimizer()
    result = optimizer.generate_bio(platform, niche, handle, cta)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n📝 Optimized Bio — {platform.title()} @{handle}\n")
    click.echo("─" * 40)
    click.echo(result["bio"])
    click.echo("─" * 40)
    click.echo(f"Characters: {result['char_count']}")
    click.echo(f"💡 {result['tip']}")


@optimize.command("engagement")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.option("--json", "as_json", is_flag=True)
def optimize_engagement(platform, as_json):
    """Get top engagement tactics for a platform.

    \b
    Example:
      social-trend-scout optimize engagement tiktok
      social-trend-scout optimize engagement youtube
    """
    optimizer = AccountOptimizer()
    result = optimizer.get_engagement_tactics(platform)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n⚡ Engagement Tactics — {platform.title()}\n")
    for i, tactic in enumerate(result["tactics"], 1):
        click.echo(f"  {i}. {tactic}")
    click.echo(f"\n🏆 Golden Rule: {result['golden_rule']}")


@optimize.command("audit")
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.argument("niche")
@click.argument("handle")
@click.option("--json", "as_json", is_flag=True)
def optimize_audit(platform, niche, handle, as_json):
    """Run a full account audit and get all optimization recommendations.

    \b
    Example:
      social-trend-scout optimize audit tiktok fitness @myaccount
      social-trend-scout optimize audit youtube finance MyChannel --json
    """
    optimizer = AccountOptimizer()
    result = optimizer.full_audit(platform, niche, handle.lstrip("@"))
    if as_json:
        print_json(result)
        return
    click.echo(f"\n🔍 Full Account Audit — @{handle} | {platform.title()} | {niche}\n")
    click.echo("=== PROFILE CHECKLIST ===")
    for i, item in enumerate(result["profile_checklist"]["checklist"], 1):
        click.echo(f"  {i}. {item}")
    click.echo("\n=== ENGAGEMENT TACTICS (Top 3) ===")
    for tactic in result["engagement_tactics"]["tactics"][:3]:
        click.echo(f"  • {tactic}")
    click.echo("\n=== BIO SUGGESTION ===")
    click.echo(result["bio_suggestion"]["bio"])
    click.echo("\n=== BEST POSTING TIME (UTC) ===")
    schedule = result["best_posting_times"].get("schedule", {})
    today = datetime.utcnow().strftime("%A")
    times = schedule.get(today, [])
    click.echo(f"  Today ({today}): {', '.join(times) or 'N/A'}")


# ======================================================================
# Theme-page group
# ======================================================================

@cli.group("theme-page")
def theme_page():
    """Theme page creation, conversion, and monetization guides."""


@theme_page.command("niches")
@click.option("--json", "as_json", is_flag=True)
def theme_page_niches(as_json):
    """List all supported niches with growth rate and competition level."""
    rows = [["Niche", "Growth Rate", "Competition", "Avg CPM", "Platforms"]]
    for niche, data in NICHE_DATABASE.items():
        rows.append([
            niche,
            data["growth_rate"],
            data["competition"],
            data["avg_cpm"],
            ", ".join(data["recommended_platforms"][:2]),
        ])
    if as_json:
        print_json(NICHE_DATABASE)
    else:
        click.echo("\n🎯 Available Niches\n")
        print_table(rows)


@theme_page.command("guide")
@click.argument("niche", type=click.Choice(NICHES))
@click.option("--json", "as_json", is_flag=True)
def theme_page_guide(niche, as_json):
    """Get the complete guide for a niche theme page.

    \b
    Example:
      social-trend-scout theme-page guide fitness
      social-trend-scout theme-page guide motivation --json
    """
    strategy = ThemePageStrategy()
    result = strategy.get_niche_guide(niche)
    if as_json:
        print_json(result)
        return

    data = result
    click.echo(f"\n📚 {niche.title()} Theme Page Guide\n")
    click.echo(f"Description: {data['description']}")
    click.echo(f"Audience: {data['audience']}")
    click.echo(f"Avg CPM: {data['avg_cpm']} | Growth: {data['growth_rate']} | Competition: {data['competition']}")
    click.echo(f"Best platforms: {', '.join(data['recommended_platforms'])}")
    click.echo(f"\nMonetization paths:")
    for m in data["monetization"]:
        click.echo(f"  • {m}")
    click.echo(f"\nLaunch Checklist:")
    for i, item in enumerate(data["launch_checklist"], 1):
        click.echo(f"  {i}. {item}")
    click.echo(f"\n30-Day Plan:")
    for phase in data["first_30_days"]:
        click.echo(f"  Days {phase['days']}: {phase['action']}")


@theme_page.command("content-sourcing")
@click.option("--budget", type=click.Choice(["zero", "low", "medium"]), default="zero", show_default=True)
@click.option("--json", "as_json", is_flag=True)
def theme_page_content_sourcing(budget, as_json):
    """Learn how to source content for your theme page.

    \b
    Example:
      social-trend-scout theme-page content-sourcing --budget zero
      social-trend-scout theme-page content-sourcing --budget low
    """
    strategy = ThemePageStrategy()
    result = strategy.get_content_sourcing_guide(budget)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n🎬 Content Sourcing Guide — Budget: {budget}\n")
    for name, method in result["methods"].items():
        click.echo(f"=== {name.replace('_', ' ').title()} ===")
        click.echo(f"  {method['description']}")
        click.echo(f"  Legality: {method['legality']}")
        click.echo(f"  Effort: {method['effort']} | Risk: {method['risk']}")
        click.echo(f"  Tools: {', '.join(method['tools'])}\n")
    click.echo("=== WORKFLOW ===")
    for step in result["recommended_workflow"]:
        click.echo(f"  {step}")


@theme_page.command("monetization")
@click.argument("niche", type=click.Choice(NICHES))
@click.argument("followers", type=int)
@click.option("--json", "as_json", is_flag=True)
def theme_page_monetization(niche, followers, as_json):
    """Get a monetization plan based on your niche and follower count.

    \b
    Example:
      social-trend-scout theme-page monetization fitness 50000
      social-trend-scout theme-page monetization finance 100000 --json
    """
    strategy = ThemePageStrategy()
    result = strategy.get_conversion_plan(niche, followers)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n💰 Monetization Plan — {niche.title()} | {followers:,} followers\n")
    click.echo(f"Stage: {result['stage'].upper()}")
    click.echo(f"Estimated monthly revenue: {result['estimated_monthly_revenue']}\n")
    click.echo("Recommended strategies:")
    for name, strategy_data in result["recommended_strategies"].items():
        click.echo(f"\n  [{name.replace('_', ' ').upper()}]")
        click.echo(f"    {strategy_data['what']}")
        click.echo(f"    CTA: {strategy_data['cta']}")
        click.echo(f"    Conversion: {strategy_data['conversion_rate']}")
        click.echo(f"    Revenue path: {strategy_data['monetization_path']}")
    click.echo(f"\n📈 Growth Roadmap:")
    for phase in result["growth_roadmap"]:
        click.echo(f"  {phase['phase']}: {phase['focus']}")


@theme_page.command("platforms")
@click.argument("niche", type=click.Choice(NICHES))
@click.option("--json", "as_json", is_flag=True)
def theme_page_platforms(niche, as_json):
    """Compare platforms for your niche.

    \b
    Example:
      social-trend-scout theme-page platforms fitness
    """
    strategy = ThemePageStrategy()
    result = strategy.platform_comparison(niche)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n📱 Platform Comparison — {niche.title()}\n")
    click.echo(f"Recommended order: {' → '.join(result['recommended_order'])}\n")
    for plt, details in result["platform_details"].items():
        click.echo(f"=== {plt.upper()} ===")
        for k, v in details.items():
            click.echo(f"  {k.replace('_', ' ').title()}: {v}")
        click.echo()
    click.echo(f"💡 {result['multi_platform_tip']}")


@theme_page.command("playbook")
@click.argument("niche", type=click.Choice(NICHES))
@click.option("--json", "as_json", is_flag=True)
@click.option("--output", default=None, help="Save to file (e.g. playbook.json)")
def theme_page_playbook(niche, as_json, output):
    """Generate the complete theme page playbook for a niche.

    Combines niche guide + content sourcing + monetization + platform comparison.

    \b
    Example:
      social-trend-scout theme-page playbook fitness
      social-trend-scout theme-page playbook motivation --output motivation_playbook.json
    """
    strategy = ThemePageStrategy()
    result = strategy.full_playbook(niche)

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"✅ Playbook saved to {output}")
        return

    if as_json:
        print_json(result)
        return

    click.echo(f"\n📖 {niche.title()} Theme Page Playbook\n")
    click.echo("This playbook covers: niche guide, content sourcing, monetization, and platform strategy.")
    click.echo("Run with --json to see full data, or --output file.json to save.\n")
    click.echo("Quick start:")
    for item in result["niche_guide"]["launch_checklist"][:5]:
        click.echo(f"  • {item}")
    click.echo(f"\nRecommended tools: {', '.join(result['tools']['content_creation'][:3])}")
    click.echo(f"Scheduling tools: {', '.join(result['tools']['scheduling'][:3])}")


# ======================================================================
# Calendar group
# ======================================================================

@cli.group()
def calendar():
    """Generate and export content calendars."""


@calendar.command("generate")
@click.argument("niche", type=click.Choice(NICHES))
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.option("--days", default=30, show_default=True, type=click.IntRange(7, 90))
@click.option("--posts-per-day", default=1, show_default=True, type=click.IntRange(1, 4))
@click.option("--json", "as_json", is_flag=True)
@click.option("--csv", "as_csv", is_flag=True, help="Output as CSV")
@click.option("--output", default=None, help="Save to file (e.g. calendar.json or calendar.csv)")
def calendar_generate(niche, platform, days, posts_per_day, as_json, as_csv, output):
    """Generate a content calendar with hooks, themes, and hashtags.

    \b
    Example:
      social-trend-scout calendar generate fitness tiktok --days 30
      social-trend-scout calendar generate motivation instagram --days 7 --posts-per-day 2 --csv
    """
    cal = ContentCalendar()
    cached_tt = SESSION.get_cached_trends(f"tiktok_hashtags_general")
    trending_tags = [h["hashtag"] for h in (cached_tt or {}).get("hashtags", [])[:10]]

    if not as_json and not as_csv and not output:
        click.echo(f"⏳ Generating {days}-day content calendar for {niche} on {platform}…", err=True)
    result = cal.generate(niche, platform, days, posts_per_day, trending_tags)

    if output:
        if output.endswith(".csv"):
            rows = cal.to_rows(result)
            with open(output, "w", newline="") as f:
                import csv as csv_mod
                csv_mod.writer(f).writerows(rows)
        else:
            with open(output, "w") as f:
                json.dump(result, f, indent=2, default=str)
        click.echo(f"✅ Calendar saved to {output}")
        return

    if as_json:
        print_json(result)
        return

    if as_csv:
        rows = cal.to_rows(result)
        click.echo(to_csv_string(rows))
        return

    click.echo(f"\n📅 {days}-Day Content Calendar — {niche.title()} | {platform.title()}\n")
    click.echo(f"Total posts: {result['total_posts']} | Pillar distribution:")
    for pillar, count in result["stats"]["content_pillar_distribution"].items():
        click.echo(f"  {pillar}: {count}")
    click.echo(f"\nFirst 7 days preview:")
    for day in result["calendar"][:7]:
        click.echo(f"\n  📆 {day['date']} ({day['day_of_week']}) — {day['week_theme'][:40]}")
        for post in day["posts"]:
            click.echo(f"     Post {post['post_number']}: {post['format']} | {post['content_pillar']}")
            click.echo(f"     Hook: {post['hook'][:60]}")


@calendar.command("sprint")
@click.argument("niche", type=click.Choice(NICHES))
@click.argument("platform", type=click.Choice(PLATFORMS))
@click.option("--json", "as_json", is_flag=True)
def calendar_sprint(niche, platform, as_json):
    """Generate a focused 7-day content sprint (2 posts/day).

    \b
    Example:
      social-trend-scout calendar sprint fitness tiktok
    """
    cal = ContentCalendar()
    result = cal.weekly_sprint(niche, platform)
    if as_json:
        print_json(result)
        return
    click.echo(f"\n🚀 7-Day Content Sprint — {niche.title()} | {platform.title()}\n")
    click.echo(f"💡 {result['tip']}\n")
    for day in result["week_sprint"]:
        click.echo(f"📆 {day['date']} ({day['day_of_week']})")
        for post in day["posts"]:
            click.echo(f"   [{post['post_number']}] {post['format']} — {post['content_pillar']}")
            click.echo(f"       Hook: \"{post['hook'][:55]}\"")
            click.echo(f"       CTA: {post['cta']}")


# ======================================================================
# Status command
# ======================================================================

@cli.command()
@click.option("--json", "as_json", is_flag=True)
def status(as_json):
    """Show current session status and API key configuration."""
    s = SESSION.status()
    if as_json:
        print_json(s)
        return
    click.echo("\n=== Social Trend Scout Status ===")
    click.echo(f"API keys: {list(s['api_keys'].keys()) or '(none set)'}")
    click.echo(f"Accounts: {dict(s['accounts']) or '(none registered)'}")
    click.echo(f"Cache: {s['cached_platforms'] or '(empty)'}")
    click.echo("\nQuick setup:")
    click.echo("  1. social-trend-scout config set-key youtube YOUR_YT_API_KEY")
    click.echo("  2. social-trend-scout trends youtube --region US --type all")
    click.echo("  3. social-trend-scout trends tiktok --type hashtags")
    click.echo("  4. social-trend-scout theme-page playbook fitness")


# ======================================================================
# REPL mode
# ======================================================================

@cli.command()
def repl():
    """Start an interactive REPL session."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    except ImportError:
        click.echo("prompt-toolkit not installed. Run: pip install prompt-toolkit", err=True)
        sys.exit(1)

    click.echo("\n🔥 Social Trend Scout REPL")
    click.echo("Type 'help' to see commands, 'exit' to quit.\n")

    session = PromptSession(history=InMemoryHistory(), auto_suggest=AutoSuggestFromHistory())
    while True:
        try:
            line = session.prompt("trend-scout> ").strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nExiting.")
            break

        if not line:
            continue
        if line in ("exit", "quit"):
            break
        if line == "help":
            click.echo("Commands: trends youtube | trends tiktok | trends cross-platform")
            click.echo("          optimize profile | optimize audit | optimize hashtags")
            click.echo("          theme-page guide | theme-page playbook | theme-page monetization")
            click.echo("          calendar generate | calendar sprint | config set-key | status")
            continue

        try:
            args = line.split()
            cli.main(args=args, prog_name="social-trend-scout", standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
