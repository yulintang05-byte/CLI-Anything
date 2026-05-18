"""SocialTrends CLI — Viral trend scraping, hashtag analysis, and account optimization.

Agent-native CLI for building viral social media presence. Supports TikTok,
YouTube, and Instagram with live trend data, hashtag scoring, music recommendations,
account auditing, and a complete theme page conversion guide.

Usage:
    python3 -m cli_anything.socialtrends [--json] <command>
    python3 -m cli_anything.socialtrends  (launches REPL)

Quick start:
    socialtrends auth setup --youtube-key YOUR_KEY
    socialtrends trends youtube --region US
    socialtrends hashtags suggest --niche fitness --platform tiktok
    socialtrends account optimize --platform tiktok --niche fitness --followers 5000
    socialtrends theme-page niches
    socialtrends theme-page guide --niche luxury
"""

import json
import sys
import shlex
import functools
import click
from typing import Optional, Any

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(f"\n  {message}")
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 4) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{_key(k)}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            click.echo(f"{pad}{_key(k)}: [{len(v)} items]")
            for item in v[:5]:
                if isinstance(item, dict):
                    sub = {sk: sv for sk, sv in item.items() if not isinstance(sv, (dict, list))}
                    click.echo(f"{pad}  › " + "  ".join(f"{k}={v}" for k, v in sub.items()))
                else:
                    click.echo(f"{pad}  › {item}")
            if len(v) > 5:
                click.echo(f"{pad}  … {len(v) - 5} more")
        else:
            click.echo(f"{pad}{_key(k)}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("    (empty)")
        return
    for item in lst[:20]:
        if isinstance(item, dict):
            parts = [f"{k}={v}" for k, v in item.items() if not isinstance(v, (dict, list))]
            click.echo("    › " + "  ".join(parts))
        else:
            click.echo(f"    › {item}")
    if len(lst) > 20:
        click.echo(f"    … {len(lst) - 20} more")


def _key(k: str) -> str:
    return f"\033[36m{k}\033[0m"


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"\n  \033[31m✗\033[0m {msg}", err=True)


def handle_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RuntimeError, ValueError, KeyError) as e:
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
@click.version_option("1.0.0", prog_name="socialtrends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """SocialTrends — viral trend scraping, hashtag analysis & account optimization.

    \b
    Quick start:
      socialtrends auth setup --youtube-key YOUR_KEY
      socialtrends trends youtube --region US
      socialtrends hashtags suggest --niche fitness --platform tiktok
      socialtrends account optimize --platform tiktok --niche fitness --followers 5000
      socialtrends theme-page niches
      socialtrends theme-page guide --niche luxury
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── auth group ────────────────────────────────────────────────────────────────

@cli.group()
def auth():
    """Configure API keys and platform tokens."""
    pass


@auth.command("setup")
@click.option("--youtube-key", default=None, help="YouTube Data API v3 key")
@click.option("--tiktok-token", default=None, help="TikTok Research API access token")
@handle_error
def auth_setup(youtube_key: Optional[str], tiktok_token: Optional[str]) -> None:
    """Configure API credentials for trend fetching.

    \b
    Get a YouTube API key (free):
      1. Go to console.cloud.google.com
      2. Create project → Enable 'YouTube Data API v3'
      3. Create credentials → API Key

    \b
    Get TikTok Research API token (requires approval):
      Apply at: https://developers.tiktok.com/products/research-api/
    """
    from cli_anything.socialtrends.utils import config as cfg

    saved: dict[str, str] = {}
    if youtube_key:
        cfg.save_config({"youtube_api_key": youtube_key})
        saved["youtube_api_key"] = "✓ saved"
    if tiktok_token:
        cfg.save_config({"tiktok_research_token": tiktok_token})
        saved["tiktok_research_token"] = "✓ saved"

    if not saved:
        click.echo("  No keys provided. Use --youtube-key or --tiktok-token.")
        return

    output(saved, "API credentials saved:")


@auth.command("status")
@handle_error
def auth_status() -> None:
    """Show which API keys are configured."""
    from cli_anything.socialtrends.utils import config as cfg

    conf = cfg.load_config()
    result = {
        "youtube_api_key": "✓ configured" if conf.get("youtube_api_key") else "✗ missing",
        "tiktok_research_token": "✓ configured" if conf.get("tiktok_research_token") else "✗ missing",
        "note": "YouTube key needed for live trends. TikTok uses Google Trends bridge without a key.",
    }
    output(result, "API key status:")


@auth.command("clear")
@click.confirmation_option(prompt="Clear all saved API credentials?")
@handle_error
def auth_clear() -> None:
    """Remove all saved credentials."""
    from cli_anything.socialtrends.utils import config as cfg
    import os
    if cfg.CONFIG_FILE.exists():
        os.unlink(cfg.CONFIG_FILE)
    output({"status": "cleared"}, "All credentials removed.")


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Fetch live trending content from YouTube and TikTok."""
    pass


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="Country code (US, GB, IN, AU, etc.)")
@click.option("--category", default="0", show_default=True,
              help="Category ID (0=all, 10=music, 20=gaming, 24=entertainment, 26=howto)")
@click.option("--max", "max_results", default=25, show_default=True, type=int, help="Videos to fetch (max 50)")
@click.option("--no-cache", is_flag=True, help="Bypass cache and fetch fresh data")
@handle_error
def trends_youtube(region: str, category: str, max_results: int, no_cache: bool) -> None:
    """Fetch YouTube trending videos and extract viral hashtags.

    Requires YouTube API key: socialtrends auth setup --youtube-key KEY

    \b
    Examples:
      socialtrends trends youtube
      socialtrends trends youtube --region GB --category 10  (UK music)
      socialtrends trends youtube --region US --category 20  (US gaming)
    """
    from cli_anything.socialtrends.core import youtube_trends as yt
    click.echo(f"\n  Fetching YouTube trending ({region}, category {category})...")
    data = yt.get_trending_topics(region=region)

    if _json_output:
        output(data)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    skin.section(f"YouTube Trending — {region} ({data['video_count']} videos)")

    skin.section("Top Trending Hashtags")
    skin.table(
        ["#", "Hashtag", "Appearances", "% of Trending"],
        [[str(i+1), h["hashtag"], str(h["count"]), f"{h['percent']}%"]
         for i, h in enumerate(data["top_hashtags"][:15])]
    )

    skin.section("Top 10 Trending Videos")
    skin.table(
        ["#", "Title", "Channel", "Views", "Likes"],
        [[str(i+1), v["title"][:40], v["channel"][:20],
          f"{v['views']:,}", f"{v['likes']:,}"]
         for i, v in enumerate(data["top_videos"][:10])]
    )

    skin.section("Category Breakdown")
    for cat, count in data["categories_breakdown"].items():
        skin.bullet([f"{cat}: {count} videos"])


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Country code")
@click.option("--niche", default="", help="Niche filter (fitness, food, etc.)")
@click.option("--no-cache", is_flag=True, help="Bypass cache")
@handle_error
def trends_tiktok(region: str, niche: str, no_cache: bool) -> None:
    """Fetch TikTok trending hashtags and content.

    Uses TikTok Research API (if configured) or Google Trends bridge.
    Curated trends always available as fallback.

    \b
    Examples:
      socialtrends trends tiktok
      socialtrends trends tiktok --niche fitness
      socialtrends trends tiktok --region GB
    """
    from cli_anything.socialtrends.core import tiktok_trends as tt

    click.echo(f"\n  Fetching TikTok trends ({region})...")

    result: dict = {}

    # Try Research API first
    token = __import__(
        "cli_anything.socialtrends.utils.config", fromlist=["get"]
    ).get("tiktok_research_token")

    if token:
        try:
            videos = tt.fetch_trending_videos_research(region=region, max_results=50)
            result["source"] = "TikTok Research API"
            result["videos"] = videos[:10]
            result["top_hashtags"] = tt.extract_trending_hashtags(videos, top_n=30)
        except Exception as e:
            result["research_api_error"] = str(e)

    # Google Trends bridge (always run)
    try:
        google = tt.fetch_trending_via_google_trends(niche=niche, region=region, use_cache=not no_cache)
        result["google_trends"] = google
    except Exception as e:
        result["google_trends_error"] = str(e)

    # Always include curated
    result["curated_trending"] = tt.get_curated_trending(region=region)

    if _json_output:
        output(result)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    skin.section(f"TikTok Trends — {region}")

    if "top_hashtags" in result and result["top_hashtags"]:
        skin.section("Research API — Trending Hashtags")
        skin.table(
            ["Hashtag", "Count", "Avg Engagement"],
            [[h["hashtag"], str(h["count"]), f"{h['avg_engagement']:,}"]
             for h in result["top_hashtags"][:15]]
        )

    curated = result.get("curated_trending", {})
    if curated:
        skin.section("Curated Trending (Always Available)")
        for category, tags in curated.items():
            if isinstance(tags, list):
                skin.info(f"{category.replace('_', ' ').title()}: {' '.join(tags[:6])}")

    if "google_trends" in result and result["google_trends"].get("trending_searches"):
        skin.section("Google Trends → TikTok Topics")
        searches = result["google_trends"]["trending_searches"][:10]
        skin.bullet(searches)


@trends.command("all")
@click.option("--region", default="US", show_default=True, help="Country code")
@click.option("--niche", default="", help="Niche filter")
@handle_error
def trends_all(region: str, niche: str) -> None:
    """Fetch trends from all available platforms simultaneously."""
    from cli_anything.socialtrends.core import youtube_trends as yt
    from cli_anything.socialtrends.core import tiktok_trends as tt

    click.echo(f"\n  Fetching trends from all platforms ({region})...")

    result: dict = {"region": region}

    try:
        yt_data = yt.get_trending_topics(region=region)
        result["youtube"] = {
            "top_hashtags": yt_data["top_hashtags"][:10],
            "top_videos": [{"title": v["title"], "views": v["views"]} for v in yt_data["top_videos"][:5]],
        }
    except Exception as e:
        result["youtube"] = {"error": str(e)}

    try:
        result["tiktok_curated"] = tt.get_curated_trending(region=region)
    except Exception as e:
        result["tiktok"] = {"error": str(e)}

    output(result, f"All platform trends — {region}:")


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag analysis, scoring, and niche-specific suggestions."""
    pass


@hashtags.command("suggest")
@click.option("--niche", required=True, help="Content niche (fitness, food, fashion, money, etc.)")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube", "all"]))
@click.option("--count", default=30, show_default=True, type=int, help="Number of hashtags")
@click.option("--no-boost", is_flag=True, help="Skip platform boost tags (fyp, reels, etc.)")
@handle_error
def hashtags_suggest(niche: str, platform: str, count: int, no_boost: bool) -> None:
    """Generate an optimized hashtag set for your niche.

    \b
    Examples:
      socialtrends hashtags suggest --niche fitness
      socialtrends hashtags suggest --niche food --platform instagram --count 25
      socialtrends hashtags suggest --niche money --platform youtube
    """
    from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags

    result = suggest_hashtags(niche=niche, platform=platform, count=count, include_boost=not no_boost)

    if _json_output:
        output(result)
        return

    if "error" in result:
        _err(result["error"])
        click.echo(f"  Available niches: {', '.join(result.get('available_niches', []))}")
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.section(f"Hashtags for #{niche} on {platform}")

    for tier, tags in result["tiers"].items():
        if tags:
            skin.info(f"{tier.replace('_', ' ').title()} ({len(tags)}): {' '.join(tags)}")

    skin.section("Caption-Ready String")
    click.echo(f"\n  {result['caption_ready']}\n")
    skin.info(result["strategy_note"])


@hashtags.command("score")
@click.argument("hashtag")
@handle_error
def hashtags_score(hashtag: str) -> None:
    """Score a hashtag's virality potential and get recommendations.

    \b
    Example:
      socialtrends hashtags score '#fitness'
      socialtrends hashtags score 'gymlife'
    """
    from cli_anything.socialtrends.core.hashtag_analyzer import score_hashtag

    result = score_hashtag(hashtag)
    output(result, f"Score for {result['hashtag']}:")


@hashtags.command("analyze")
@click.argument("tags", nargs=-1, required=True)
@handle_error
def hashtags_analyze(tags: tuple) -> None:
    """Analyze a set of hashtags for balance and missing tiers.

    \b
    Example:
      socialtrends hashtags analyze '#fitness' '#gym' '#fyp' '#homeworkout'
    """
    from cli_anything.socialtrends.core.hashtag_analyzer import analyze_hashtag_set

    result = analyze_hashtag_set(list(tags))
    output(result, "Hashtag set analysis:")


@hashtags.command("niches")
@handle_error
def hashtags_niches() -> None:
    """List all available niche categories for hashtag suggestions."""
    from cli_anything.socialtrends.core.hashtag_analyzer import list_niches

    niches = list_niches()
    click.echo(f"\n  Available niches ({len(niches)}):")
    click.echo("  " + "  ".join(f"\033[36m{n}\033[0m" for n in niches))
    click.echo()


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Trending music and sound recommendations."""
    pass


@music.command("trending")
@click.option("--region", default="US", show_default=True)
@click.option("--source", default="all", type=click.Choice(["youtube", "spotify", "all"]))
@handle_error
def music_trending(region: str, source: str) -> None:
    """Fetch trending music from YouTube and Spotify.

    \b
    Example:
      socialtrends music trending
      socialtrends music trending --region GB --source spotify
    """
    from cli_anything.socialtrends.core import music_trends as mt

    result: dict = {"region": region}

    if source in ("youtube", "all"):
        try:
            yt_music = mt.fetch_youtube_music_trending(region=region)
            result["youtube_music"] = [
                {"rank": i+1, "title": v["title"], "channel": v["channel"], "views": v["views"]}
                for i, v in enumerate(yt_music[:10])
            ]
        except Exception as e:
            result["youtube_music_error"] = str(e)

    if source in ("spotify", "all"):
        result["spotify_charts"] = mt.get_spotify_charts(region=region)

    result["evergreen_tiktok_sounds"] = mt.get_evergreen_sounds()
    output(result, f"Trending music — {region}:")


@music.command("recommend")
@click.option("--niche", required=True, help="Content niche")
@handle_error
def music_recommend(niche: str) -> None:
    """Get music style recommendations for your content niche.

    \b
    Example:
      socialtrends music recommend --niche fitness
      socialtrends music recommend --niche travel
    """
    from cli_anything.socialtrends.core import music_trends as mt

    result = mt.get_music_recommendations(niche=niche)

    if _json_output:
        output(result)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.section(f"Music Recommendations — {niche}")
    skin.info(f"Moods: {', '.join(result['recommended_moods'])}")
    skin.info(f"Avoid: {', '.join(result.get('avoid', []))}")
    skin.info(f"Pro tip: {result['pro_tip']}")

    skin.section("YouTube Search Terms")
    skin.bullet(result["youtube_search_terms"])

    skin.section("Evergreen TikTok Sounds")
    for s in result["evergreen_tiktok_sounds"]:
        skin.bullet([f"{s['name']} by {s['artist']} ({s['niche']}, {s['uses']} uses)"])

    skin.section("Where to Find Trending Sounds")
    skin.bullet(result["where_to_find_trending_sounds"])


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization, posting schedules, captions, and audits."""
    pass


@account.command("optimize")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--niche", required=True, help="Content niche")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--avg-likes", default=0, type=int, help="Average likes per post")
@click.option("--avg-comments", default=0, type=int, help="Average comments per post")
@click.option("--posts-per-week", default=5, type=int, help="Current posts per week")
@handle_error
def account_optimize(
    platform: str, niche: str, followers: int, avg_likes: int,
    avg_comments: int, posts_per_week: int,
) -> None:
    """Run a full account audit and get priority action plan.

    \b
    Examples:
      socialtrends account optimize --platform tiktok --niche fitness --followers 5000
      socialtrends account optimize --platform instagram --niche food --followers 25000 --avg-likes 800 --avg-comments 40
    """
    from cli_anything.socialtrends.core.account_optimizer import full_account_audit

    result = full_account_audit(
        platform=platform, niche=niche, followers=followers,
        avg_likes=avg_likes, avg_comments=avg_comments,
        posts_per_week=posts_per_week,
    )

    if _json_output:
        output(result)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    score = result["overall_score"]
    score_color = "\033[32m" if score >= 70 else "\033[33m" if score >= 40 else "\033[31m"

    skin.section(f"Account Audit — {platform.title()} / #{niche}")
    click.echo(f"\n  Overall Score: {score_color}{score}/100\033[0m  |  "
               f"ER: {result['engagement_rate']}% ({result['engagement_rating']})\n")

    if result["wins"]:
        skin.section("What's Working ✓")
        skin.bullet(result["wins"], "✓")

    if result["issues"]:
        skin.section("Issues Found ✗")
        skin.bullet(result["issues"], "✗")

    if result["priority_actions"]:
        skin.section("Priority Actions (Do This Week)")
        for i, action in enumerate(result["priority_actions"], 1):
            click.echo(f"    {i}. {action}")

    skin.section("Algorithm Signals (Ranked by Impact)")
    skin.bullet(result["algorithm_signals"])

    skin.section("Growth Hacks")
    skin.bullet(result["recommendations"][:5])


@account.command("bio")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--niche", required=True)
@click.option("--name", required=True, help="Your name or brand name")
@click.option("--cta", default="", help="Call-to-action text")
@click.option("--keywords", default="", help="Comma-separated keywords")
@handle_error
def account_bio(platform: str, niche: str, name: str, cta: str, keywords: str) -> None:
    """Generate an optimized bio template.

    \b
    Example:
      socialtrends account bio --platform instagram --niche fitness --name "Alex Fit" --cta "Get my free 7-day plan"
    """
    from cli_anything.socialtrends.core.account_optimizer import generate_bio

    kws = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
    result = generate_bio(platform=platform, niche=niche, name=name, cta=cta, keywords=kws)

    if _json_output:
        output(result)
        return

    click.echo(f"\n  \033[1mBio Template ({result['char_count']}/{result['limit']} chars):\033[0m\n")
    click.echo("  " + result["bio_template"].replace("\n", "\n  "))
    click.echo()
    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    ReplSkin().bullet(result["tips"])


@account.command("schedule")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--timezone", default="ET", show_default=True, help="Your timezone (ET, PT, GMT, IST, etc.)")
@click.option("--posts-per-week", default=7, type=int, show_default=True)
@handle_error
def account_schedule(platform: str, timezone: str, posts_per_week: int) -> None:
    """Generate an optimal posting schedule.

    \b
    Example:
      socialtrends account schedule --platform tiktok --timezone PT
      socialtrends account schedule --platform instagram --posts-per-week 5
    """
    from cli_anything.socialtrends.core.account_optimizer import get_posting_schedule

    result = get_posting_schedule(platform=platform, timezone=timezone, posts_per_week=posts_per_week)

    if _json_output:
        output(result)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.section(f"Posting Schedule — {platform.title()} ({timezone})")
    skin.table(
        ["Day", "Post At (ET)", "# Posts"],
        [[s["day"], ", ".join(s["post_at"]), str(s["post_count"])] for s in result["schedule"]]
    )
    skin.info(result["timezone_note"])
    skin.info(result["pro_tip"])


@account.command("caption")
@click.option("--topic", required=True, help="What the content is about")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--with-hashtags/--no-hashtags", default=True)
@handle_error
def account_caption(topic: str, niche: str, platform: str, with_hashtags: bool) -> None:
    """Generate an engagement-optimized caption using proven formulas.

    \b
    Examples:
      socialtrends account caption --topic "how to lose belly fat" --niche fitness
      socialtrends account caption --topic "best credit card for beginners" --niche money --platform youtube
    """
    from cli_anything.socialtrends.core.account_optimizer import generate_caption
    from cli_anything.socialtrends.core.hashtag_analyzer import suggest_hashtags

    hashtag_list: list[str] = []
    if with_hashtags:
        h_result = suggest_hashtags(niche=niche, platform=platform, count=25)
        hashtag_list = h_result.get("hashtags", [])

    result = generate_caption(
        topic=topic, niche=niche, platform=platform,
        include_hashtags=with_hashtags, hashtags=hashtag_list,
    )

    if _json_output:
        output(result)
        return

    click.echo(f"\n  \033[1mCaption ({result['formula_used']}):\033[0m\n")
    click.echo("  " + result["caption"].replace("\n", "\n  "))
    click.echo()
    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    ReplSkin().bullet(result["tips"])


@account.command("engagement")
@click.option("--followers", required=True, type=int)
@click.option("--likes", required=True, type=int)
@click.option("--comments", default=0, type=int)
@click.option("--shares", default=0, type=int)
@click.option("--saves", default=0, type=int)
@handle_error
def account_engagement(followers: int, likes: int, comments: int, shares: int, saves: int) -> None:
    """Calculate your engagement rate and benchmark it.

    \b
    Example:
      socialtrends account engagement --followers 25000 --likes 1200 --comments 80 --saves 150
    """
    from cli_anything.socialtrends.core.account_optimizer import calculate_engagement_rate

    result = calculate_engagement_rate(followers, likes, comments, shares, saves)
    output(result, f"Engagement Rate: {result['engagement_rate_percent']}% — {result['rating']}")


# ── theme-page group ──────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Complete theme page guide: niches, conversion funnels, monetization."""
    pass


@theme_page.command("niches")
@click.option("--sort", default="monetization", type=click.Choice(["monetization", "difficulty", "growth_speed"]))
@handle_error
def tp_niches(sort: str) -> None:
    """List all profitable theme page niches ranked by revenue potential.

    \b
    Example:
      socialtrends theme-page niches
      socialtrends theme-page niches --sort difficulty
    """
    from cli_anything.socialtrends.core.theme_pages import list_niches

    niches = list_niches(sort_by=sort)

    if _json_output:
        output(niches)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.section(f"Profitable Theme Page Niches (sorted by {sort})")
    skin.table(
        ["Niche", "Difficulty", "Monetization", "Brand Deals", "Best Platforms"],
        [
            [
                n["name"],
                n["difficulty"],
                n["monetization_potential"],
                n["typical_brand_deal_range"],
                ", ".join(n["best_platforms"][:2]),
            ]
            for n in niches
        ]
    )


@theme_page.command("guide")
@click.option("--niche", required=True, help="Niche slug (luxury, fitness, finance, etc.)")
@handle_error
def tp_guide(niche: str) -> None:
    """Get a complete guide for a specific theme page niche.

    \b
    Example:
      socialtrends theme-page guide --niche luxury
      socialtrends theme-page guide --niche fitness
      socialtrends theme-page guide --niche finance
    """
    from cli_anything.socialtrends.core.theme_pages import get_niche

    result = get_niche(niche)
    if "error" in result:
        _err(result["error"])
        return

    if _json_output:
        output(result)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.section(f"Theme Page Guide — {result['name']}")

    click.echo(f"    Difficulty: {result['difficulty']}  |  Competition: {result['competition']}")
    click.echo(f"    Monetization: {result['monetization_potential']}  |  Avg RPM: {result['avg_rpm_per_1k_views']}")
    click.echo(f"    Brand Deals: {result['typical_brand_deal_range']}")
    click.echo()

    skin.section("Best Platforms")
    skin.bullet(result["best_platforms"])

    skin.section("Content Types to Post")
    skin.bullet(result["content_types"])

    skin.section("Top Monetization Methods")
    skin.bullet(result["top_monetization"])

    skin.section("Fastest Path to Revenue")
    click.echo(f"    {result['fastest_path_to_revenue']}\n")

    skin.section("Target Audience")
    click.echo(f"    {result['target_audience']}\n")


@theme_page.command("convert")
@click.option("--strategy", default=None,
              type=click.Choice(["link_in_bio_funnel", "story_funnel", "email_list_building",
                                  "shoutout_model", "digital_products", "affiliate_marketing"]),
              help="Specific conversion strategy")
@handle_error
def tp_convert(strategy: Optional[str]) -> None:
    """Learn conversion strategies to turn followers into revenue.

    \b
    Examples:
      socialtrends theme-page convert                          (list all)
      socialtrends theme-page convert --strategy email_list_building
      socialtrends theme-page convert --strategy digital_products
    """
    from cli_anything.socialtrends.core.theme_pages import (
        list_conversion_strategies, get_conversion_strategy
    )

    if not strategy:
        strategies = list_conversion_strategies()
        if _json_output:
            output(strategies)
            return
        from cli_anything.socialtrends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Conversion Strategies")
        skin.table(
            ["Strategy", "Difficulty", "Revenue Potential"],
            [[s["name"], s["difficulty"], s["revenue_potential"]] for s in strategies]
        )
        click.echo("  Run with --strategy <slug> for full blueprint.\n")
        return

    result = get_conversion_strategy(strategy)
    if _json_output:
        output(result)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    skin.section(result["name"])
    skin.info(f"Difficulty: {result['difficulty']}")
    skin.info(f"Revenue potential: {result['revenue_potential']}")

    skin.section("Tools Needed")
    skin.bullet(result["tools"])

    skin.section("Step-by-Step Blueprint")
    for step in result["steps"]:
        click.echo(f"    {step}")

    click.echo(f"\n    Conversion rate: {result['conversion_rate_benchmark']}\n")


@theme_page.command("sourcing")
@click.option("--method", default=None,
              type=click.Choice(["repost_with_credit", "royalty_free_content",
                                  "user_generated_content", "original_content"]))
@handle_error
def tp_sourcing(method: Optional[str]) -> None:
    """Content sourcing guide — how to legally get content for your theme page.

    \b
    Examples:
      socialtrends theme-page sourcing                          (all methods)
      socialtrends theme-page sourcing --method royalty_free_content
      socialtrends theme-page sourcing --method original_content
    """
    from cli_anything.socialtrends.core.theme_pages import get_content_sourcing_guide

    result = get_content_sourcing_guide(method=method)
    output(result, "Content sourcing guide:")


@theme_page.command("playbook")
@click.option("--stage", default="0_to_10k",
              type=click.Choice(["0_to_10k", "10k_to_100k", "100k_plus"]),
              show_default=True)
@handle_error
def tp_playbook(stage: str) -> None:
    """Step-by-step growth playbook by follower milestone.

    \b
    Examples:
      socialtrends theme-page playbook                          (0 to 10k)
      socialtrends theme-page playbook --stage 10k_to_100k
      socialtrends theme-page playbook --stage 100k_plus
    """
    from cli_anything.socialtrends.core.theme_pages import get_growth_playbook

    playbook = get_growth_playbook(stage=stage)

    if _json_output:
        output(playbook)
        return

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin()
    label = stage.replace("_", " → ")
    skin.section(f"Growth Playbook — {label}")

    for phase in playbook:
        week = phase.get("week") or phase.get("phase", "")
        skin.section(week)
        skin.bullet(phase.get("actions", []))


@theme_page.command("revenue")
@click.option("--niche", required=True, help="Niche slug (luxury, fitness, finance, etc.)")
@click.option("--followers", required=True, type=int, help="Current follower count")
@handle_error
def tp_revenue(niche: str, followers: int) -> None:
    """Estimate realistic revenue potential at your current follower level.

    \b
    Example:
      socialtrends theme-page revenue --niche fitness --followers 25000
      socialtrends theme-page revenue --niche finance --followers 100000
    """
    from cli_anything.socialtrends.core.theme_pages import get_monetization_timeline

    result = get_monetization_timeline(niche_slug=niche, followers=followers)
    output(result, f"Revenue potential — {niche} @ {followers:,} followers:")


# ── cache group ───────────────────────────────────────────────────────────────

@cli.group()
def cache():
    """Manage API response cache."""
    pass


@cache.command("clear")
@handle_error
def cache_clear() -> None:
    """Clear all cached API responses."""
    from cli_anything.socialtrends.utils.cache import clear_cache
    count = clear_cache()
    output({"cleared_files": count}, f"Cache cleared ({count} files).")


@cache.command("status")
@handle_error
def cache_status() -> None:
    """Show cache directory info."""
    from cli_anything.socialtrends.utils.cache import CACHE_DIR
    if CACHE_DIR.exists():
        files = list(CACHE_DIR.glob("*.json"))
        output({"cache_dir": str(CACHE_DIR), "cached_files": len(files)}, "Cache status:")
    else:
        output({"cache_dir": str(CACHE_DIR), "cached_files": 0}, "No cache yet.")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.socialtrends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "auth setup --youtube-key KEY": "Configure YouTube API key",
        "auth status": "Check configured API keys",
        "trends youtube --region US": "Fetch YouTube trending content",
        "trends tiktok --niche fitness": "Fetch TikTok trends",
        "trends all": "Fetch from all platforms",
        "hashtags suggest --niche fitness --platform tiktok": "Get hashtag set",
        "hashtags score '#gymlife'": "Score a hashtag",
        "hashtags niches": "List all niches",
        "music trending": "Trending music & sounds",
        "music recommend --niche fitness": "Music for your niche",
        "account optimize --platform tiktok --niche fitness --followers 5000": "Full audit",
        "account bio --platform instagram --niche food --name YourName": "Generate bio",
        "account schedule --platform tiktok": "Posting schedule",
        "account caption --topic 'lose belly fat' --niche fitness": "Generate caption",
        "account engagement --followers 10000 --likes 500 --comments 30": "ER calculator",
        "theme-page niches": "List profitable niches",
        "theme-page guide --niche luxury": "Full niche guide",
        "theme-page convert": "Conversion strategies",
        "theme-page playbook": "Growth playbook (0→10k)",
        "theme-page revenue --niche fitness --followers 25000": "Revenue estimate",
        "theme-page sourcing": "Content sourcing methods",
        "cache clear": "Clear API cache",
        "help": "Show this help",
        "quit": "Exit",
    }

    while True:
        try:
            raw = skin.get_input(pt_session)
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
