"""CLI-Anything Social Trends — main CLI entry point."""

import json
import sys
import click

from .core.youtube_scraper import get_trending as yt_trending, get_search_trends
from .core.tiktok_scraper import get_trending as tt_trending, get_hashtag_info
from .core.hashtag_analyzer import analyze_hashtags, get_niche_hashtags, recommend_for_content
from .core.music_tracker import get_trending_music, recommend_music_for_niche
from .core.account_optimizer import get_posting_schedule, optimize_bio as _optimize_bio_fn, get_growth_playbook, audit_account
from .core.theme_page_guide import get_niche_guide, get_setup_checklist, get_content_transformation_guide, generate_brand_pitch
from .utils.backend import load_config, save_config, add_account, get_accounts, format_output


# ---------------------------------------------------------------------------
# CLI root
# ---------------------------------------------------------------------------

@click.group()
@click.option("--json", "json_out", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, json_out):
    """CLI-Anything Social Trends — scrape viral trends, optimize accounts, build theme pages."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_out
    ctx.obj["config"] = load_config()


def _out(ctx, data):
    click.echo(format_output(data, ctx.obj.get("json", False)))


# ---------------------------------------------------------------------------
# trends group
# ---------------------------------------------------------------------------

@cli.group()
def trends():
    """Scrape viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="ISO country code")
@click.option("--category", default="all", show_default=True,
              type=click.Choice(["all","music","gaming","films","entertainment","beauty","news","sports","tech","travel","food"]),
              help="Content category")
@click.option("--limit", default=20, show_default=True, help="Max videos to fetch")
@click.option("--api-key", default=None, help="YouTube Data API v3 key (overrides config)")
@click.pass_context
def trends_youtube(ctx, region, category, limit, api_key):
    """Fetch YouTube trending videos with hashtags and engagement data."""
    config = ctx.obj["config"]
    key = api_key or config.get("youtube_api_key") or None
    result = yt_trending(region=region, category=category, limit=limit, api_key=key)
    _out(ctx, result)


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="ISO country code")
@click.option("--limit", default=20, show_default=True, help="Max videos to fetch")
@click.option("--rapidapi-key", default=None, help="RapidAPI key for TikTok (overrides config)")
@click.option("--use-playwright", is_flag=True, help="Use TikTokApi (requires playwright + ms_token)")
@click.pass_context
def trends_tiktok(ctx, region, limit, rapidapi_key, use_playwright):
    """Fetch TikTok trending videos with hashtags and viral music."""
    config = ctx.obj["config"]
    key = rapidapi_key or config.get("rapidapi_key") or None
    result = tt_trending(region=region, limit=limit, rapidapi_key=key, use_tiktokapi=use_playwright)
    _out(ctx, result)


@trends.command("all")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=10, show_default=True)
@click.pass_context
def trends_all(ctx, region, limit):
    """Fetch trends from ALL platforms simultaneously."""
    config = ctx.obj["config"]
    yt_key = config.get("youtube_api_key") or None
    rap_key = config.get("rapidapi_key") or None

    result = {
        "youtube": yt_trending(region=region, limit=limit, api_key=yt_key),
        "tiktok": tt_trending(region=region, limit=limit, rapidapi_key=rap_key),
    }
    _out(ctx, result)


@trends.command("search")
@click.argument("query")
@click.option("--platform", default="youtube", type=click.Choice(["youtube"]), show_default=True)
@click.option("--limit", default=10, show_default=True)
@click.pass_context
def trends_search(ctx, query, platform, limit):
    """Search for trending content on a specific topic."""
    config = ctx.obj["config"]
    key = config.get("youtube_api_key") or None
    result = get_search_trends(query, limit, key)
    _out(ctx, result)


@trends.command("hashtag")
@click.argument("hashtag")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok"]), show_default=True)
@click.option("--limit", default=10, show_default=True)
@click.pass_context
def trends_hashtag(ctx, hashtag, platform, limit):
    """Fetch top videos for a specific hashtag."""
    config = ctx.obj["config"]
    key = config.get("rapidapi_key") or None
    result = get_hashtag_info(hashtag, limit, key)
    _out(ctx, result)


# ---------------------------------------------------------------------------
# hashtags group
# ---------------------------------------------------------------------------

@cli.group()
def hashtags():
    """Analyze, recommend, and score hashtags."""


@hashtags.command("analyze")
@click.argument("tags", nargs=-1, required=True)
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram"]), show_default=True)
@click.option("--niche", default=None, help="Your content niche for tailored recommendations")
@click.pass_context
def hashtags_analyze(ctx, tags, platform, niche):
    """Analyze a list of hashtags and get ranked recommendations.

    Example: social-trends hashtags analyze #fyp #fitness #gymtok --niche fitness
    """
    result = analyze_hashtags(list(tags), platform, niche)
    _out(ctx, result)


@hashtags.command("niche")
@click.argument("niche")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram"]), show_default=True)
@click.pass_context
def hashtags_niche(ctx, niche, platform):
    """Get the optimal hashtag set for a specific content niche.

    Available niches: motivation, fitness, luxury, aesthetic, food, fashion,
    finance, travel, pets, gaming, beauty, themepage
    """
    result = get_niche_hashtags(niche, platform)
    _out(ctx, result)


@hashtags.command("recommend")
@click.argument("description")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram"]), show_default=True)
@click.option("--count", default=20, show_default=True, help="Number of hashtags to return")
@click.pass_context
def hashtags_recommend(ctx, description, platform, count):
    """Auto-recommend hashtags based on your content description.

    Example: social-trends hashtags recommend "morning workout routine"
    """
    result = recommend_for_content(description, platform, count)
    _out(ctx, result)


# ---------------------------------------------------------------------------
# music group
# ---------------------------------------------------------------------------

@cli.group()
def music():
    """Discover viral music and trending audio."""


@music.command("trending")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram","all"]), show_default=True)
@click.option("--genre", default=None, help="Filter by genre (pop, hip-hop, r&b, indie, etc.)")
@click.option("--mood", default=None, help="Filter by mood (upbeat, emotional, dreamy, etc.)")
@click.option("--limit", default=10, show_default=True)
@click.pass_context
def music_trending(ctx, platform, genre, mood, limit):
    """Show currently trending viral music tracks."""
    result = get_trending_music(platform, genre, mood, limit)
    _out(ctx, result)


@music.command("for-niche")
@click.argument("niche")
@click.pass_context
def music_for_niche(ctx, niche):
    """Get the best trending music tracks for a specific content niche.

    Example: social-trends music for-niche fitness
    """
    result = recommend_music_for_niche(niche)
    _out(ctx, result)


# ---------------------------------------------------------------------------
# optimize group
# ---------------------------------------------------------------------------

@cli.group()
def optimize():
    """Optimize your social media accounts for maximum growth."""


@optimize.command("schedule")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram"]), show_default=True)
@click.option("--timezone-offset", default=0, show_default=True, help="UTC offset (e.g., -5 for EST)")
@click.option("--posts-per-day", default=2, show_default=True)
@click.option("--account-type", default="theme_page", type=click.Choice(["theme_page","creator","brand"]), show_default=True)
@click.pass_context
def optimize_schedule(ctx, platform, timezone_offset, posts_per_day, account_type):
    """Generate an optimal posting schedule for your platform."""
    result = get_posting_schedule(platform, timezone_offset, posts_per_day, account_type)
    _out(ctx, result)


@optimize.command("bio")
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram"]), show_default=True)
@click.option("--niche", default="general", show_default=True)
@click.option("--followers", default=0, show_default=True, type=int)
@click.option("--link-text", default="Free guide", show_default=True)
@click.pass_context
def cmd_optimize_bio(ctx, platform, niche, followers, link_text):
    """Generate an optimized bio for your account."""
    result = _optimize_bio_fn(platform, niche, followers, link_text)
    _out(ctx, result)


@optimize.command("playbook")
@click.argument("followers", type=int)
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok","youtube","instagram"]), show_default=True)
@click.pass_context
def optimize_playbook(ctx, followers, platform):
    """Get the growth playbook for your current follower stage.

    Example: social-trends optimize playbook 5000 --platform tiktok
    """
    result = get_growth_playbook(followers, platform)
    _out(ctx, result)


@optimize.command("audit")
@click.option("--platform", required=True, type=click.Choice(["tiktok","youtube","instagram"]))
@click.option("--username", required=True)
@click.option("--followers", required=True, type=int)
@click.option("--following", default=500, show_default=True, type=int)
@click.option("--posts", default=60, show_default=True, type=int, help="Total posts on account")
@click.option("--avg-views", default=1000, show_default=True, type=int)
@click.option("--avg-likes", default=50, show_default=True, type=int)
@click.option("--niche", default="general", show_default=True)
@click.option("--account-type", default="creator", type=click.Choice(["creator","theme_page","brand"]), show_default=True)
@click.pass_context
def optimize_audit(ctx, platform, username, followers, following, posts, avg_views, avg_likes, niche, account_type):
    """Run a full account audit and get optimization recommendations."""
    result = audit_account(platform, username, followers, following, posts, avg_views, avg_likes, niche, account_type)
    _out(ctx, result)


@optimize.command("all-accounts")
@click.pass_context
def optimize_all_accounts(ctx):
    """Run optimization audit across all registered accounts."""
    accounts = get_accounts()
    if not accounts:
        click.echo("No accounts registered. Use: social-trends accounts add <platform> <username>")
        return
    results = []
    for acc in accounts:
        result = get_growth_playbook(acc.get("followers", 0), acc.get("platform", "tiktok"))
        result["account"] = acc.get("username")
        results.append(result)
    _out(ctx, {"accounts_audited": len(results), "results": results})


# ---------------------------------------------------------------------------
# themepage group
# ---------------------------------------------------------------------------

@cli.group()
def themepage():
    """Learn to build, grow, and monetize theme pages."""


@themepage.command("niches")
@click.option("--niche", default=None, help="Get detailed guide for a specific niche")
@click.pass_context
def themepage_niches(ctx, niche):
    """List all profitable theme page niches or get a detailed guide.

    Example: social-trends themepage niches --niche luxury
    """
    result = get_niche_guide(niche)
    _out(ctx, result)


@themepage.command("checklist")
@click.option("--phase", default=None, type=int, help="Show only a specific phase (1-6)")
@click.pass_context
def themepage_checklist(ctx, phase):
    """Get the step-by-step theme page setup checklist."""
    result = get_setup_checklist(phase)
    _out(ctx, result)


@themepage.command("content-methods")
@click.pass_context
def themepage_content_methods(ctx):
    """Learn legal methods for repurposing viral content."""
    result = get_content_transformation_guide()
    _out(ctx, result)


@themepage.command("pitch")
@click.option("--handle", required=True, help="Your social media handle")
@click.option("--brand", required=True, help="Brand name to pitch")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--followers", required=True, type=int)
@click.option("--platform", default="TikTok", show_default=True)
@click.option("--engagement", default=5.0, show_default=True, type=float, help="Avg engagement rate %")
@click.option("--rate", default=200, show_default=True, type=int, help="Asking rate in USD")
@click.option("--name", default="Creator", show_default=True)
@click.option("--email", default="creator@email.com", show_default=True)
@click.pass_context
def themepage_pitch(ctx, handle, brand, niche, followers, platform, engagement, rate, name, email):
    """Generate a customized brand partnership pitch email."""
    result = generate_brand_pitch(handle, brand, niche, followers, platform, engagement, rate, name, email)
    _out(ctx, result)


# ---------------------------------------------------------------------------
# accounts group
# ---------------------------------------------------------------------------

@cli.group()
def accounts():
    """Manage your social media accounts."""


@accounts.command("add")
@click.argument("platform", type=click.Choice(["tiktok","youtube","instagram"]))
@click.argument("username")
@click.option("--followers", default=0, type=int, show_default=True)
@click.option("--niche", default="general", show_default=True)
@click.pass_context
def accounts_add(ctx, platform, username, followers, niche):
    """Register a social media account for tracking.

    Example: social-trends accounts add tiktok @myaccount --followers 5000 --niche fitness
    """
    result = add_account(platform, username, followers, niche)
    click.echo(f"Account registered: {result['username']} ({result['platform']})")
    _out(ctx, result)


@accounts.command("list")
@click.option("--platform", default=None, type=click.Choice(["tiktok","youtube","instagram"]))
@click.pass_context
def accounts_list(ctx, platform):
    """List all registered accounts."""
    accs = get_accounts(platform)
    if not accs:
        click.echo("No accounts registered yet. Use: social-trends accounts add")
        return
    _out(ctx, {"accounts": accs, "total": len(accs)})


# ---------------------------------------------------------------------------
# config group
# ---------------------------------------------------------------------------

@cli.group()
def config():
    """Manage API keys and settings."""


@config.command("set")
@click.argument("key", type=click.Choice(["youtube_api_key","rapidapi_key","default_region","default_platform"]))
@click.argument("value")
@click.pass_context
def config_set(ctx, key, value):
    """Set a configuration value.

    Example: social-trends config set youtube_api_key AIza...
    """
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    click.echo(f"Config updated: {key} = {'***' if 'key' in key.lower() else value}")


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show current configuration (masks API keys)."""
    cfg = load_config()
    display = {}
    for k, v in cfg.items():
        if "key" in k.lower() and v:
            display[k] = f"{v[:6]}...{v[-4:]}" if len(v) > 10 else "***"
        elif k == "accounts":
            display[k] = f"{len(v)} registered"
        else:
            display[k] = v
    _out(ctx, display)


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

@cli.command("repl")
@click.pass_context
def repl(ctx):
    """Start an interactive REPL session for social trends exploration."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        _rich_repl(ctx)
    except ImportError:
        _basic_repl(ctx)


def _rich_repl(ctx):
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

    session = PromptSession(history=InMemoryHistory(), auto_suggest=AutoSuggestFromHistory())
    click.echo("Social Trends REPL — type 'help' for commands, 'exit' to quit")
    click.echo("Commands: trends youtube | trends tiktok | trends all | hashtags niche <niche>")
    click.echo("          music trending | optimize schedule | themepage niches | exit\n")

    while True:
        try:
            line = session.prompt("social-trends> ").strip()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        if line.lower() == "help":
            ctx.invoke(cli, args=["--help"])
            continue

        args = line.split()
        try:
            cli.main(args=args, standalone_mode=False, obj=ctx.obj.copy())
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def _basic_repl(ctx):
    click.echo("Social Trends REPL — type 'help' for commands, 'exit' to quit")
    while True:
        try:
            line = input("social-trends> ").strip()
        except (KeyboardInterrupt, EOFError):
            click.echo("\nGoodbye!")
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            click.echo("Goodbye!")
            break
        args = line.split()
        try:
            cli.main(args=args, standalone_mode=False, obj=ctx.obj.copy())
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
