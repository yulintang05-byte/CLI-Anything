"""
socials — CLI harness for social media trend research, optimization, and growth.

Usage:
  socials trends youtube [--api-key KEY] [--region US] [--category all] [--limit 25]
  socials trends tiktok [--region US] [--limit 25]
  socials trends all [--region US] [--limit 20]
  socials music trending [--platform tiktok|youtube] [--region US]
  socials music strategy <content_type>
  socials music times <platform> [--region US]
  socials hashtags trending [--region US] [--period 7] [--limit 30]
  socials hashtags build <niche> [--platform tiktok] [--strategy balanced] [--max-tags 30]
  socials hashtags research <tag> [--platform tiktok]
  socials hashtags score <tag1> <tag2> ...
  socials account audit <platform> <username> [OPTIONS]
  socials account bio-guide <platform>
  socials account score-bio <platform> <bio>
  socials account content-plan <niche> [--platform tiktok] [--posts-per-week 5]
  socials account playbook [--stage 0_to_1k|1k_to_10k|10k_to_100k]
  socials theme-pages list
  socials theme-pages blueprint <niche>
  socials theme-pages recommend [--interests X Y] [--risk low|medium|high]
  socials theme-pages roadmap
  socials theme-pages stage <followers>
  socials theme-pages acquire
  socials repl
"""
from __future__ import annotations

import json
import os
import sys

import click

from cli_anything.social_media import trends as _trends
from cli_anything.social_media import hashtags as _hashtags
from cli_anything.social_media import music as _music
from cli_anything.social_media import account as _account
from cli_anything.social_media import theme_pages as _theme


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _out(data: object, human: bool = False) -> None:
    """Print data. In human mode show pretty tables; otherwise emit JSON."""
    if human:
        _human_print(data)
    else:
        click.echo(json.dumps(data, indent=2, default=str))


def _human_print(data: object, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{click.style(str(k), bold=True)}:")
                _human_print(v, indent + 1)
            else:
                click.echo(f"{pad}{click.style(str(k), bold=True)}: {v}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}[{i+1}]")
                _human_print(item, indent + 1)
            else:
                click.echo(f"{pad}• {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    click.echo(json.dumps({"error": msg}), err=True)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Root group
# ---------------------------------------------------------------------------

@click.group()
@click.option("--human", is_flag=True, default=False, help="Human-readable output instead of JSON")
@click.pass_context
def main(ctx: click.Context, human: bool) -> None:
    """socials — agent-native social media research and optimization CLI."""
    ctx.ensure_object(dict)
    ctx.obj["human"] = human


# ---------------------------------------------------------------------------
# trends
# ---------------------------------------------------------------------------

@main.group()
def trends() -> None:
    """Fetch viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None, help="YouTube Data API v3 key")
@click.option("--region", default="US", show_default=True, help="Country code (US, UK, CA, AU...)")
@click.option("--category", default="all", show_default=True,
              type=click.Choice(list(_trends.YOUTUBE_CATEGORY_IDS.keys()), case_sensitive=False),
              help="Video category")
@click.option("--limit", default=25, show_default=True, type=int, help="Number of results")
@click.pass_context
def trends_youtube(ctx: click.Context, api_key: str, region: str, category: str, limit: int) -> None:
    """Fetch YouTube trending videos. Uses official API if --api-key provided, else scrapes public page."""
    try:
        if api_key:
            result = _trends.fetch_youtube_trending(api_key, region=region, category=category, limit=limit)
        else:
            click.echo('{"info": "No API key provided — scraping public YouTube trending page. Use --api-key or set YOUTUBE_API_KEY for more reliable results."}', err=True)
            result = _trends.fetch_youtube_trending_no_key(region=region, limit=limit)
        _out(result.to_dict(), ctx.obj["human"])
    except Exception as e:
        _err(str(e))


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Country code")
@click.option("--limit", default=25, show_default=True, type=int, help="Number of results")
@click.pass_context
def trends_tiktok(ctx: click.Context, region: str, limit: int) -> None:
    """Fetch TikTok viral trending content via public endpoints."""
    try:
        result = _trends.fetch_tiktok_trending(limit=limit, region=region)
        _out(result.to_dict(), ctx.obj["human"])
    except Exception as e:
        _err(str(e))


@trends.command("all")
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None, help="YouTube Data API v3 key")
@click.option("--region", default="US", show_default=True)
@click.option("--limit", default=20, show_default=True, type=int)
@click.pass_context
def trends_all(ctx: click.Context, api_key: str, region: str, limit: int) -> None:
    """Fetch trending from both YouTube and TikTok in one call."""
    try:
        result = _trends.fetch_all_trending(youtube_api_key=api_key, region=region, limit=limit)
        _out(result, ctx.obj["human"])
    except Exception as e:
        _err(str(e))


# ---------------------------------------------------------------------------
# music
# ---------------------------------------------------------------------------

@main.group()
def music() -> None:
    """Trending music, sounds, and posting time strategies."""


@music.command("trending")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube"], case_sensitive=False))
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=click.Choice(["1", "7", "30"]))
@click.option("--limit", default=25, show_default=True, type=int)
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None, help="Required for YouTube music")
@click.pass_context
def music_trending(ctx: click.Context, platform: str, region: str, period: str, limit: int, api_key: str) -> None:
    """Fetch trending sounds/music for a platform."""
    try:
        if platform == "tiktok":
            result = _music.fetch_tiktok_trending_sounds(region=region, period=int(period), limit=limit)
        else:
            if not api_key:
                _err("YouTube music trending requires a --api-key or YOUTUBE_API_KEY env var.")
            result = _music.fetch_youtube_trending_music(api_key=api_key, region=region, limit=limit)
        _out(result.to_dict(), ctx.obj["human"])
    except Exception as e:
        _err(str(e))


@music.command("strategy")
@click.argument("content_type", type=click.Choice(list(_music.SOUND_STRATEGY.keys())))
@click.pass_context
def music_strategy(ctx: click.Context, content_type: str) -> None:
    """Get sound usage strategy for a content type."""
    try:
        _out(_music.get_sound_strategy(content_type), ctx.obj["human"])
    except Exception as e:
        _err(str(e))


@music.command("strategies")
@click.pass_context
def music_strategies(ctx: click.Context) -> None:
    """List all available sound strategies."""
    _out(_music.list_sound_strategies(), ctx.obj["human"])


@music.command("times")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--region", default="US", show_default=True)
@click.pass_context
def music_times(ctx: click.Context, platform: str, region: str) -> None:
    """Get peak posting times for a platform."""
    try:
        result = _music.get_peak_posting_times(platform, region)
        _out({"platform": platform, "region": region, "peak_windows": result}, ctx.obj["human"])
    except Exception as e:
        _err(str(e))


# ---------------------------------------------------------------------------
# hashtags
# ---------------------------------------------------------------------------

@main.group()
def hashtags() -> None:
    """Hashtag research, set building, and optimization."""


@hashtags.command("trending")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7, show_default=True, type=click.Choice(["1", "7", "30"]))
@click.option("--limit", default=30, show_default=True, type=int)
@click.pass_context
def hashtags_trending(ctx: click.Context, region: str, period: str, limit: int) -> None:
    """Fetch trending TikTok hashtags from Creative Center."""
    try:
        result = _hashtags.fetch_tiktok_trending_hashtags(region=region, period=int(period), limit=limit)
        _out([h.to_dict() for h in result], ctx.obj["human"])
    except Exception as e:
        _err(str(e))


@hashtags.command("build")
@click.argument("niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram"], case_sensitive=False))
@click.option("--strategy", default="balanced", show_default=True,
              type=click.Choice(["broad", "niche", "micro", "balanced"]))
@click.option("--max-tags", default=30, show_default=True, type=int)
@click.pass_context
def hashtags_build(ctx: click.Context, niche: str, platform: str, strategy: str, max_tags: int) -> None:
    """Build an optimized hashtag set for a niche."""
    result = _hashtags.build_hashtag_set(niche=niche, platform=platform, strategy=strategy, max_tags=max_tags)
    _out(result.to_dict(), ctx.obj["human"])


@hashtags.command("research")
@click.argument("tag")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram"]))
@click.pass_context
def hashtags_research(ctx: click.Context, tag: str, platform: str) -> None:
    """Research a single hashtag for stats and difficulty."""
    try:
        result = _hashtags.research_hashtag(tag, platform=platform)
        _out(result.to_dict(), ctx.obj["human"])
    except Exception as e:
        _err(str(e))


@hashtags.command("score")
@click.argument("tags", nargs=-1, required=True)
@click.pass_context
def hashtags_score(ctx: click.Context, tags: tuple) -> None:
    """Score a list of hashtags for balance and strategy quality."""
    result = _hashtags.score_hashtag_set(list(tags))
    _out(result, ctx.obj["human"])


@hashtags.command("niches")
@click.pass_context
def hashtags_niches(ctx: click.Context) -> None:
    """List available niche seed sets."""
    _out({"available_niches": list(_hashtags.NICHE_SEEDS.keys())}, ctx.obj["human"])


# ---------------------------------------------------------------------------
# account
# ---------------------------------------------------------------------------

@main.group()
def account() -> None:
    """Account auditing, bio optimization, and growth playbooks."""


@account.command("audit")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.argument("username")
@click.option("--bio", default=None, help="Your current bio text")
@click.option("--posts-per-week", type=float, default=None)
@click.option("--avg-views", type=int, default=None)
@click.option("--followers", type=int, default=None)
@click.option("--has-pic/--no-pic", default=True)
@click.option("--has-link/--no-link", default=False)
@click.option("--consistent/--not-consistent", default=False)
@click.option("--trending-audio/--no-trending-audio", default=False)
@click.option("--uses-hashtags/--no-hashtags", default=False)
@click.option("--branded/--not-branded", default=False)
@click.pass_context
def account_audit(
    ctx: click.Context,
    platform: str, username: str, bio: str,
    posts_per_week: float, avg_views: int, followers: int,
    has_pic: bool, has_link: bool, consistent: bool,
    trending_audio: bool, uses_hashtags: bool, branded: bool,
) -> None:
    """Audit a social media account and get an optimization report."""
    result = _account.audit_account(
        platform=platform,
        username=username,
        bio=bio,
        posts_per_week=posts_per_week,
        avg_views=avg_views,
        follower_count=followers,
        has_profile_pic=has_pic,
        has_link_in_bio=has_link,
        posts_consistent=consistent,
        uses_trending_audio=trending_audio,
        uses_hashtags=uses_hashtags,
        has_branded_content=branded,
    )
    _out(result.to_dict(), ctx.obj["human"])


@account.command("bio-guide")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.pass_context
def account_bio_guide(ctx: click.Context, platform: str) -> None:
    """Get bio optimization guide and templates for a platform."""
    _out(_account.get_bio_guide(platform), ctx.obj["human"])


@account.command("score-bio")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.argument("bio")
@click.pass_context
def account_score_bio(ctx: click.Context, platform: str, bio: str) -> None:
    """Score your bio and get improvement feedback (0-100)."""
    _out(_account.score_bio(bio, platform), ctx.obj["human"])


@account.command("content-plan")
@click.argument("niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube"]))
@click.option("--posts-per-week", default=5, show_default=True, type=int)
@click.pass_context
def account_content_plan(ctx: click.Context, niche: str, platform: str, posts_per_week: int) -> None:
    """Generate a weekly content plan with hooks, pillars, and CTAs."""
    result = _account.get_content_plan(niche, platform=platform, posts_per_week=posts_per_week)
    _out(result.to_dict(), ctx.obj["human"])


@account.command("playbook")
@click.option("--stage", default=None,
              type=click.Choice(["0_to_1k", "1k_to_10k", "10k_to_100k"]),
              help="Your current follower stage")
@click.option("--followers", type=int, default=None, help="Your follower count (auto-selects stage)")
@click.pass_context
def account_playbook(ctx: click.Context, stage: str, followers: int) -> None:
    """Get an actionable growth playbook for your follower stage."""
    if stage:
        _out(_account.get_growth_playbook(stage), ctx.obj["human"])
    elif followers is not None:
        if followers < 1000:
            s = "0_to_1k"
        elif followers < 10000:
            s = "1k_to_10k"
        else:
            s = "10k_to_100k"
        _out(_account.get_growth_playbook(s), ctx.obj["human"])
    else:
        _out(_account.list_growth_playbooks(), ctx.obj["human"])


# ---------------------------------------------------------------------------
# theme-pages
# ---------------------------------------------------------------------------

@main.group("theme-pages")
def theme_pages() -> None:
    """Theme page creation, growth, and conversion playbooks."""


@theme_pages.command("list")
@click.pass_context
def tp_list(ctx: click.Context) -> None:
    """List all available theme page niches."""
    _out(_theme.list_niches(), ctx.obj["human"])


@theme_pages.command("blueprint")
@click.argument("niche")
@click.pass_context
def tp_blueprint(ctx: click.Context, niche: str) -> None:
    """Get a full theme page blueprint for a niche (names, bio, content, monetization)."""
    try:
        result = _theme.get_niche_blueprint(niche)
        _out(result.to_dict(), ctx.obj["human"])
    except ValueError as e:
        _err(str(e))


@theme_pages.command("recommend")
@click.option("--interests", multiple=True, help="Your interests or skills")
@click.option("--risk", default="medium", show_default=True,
              type=click.Choice(["low", "medium", "high"]))
@click.option("--time", "time_available", default="1-2 hours/day", show_default=True,
              type=click.Choice(["<1 hour/day", "1-2 hours/day", "3+ hours/day"]))
@click.pass_context
def tp_recommend(ctx: click.Context, interests: tuple, risk: str, time_available: str) -> None:
    """Get personalized niche recommendations based on your interests."""
    result = _theme.recommend_niche(list(interests), risk_tolerance=risk, time_available=time_available)
    _out(result, ctx.obj["human"])


@theme_pages.command("roadmap")
@click.pass_context
def tp_roadmap(ctx: click.Context) -> None:
    """Show the full theme page → monetization conversion roadmap."""
    _out(_theme.get_conversion_roadmap(), ctx.obj["human"])


@theme_pages.command("stage")
@click.argument("followers", type=int)
@click.pass_context
def tp_stage(ctx: click.Context, followers: int) -> None:
    """Get conversion strategy for your current follower count."""
    _out(_theme.get_conversion_stage(followers), ctx.obj["human"])


@theme_pages.command("acquire")
@click.pass_context
def tp_acquire(ctx: click.Context) -> None:
    """Guide for buying existing theme pages (what to look for, pricing, red flags)."""
    _out(_theme.get_acquisition_guide(), ctx.obj["human"])


# ---------------------------------------------------------------------------
# REPL
# ---------------------------------------------------------------------------

@main.command()
@click.pass_context
def repl(ctx: click.Context) -> None:
    """Interactive REPL mode — type commands without the 'socials' prefix."""
    import shlex
    click.echo('socials REPL — type "help" to list commands, "exit" to quit.')
    while True:
        try:
            line = click.prompt("socials>", prompt_suffix=" ")
        except (EOFError, KeyboardInterrupt):
            break
        line = line.strip()
        if not line:
            continue
        if line in ("exit", "quit", "q"):
            break
        if line in ("help", "?"):
            click.echo(__doc__)
            continue
        try:
            args = shlex.split(line)
            main.main(args=args, standalone_mode=False, obj={"human": True})
        except SystemExit:
            pass
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
