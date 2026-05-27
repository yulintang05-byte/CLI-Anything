"""CLI entry-point for Social Trends agent harness."""
from __future__ import annotations
import json
import sys
import click

from .trends import fetch_youtube_trending, fetch_tiktok_trending
from .hashtags import rank_hashtags, get_google_trends
from .music import fetch_trending_music, fetch_tiktok_sounds_chart
from .optimizer import generate_account_audit, optimize_profile
from .theme_pages import get_theme_page_guide


def _out(data: object, pretty: bool) -> None:
    if pretty:
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        click.echo(json.dumps(data, ensure_ascii=False))


@click.group()
@click.version_option("0.1.0", prog_name="social-trends")
def cli() -> None:
    """Social Trends — viral trend scraper & account optimizer."""


# ── trends ────────────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch trending content from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--category", default="now", type=click.Choice(["now", "music", "gaming", "movies"]), show_default=True)
@click.option("--country", default="US", show_default=True, help="ISO 3166-1 alpha-2 country code")
@click.option("--limit", default=20, show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def trends_youtube(category: str, country: str, limit: int, pretty: bool) -> None:
    """Scrape YouTube trending videos."""
    results = fetch_youtube_trending(category=category, country=country, limit=limit)
    _out({"count": len(results), "category": category, "country": country, "items": results}, pretty)


@trends.command("tiktok")
@click.option("--limit", default=20, show_default=True)
@click.option("--region", default="US", show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def trends_tiktok(limit: int, region: str, pretty: bool) -> None:
    """Scrape TikTok trending videos."""
    results = fetch_tiktok_trending(limit=limit, region=region)
    _out({"count": len(results), "region": region, "items": results}, pretty)


@trends.command("all")
@click.option("--limit", default=20, show_default=True)
@click.option("--region", default="US", show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def trends_all(limit: int, region: str, pretty: bool) -> None:
    """Fetch trending content from ALL platforms combined."""
    yt = fetch_youtube_trending(limit=limit, country=region)
    tt = fetch_tiktok_trending(limit=limit, region=region)
    _out({
        "youtube": {"count": len(yt), "items": yt},
        "tiktok": {"count": len(tt), "items": tt},
    }, pretty)


# ── hashtags ─────────────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Extract and rank viral hashtags."""


@hashtags.command("rank")
@click.option("--platform", default="all", type=click.Choice(["youtube", "tiktok", "all"]), show_default=True)
@click.option("--limit", default=25, show_default=True)
@click.option("--region", default="US", show_default=True)
@click.option("--top-n", default=30, show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def hashtags_rank(platform: str, limit: int, region: str, top_n: int, pretty: bool) -> None:
    """Scrape trends then rank hashtags by viral score."""
    items: list = []
    if platform in ("youtube", "all"):
        items.extend(fetch_youtube_trending(limit=limit, country=region))
    if platform in ("tiktok", "all"):
        items.extend(fetch_tiktok_trending(limit=limit, region=region))
    ranked = rank_hashtags(items, top_n=top_n)
    _out({"total_items_analyzed": len(items), "top_hashtags": ranked}, pretty)


@hashtags.command("google-trends")
@click.argument("keywords", nargs=-1, required=True)
@click.option("--timeframe", default="now 7-d", show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def hashtags_google(keywords: tuple[str, ...], timeframe: str, pretty: bool) -> None:
    """Query Google Trends for keywords (requires pytrends)."""
    result = get_google_trends(list(keywords), timeframe=timeframe)
    _out(result, pretty)


# ── music ─────────────────────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Discover trending music and sounds."""


@music.command("trending")
@click.option("--platform", default="all", type=click.Choice(["tiktok", "youtube", "all"]), show_default=True)
@click.option("--limit", default=20, show_default=True)
@click.option("--region", default="US", show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def music_trending(platform: str, limit: int, region: str, pretty: bool) -> None:
    """Fetch trending music/sounds across platforms."""
    results = fetch_trending_music(platform=platform, limit=limit, region=region)
    _out({"count": len(results), "platform": platform, "music": results}, pretty)


@music.command("tiktok-charts")
@click.option("--limit", default=20, show_default=True)
@click.option("--pretty", is_flag=True, default=True)
def music_tiktok_charts(limit: int, pretty: bool) -> None:
    """Pull TikTok Creative Center top sounds chart."""
    results = fetch_tiktok_sounds_chart(limit=limit)
    _out({"count": len(results), "source": "tiktok_creative_center", "charts": results}, pretty)


# ── optimize ─────────────────────────────────────────────────────────────────

@cli.group()
def optimize() -> None:
    """Audit and optimize social media accounts."""


@optimize.command("audit")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "x_twitter"]), help="Platform to audit")
@click.option("--username", required=True)
@click.option("--niche", default="", help="Content niche (e.g. fitness, finance, comedy)")
@click.option("--followers", default=0, type=int)
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
@click.option("--bio", default="", help="Your current bio text")
@click.option("--hashtags-used", default="", help="Comma-separated current hashtags")
@click.option("--posting-freq", default="", help="Current posting frequency (e.g. '3x/week')")
@click.option("--pretty", is_flag=True, default=True)
def optimize_audit(
    platform: str, username: str, niche: str, followers: int,
    avg_views: int, avg_likes: int, bio: str, hashtags_used: str,
    posting_freq: str, pretty: bool,
) -> None:
    """Run a full account audit and get an action plan."""
    htags = [h.strip() for h in hashtags_used.split(",") if h.strip()] if hashtags_used else []
    result = generate_account_audit(
        platform=platform,
        username=username,
        niche=niche,
        current_followers=followers,
        avg_views=avg_views,
        avg_likes=avg_likes,
        bio=bio,
        posting_frequency=posting_freq,
        current_hashtags=htags,
    )
    _out(result, pretty)


@optimize.command("profile")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "x_twitter"]))
@click.option("--niche", required=True)
@click.option("--bio", default="", help="Current bio (optional — for comparison)")
@click.option("--username", default="")
@click.option("--pretty", is_flag=True, default=True)
def optimize_profile_cmd(platform: str, niche: str, bio: str, username: str, pretty: bool) -> None:
    """Generate optimized bio, hashtag stack, and content calendar."""
    result = optimize_profile(platform=platform, niche=niche, current_bio=bio, username=username)
    _out(result, pretty)


@optimize.command("all-platforms")
@click.option("--niche", required=True)
@click.option("--pretty", is_flag=True, default=True)
def optimize_all_platforms(niche: str, pretty: bool) -> None:
    """Generate optimization plan for TikTok + Instagram + YouTube + Twitter simultaneously."""
    platforms = ["tiktok", "instagram", "youtube", "x_twitter"]
    result = {p: optimize_profile(platform=p, niche=niche) for p in platforms}
    _out({"niche": niche, "platforms": result}, pretty)


# ── theme-page ────────────────────────────────────────────────────────────────

@cli.group()
def theme_page() -> None:
    """Create and monetize theme pages."""


@theme_page.command("guide")
@click.option("--niche", default="general", show_default=True)
@click.option("--goal", default="monetize", type=click.Choice(["monetize", "grow", "convert"]), show_default=True, help="'convert' for turning personal page into theme page")
@click.option("--followers", default=0, type=int, help="Current follower count")
@click.option("--pretty", is_flag=True, default=True)
def theme_guide(niche: str, goal: str, followers: int, pretty: bool) -> None:
    """Get the complete theme page playbook for your niche."""
    result = get_theme_page_guide(niche=niche, goal=goal, current_followers=followers)
    _out(result, pretty)


@theme_page.command("monetization")
@click.option("--followers", default=0, type=int, required=True)
@click.option("--niche", default="general")
@click.option("--pretty", is_flag=True, default=True)
def theme_monetization(followers: int, niche: str, pretty: bool) -> None:
    """Get monetization roadmap for your current follower count."""
    guide = get_theme_page_guide(niche=niche, goal="monetize", current_followers=followers)
    _out({
        "followers": followers,
        "niche": niche,
        "monetization_roadmap": guide["monetization_roadmap"],
        "income_potential": guide["overview"]["income_potential"],
    }, pretty)


# ── full workflow ─────────────────────────────────────────────────────────────

@cli.command("full-report")
@click.option("--niche", required=True)
@click.option("--platform", default="tiktok", type=click.Choice(["tiktok", "youtube", "instagram", "x_twitter"]))
@click.option("--username", default="my_account")
@click.option("--followers", default=0, type=int)
@click.option("--region", default="US")
@click.option("--pretty", is_flag=True, default=True)
def full_report(niche: str, platform: str, username: str, followers: int, region: str, pretty: bool) -> None:
    """
    Run the complete viral intelligence + account optimization pipeline.
    Fetches trends, extracts top hashtags, finds trending music, audits account, and outputs theme page guide.
    """
    click.echo("Fetching trends...", err=True)
    yt_items = fetch_youtube_trending(limit=20, country=region)
    tt_items = fetch_tiktok_trending(limit=20, region=region)
    all_items = yt_items + tt_items

    click.echo("Ranking hashtags...", err=True)
    top_hashtags = rank_hashtags(all_items, top_n=20)

    click.echo("Fetching trending music...", err=True)
    trending_music = fetch_tiktok_sounds_chart(limit=10)

    click.echo("Auditing account...", err=True)
    audit = generate_account_audit(
        platform=platform, username=username,
        niche=niche, current_followers=followers,
    )

    click.echo("Building theme page guide...", err=True)
    theme = get_theme_page_guide(niche=niche, goal="monetize", current_followers=followers)

    _out({
        "report": "viral_intelligence_full",
        "niche": niche,
        "region": region,
        "trending_videos": {
            "youtube": len(yt_items),
            "tiktok": len(tt_items),
        },
        "top_hashtags": top_hashtags[:15],
        "trending_music": trending_music[:10],
        "account_audit": audit,
        "theme_page_guide": {
            "setup_checklist": theme["setup_checklist"],
            "content_strategy": theme["content_strategy"],
            "growth_hacks": theme["growth_hacks"],
            "monetization_roadmap": theme["monetization_roadmap"],
        },
    }, pretty)


def main() -> None:
    cli()
