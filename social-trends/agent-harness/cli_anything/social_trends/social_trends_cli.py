#!/usr/bin/env python3
"""Social Trends CLI — Viral trend scraping, account optimisation, and theme page strategy.

Usage:
    # Fetch YouTube trending
    cli-anything-social-trends trends fetch youtube --region US --category music

    # Fetch TikTok viral content
    cli-anything-social-trends trends fetch tiktok --niche fitness --limit 20

    # Cross-platform trend report
    cli-anything-social-trends trends report --region US

    # Analyse hashtags
    cli-anything-social-trends hashtags analyze --platform tiktok --niche gym

    # Suggest hashtag set for caption
    cli-anything-social-trends hashtags suggest --niche travel --platform tiktok

    # Trending music / sounds
    cli-anything-social-trends music trending --platform all --region US

    # Search a track's virality
    cli-anything-social-trends music search "Flowers" "Miley Cyrus"

    # Optimise an account
    cli-anything-social-trends account optimize --platform tiktok --niche finance

    # Posting schedule
    cli-anything-social-trends account schedule --platform tiktok

    # Generate bio templates
    cli-anything-social-trends account bio --platform tiktok --niche fitness

    # Theme page niche ranking
    cli-anything-social-trends theme-page niches

    # Full strategy roadmap
    cli-anything-social-trends theme-page strategy --niche "Fitness / Gym"

    # Conversion funnel
    cli-anything-social-trends theme-page convert --niche finance

    # Repost ethics guide
    cli-anything-social-trends theme-page ethics

    # Interactive REPL
    cli-anything-social-trends repl
"""

import json
import os
import sys

import click

from cli_anything.social_trends.utils.repl_skin import ReplSkin

# ── Output helpers ─────────────────────────────────────────────────────────────

_json_mode = False


def _out(data: object, message: str = "") -> None:
    if _json_mode:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data: object, indent: int = 0) -> None:
    pad = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{click.style(k, bold=True)}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{click.style(k, bold=True)}: {v}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                _pretty(item, indent)
                click.echo(f"{pad}{'─' * 40}")
            else:
                click.echo(f"{pad}• {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    click.echo(click.style(f"ERROR: {msg}", fg="red"), err=True)


def _info(msg: str) -> None:
    if not _json_mode:
        click.echo(click.style(f"  {msg}", fg="cyan"))


def _table(headers: list[str], rows: list[list], col_widths: list[int] | None = None) -> None:
    if _json_mode:
        return
    try:
        from tabulate import tabulate
        click.echo(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    except ImportError:
        # Fallback plain table
        if not col_widths:
            col_widths = [max(len(str(r[i])) for r in ([headers] + rows)) for i in range(len(headers))]
        header_row = "  ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
        click.echo(click.style(header_row, bold=True))
        click.echo("─" * sum(col_widths))
        for row in rows:
            click.echo("  ".join(str(c).ljust(w) for c, w in zip(row, col_widths)))


# ── Root group ────────────────────────────────────────────────────────────────

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--json", "use_json", is_flag=True, help="Output JSON instead of human-readable text.")
@click.version_option("1.0.0", prog_name="cli-anything-social-trends")
def main(use_json: bool) -> None:
    """Social Trends CLI — scrape viral trends, optimise accounts, build theme pages."""
    global _json_mode
    _json_mode = use_json


# ── trends ────────────────────────────────────────────────────────────────────

@main.group()
def trends() -> None:
    """Scrape viral trends from YouTube and TikTok."""


@trends.group("fetch")
def trends_fetch() -> None:
    """Fetch trending content from a specific platform."""


@trends_fetch.command("youtube")
@click.option("--region", "-r", default="US", show_default=True, help="ISO country code (US, GB, IN…)")
@click.option("--category", "-c", default="all", show_default=True,
              help="Category slug (all, music, gaming, sports, entertainment…)")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of videos to fetch (max 50)")
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None, help="YouTube Data API v3 key")
def trends_youtube(region: str, category: str, limit: int, api_key: str | None) -> None:
    """Fetch trending YouTube videos with tags and engagement data."""
    from cli_anything.social_trends.core.youtube_trends import fetch_trending, extract_top_tags

    _info(f"Fetching YouTube trending [{category}] for region {region}…")
    try:
        videos = fetch_trending(region=region, category=category, max_results=limit, api_key=api_key)
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)

    if not videos:
        _err("No results returned — check region/category or API key.")
        sys.exit(1)

    if _json_mode:
        _out([v.to_dict() for v in videos])
        return

    headers = ["#", "Title", "Channel", "Views", "Likes", "Eng%", "Duration", "Tags"]
    rows = [
        [
            i,
            v.title[:50] + ("…" if len(v.title) > 50 else ""),
            v.channel[:25],
            f"{v.view_count:,}",
            f"{v.like_count:,}",
            f"{v.engagement_rate}%",
            v.duration,
            ", ".join(v.tags[:4]) or "—",
        ]
        for i, v in enumerate(videos, 1)
    ]
    _table(headers, rows)

    top_tags = extract_top_tags(videos, top_n=15)
    if top_tags:
        click.echo()
        click.echo(click.style("  Top Tags Across Trending Videos:", bold=True))
        tag_rows = [[rank, f"#{tag}", count] for rank, (tag, count) in enumerate(top_tags, 1)]
        _table(["#", "Tag", "Frequency"], tag_rows)


@trends_fetch.command("tiktok")
@click.option("--region", "-r", default="US", show_default=True, help="Region code")
@click.option("--niche", "-n", default="all", show_default=True,
              help="Niche (all, fitness, beauty, food, gaming, travel, finance…)")
@click.option("--hashtag", "-H", default="fyp", show_default=True, help="Hashtag to search viral videos for")
@click.option("--limit", "-l", default=20, show_default=True, help="Number of results")
def trends_tiktok(region: str, niche: str, hashtag: str, limit: int) -> None:
    """Fetch TikTok viral hashtags, sounds, and video metadata."""
    from cli_anything.social_trends.core.tiktok_trends import (
        fetch_trending_hashtags, fetch_trending_sounds, fetch_trending_videos,
    )

    _info(f"Fetching TikTok trends [{niche}] for region {region}…")

    try:
        hashtags = fetch_trending_hashtags(region=region, niche=niche, limit=limit)
        sounds = fetch_trending_sounds(region=region, niche=niche, limit=10)
        videos = fetch_trending_videos(hashtag=hashtag, region=region, limit=10)
    except Exception as exc:
        _err(str(exc))
        sys.exit(1)

    if _json_mode:
        _out({
            "hashtags": [h.to_dict() for h in hashtags],
            "sounds": [s.to_dict() for s in sounds],
            "videos": [v.to_dict() for v in videos],
        })
        return

    if hashtags:
        click.echo(click.style(f"\n  Trending Hashtags ({region} · {niche}):", bold=True))
        rows = [
            [h.rank, f"#{h.name}", f"{h.post_count:,}", f"{h.view_count:,}", h.trend_score]
            for h in hashtags[:15]
        ]
        _table(["#", "Hashtag", "Posts", "Views", "Trend Score"], rows)

    if sounds:
        click.echo(click.style(f"\n  Trending Sounds ({region}):", bold=True))
        rows = [
            [s.rank, s.title[:40], s.artist[:25], f"{s.clip_count:,}", s.virality_label]
            for s in sounds
        ]
        _table(["#", "Track", "Artist", "Uses", "Virality"], rows)

    if videos:
        click.echo(click.style(f"\n  Top Videos — #{hashtag}:", bold=True))
        rows = [
            [
                v.author[:20],
                v.description[:45] + "…" if len(v.description) > 45 else v.description,
                f"{v.play_count:,}",
                f"{v.like_count:,}",
                f"{v.engagement_rate}%",
            ]
            for v in videos[:8]
        ]
        _table(["Creator", "Caption", "Plays", "Likes", "Eng%"], rows)


@trends.command("report")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--niche", "-n", default="all", show_default=True)
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None)
def trends_report(region: str, niche: str, api_key: str | None) -> None:
    """Combined cross-platform trend report (YouTube + TikTok)."""
    from cli_anything.social_trends.core.youtube_trends import fetch_trending, extract_top_tags
    from cli_anything.social_trends.core.tiktok_trends import fetch_trending_hashtags

    _info(f"Building cross-platform report [{region} · {niche}]…")

    yt_error = tt_error = None
    yt_videos, tt_hashtags = [], []

    try:
        yt_videos = fetch_trending(region=region, category=niche if niche != "all" else "all",
                                   max_results=10, api_key=api_key)
    except Exception as exc:
        yt_error = str(exc)

    try:
        tt_hashtags = fetch_trending_hashtags(region=region, niche=niche, limit=15)
    except Exception as exc:
        tt_error = str(exc)

    report = {
        "region": region,
        "niche": niche,
        "youtube": {
            "status": "error" if yt_error else "ok",
            "error": yt_error,
            "top_videos": [v.to_dict() for v in yt_videos[:5]],
            "top_tags": [{"tag": t, "count": c} for t, c in extract_top_tags(yt_videos, 10)],
        },
        "tiktok": {
            "status": "error" if tt_error else "ok",
            "error": tt_error,
            "top_hashtags": [h.to_dict() for h in tt_hashtags[:10]],
        },
    }

    if _json_mode:
        _out(report)
        return

    click.echo(click.style(f"\n  CROSS-PLATFORM TREND REPORT — {region} / {niche.upper()}", bold=True))
    click.echo()

    # YouTube section
    click.echo(click.style("  YouTube Trending:", fg="red", bold=True))
    if yt_error:
        click.echo(f"  {click.style('⚠', fg='yellow')} {yt_error}")
    elif yt_videos:
        for i, v in enumerate(yt_videos[:5], 1):
            click.echo(f"  {i}. {v.title[:60]} — {v.channel} ({v.view_count:,} views)")

    click.echo()

    # TikTok section
    click.echo(click.style("  TikTok Trending Hashtags:", fg="cyan", bold=True))
    if tt_error:
        click.echo(f"  {click.style('⚠', fg='yellow')} {tt_error}")
    elif tt_hashtags:
        for h in tt_hashtags[:8]:
            click.echo(f"  #{h.name:<25} {h.post_count:>10,} posts   {h.view_count:>15,} views")


# ── hashtags ──────────────────────────────────────────────────────────────────

@main.group()
def hashtags() -> None:
    """Analyse and suggest optimised hashtag sets."""


@hashtags.command("analyze")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "all"]), help="Platform to analyse")
@click.option("--niche", "-n", default="all", show_default=True)
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-l", default=30, show_default=True)
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None)
def hashtags_analyze(platform: str, niche: str, region: str, limit: int, api_key: str | None) -> None:
    """Rank trending hashtags by reach, competition, and opportunity score."""
    from cli_anything.social_trends.core import hashtag_analyzer as ha
    from cli_anything.social_trends.core.tiktok_trends import fetch_trending_hashtags
    from cli_anything.social_trends.core.youtube_trends import fetch_trending, extract_top_tags

    tt_scores: list = []
    yt_scores: list = []

    if platform in ("tiktok", "all"):
        _info("Fetching TikTok hashtags…")
        try:
            tt_tags = fetch_trending_hashtags(region=region, niche=niche, limit=limit)
            tt_scores = ha.score_tiktok_hashtags(tt_tags)
        except Exception as exc:
            _err(f"TikTok: {exc}")

    if platform in ("youtube", "all"):
        _info("Fetching YouTube tags…")
        try:
            yt_videos = fetch_trending(region=region, category=niche if niche != "all" else "all",
                                       max_results=50, api_key=api_key)
            tag_counts = extract_top_tags(yt_videos, top_n=limit)
            yt_scores = ha.score_youtube_tags(tag_counts)
        except Exception as exc:
            _err(f"YouTube: {exc}")

    if platform == "all" and tt_scores and yt_scores:
        scores = ha.merge_platform_scores(tt_scores, yt_scores)
    elif tt_scores:
        scores = sorted(tt_scores, key=lambda s: s.opportunity_score, reverse=True)
    elif yt_scores:
        scores = sorted(yt_scores, key=lambda s: s.opportunity_score, reverse=True)
    else:
        _err("No data returned from any platform.")
        sys.exit(1)

    if _json_mode:
        _out([s.to_dict() for s in scores])
        return

    headers = ["Tag", "Platform", "Reach", "Competition", "Opportunity", "Velocity%", "Posts", "Recommended"]
    rows = [
        [
            s.tag,
            s.platform,
            f"{s.reach_score:.1f}",
            f"{s.competition_score:.1f}",
            f"{s.opportunity_score:.1f}",
            f"{s.trend_velocity:.1f}",
            f"{s.post_count:,}",
            "✓" if s.recommended else "",
        ]
        for s in scores[:30]
    ]
    _table(headers, rows)


@hashtags.command("suggest")
@click.option("--niche", "-n", required=True, help="Your content niche (fitness, travel, food…)")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube"]))
@click.option("--count", "-c", default=30, show_default=True, help="Number of hashtags in the set")
@click.option("--mix", "-m", default="balanced", show_default=True,
              type=click.Choice(["balanced", "viral", "niche"]),
              help="Hashtag strategy: balanced, viral (max reach), or niche (low competition)")
@click.option("--region", "-r", default="US", show_default=True)
def hashtags_suggest(niche: str, platform: str, count: int, mix: str, region: str) -> None:
    """Generate an optimal hashtag set ready to paste into your caption."""
    from cli_anything.social_trends.core import hashtag_analyzer as ha
    from cli_anything.social_trends.core.tiktok_trends import fetch_trending_hashtags

    _info(f"Building {mix} hashtag set for #{niche} on {platform}…")

    scores: list = []
    try:
        tt_tags = fetch_trending_hashtags(region=region, niche=niche, limit=50)
        scores = ha.score_tiktok_hashtags(tt_tags)
    except Exception:
        pass

    if scores:
        caption_set = ha.build_caption_set(scores, platform=platform, count=count, mix=mix)
    else:
        _info("Live scrape unavailable — using curated starter set.")
        caption_set = ha.suggest_for_niche(niche, count=count)

    if _json_mode:
        _out({"platform": platform, "niche": niche, "mix": mix, "hashtags": caption_set})
        return

    click.echo(click.style(f"\n  Hashtag Set ({mix}) for #{niche} on {platform.title()}:", bold=True))
    click.echo()
    click.echo("  " + " ".join(caption_set))
    click.echo()
    click.echo(click.style(f"  Total: {len(caption_set)} hashtags — copy the line above into your caption.", fg="green"))


# ── music ─────────────────────────────────────────────────────────────────────

@main.group()
def music() -> None:
    """Track viral music and sounds across platforms."""


@music.command("trending")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "all"]))
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--niche", "-n", default="all", show_default=True)
@click.option("--limit", "-l", default=20, show_default=True)
@click.option("--api-key", envvar="YOUTUBE_API_KEY", default=None)
def music_trending(platform: str, region: str, niche: str, limit: int, api_key: str | None) -> None:
    """List the most viral songs and sounds currently dominating feeds."""
    from cli_anything.social_trends.core import music_tracker as mt

    tracks: list = []

    if platform in ("tiktok", "all"):
        _info("Fetching TikTok trending sounds…")
        try:
            tracks += mt.fetch_tiktok_music(region=region, niche=niche, limit=limit)
        except Exception as exc:
            _err(f"TikTok music: {exc}")

    if platform in ("youtube", "all"):
        _info("Fetching YouTube trending music…")
        try:
            tracks += mt.fetch_youtube_music_charts(region=region, limit=limit, api_key=api_key)
        except Exception as exc:
            _err(f"YouTube music: {exc}")

    if platform == "all" and tracks:
        yt = [t for t in tracks if t.platform == "youtube"]
        tt = [t for t in tracks if t.platform == "tiktok"]
        tracks = mt.merge_tracks(tt, yt)

    if not tracks:
        _err("No tracks returned.")
        sys.exit(1)

    if _json_mode:
        _out([t.to_dict() for t in tracks])
        return

    headers = ["#", "Track", "Artist", "Platform", "Uses/Views", "Score", "Virality"]
    rows = [
        [
            t.rank,
            t.title[:40] + ("…" if len(t.title) > 40 else ""),
            t.artist[:25],
            t.platform,
            f"{t.clip_count:,}",
            f"{t.trend_score:.1f}",
            t.virality_label,
        ]
        for t in tracks[:limit]
    ]
    _table(headers, rows)

    if tracks:
        genres = mt.identify_trending_genres(tracks)
        if genres:
            click.echo(click.style("\n  Trending Genres:", bold=True))
            for genre, count in genres.items():
                bar = "█" * count
                click.echo(f"  {genre:<20} {bar} ({count})")


@music.command("search")
@click.argument("title")
@click.argument("artist", required=False, default="")
def music_search(title: str, artist: str) -> None:
    """Look up a specific song's TikTok virality stats."""
    from cli_anything.social_trends.core.music_tracker import search_track_virality

    _info(f"Searching TikTok for '{title}' by '{artist}'…")
    result = search_track_virality(title=title, artist=artist)

    if _json_mode:
        _out(result)
        return

    if not result.get("found"):
        click.echo(click.style(f"  No results found for '{title}'.", fg="yellow"))
        if result.get("error"):
            _err(result["error"])
        return

    click.echo(click.style(f"\n  TikTok Virality — '{title}':", bold=True))
    for r in result.get("results", []):
        click.echo(f"\n  {r['title']} — {r['artist']}")
        click.echo(f"    Uses: {r['clip_count']:,}   Score: {r['trend_score']:.1f}")
        click.echo(f"    URL:  {r['url']}")


# ── account ───────────────────────────────────────────────────────────────────

@main.group()
def account() -> None:
    """Optimise your social media accounts."""


@account.command("optimize")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "all"]))
@click.option("--niche", "-n", required=True, help="Your content niche")
def account_optimize(platform: str, niche: str) -> None:
    """Generate a full account optimisation checklist ranked by priority."""
    from cli_anything.social_trends.core.account_optimizer import build_checklist

    items = build_checklist(platform=platform, niche=niche)

    if _json_mode:
        _out([i.to_dict() for i in items])
        return

    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    priority_colors = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "white"}

    for priority in ["critical", "high", "medium", "low"]:
        group = [i for i in items if i.priority == priority]
        if not group:
            continue
        color = priority_colors[priority]
        click.echo(click.style(f"\n  [{priority.upper()}] Priority", fg=color, bold=True))
        for item in group:
            category = click.style(f"[{item.category}]", fg="white", dim=True)
            click.echo(f"  □  {category} {item.action}")
            click.echo(f"       → {click.style(item.impact, fg='green', dim=True)}")


@account.command("schedule")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
def account_schedule(platform: str) -> None:
    """Show the optimal posting schedule for maximum reach."""
    from cli_anything.social_trends.core.account_optimizer import get_posting_schedule

    slots = get_posting_schedule(platform)

    if _json_mode:
        _out([s.to_dict() for s in slots])
        return

    click.echo(click.style(f"\n  Optimal Posting Schedule — {platform.title()}", bold=True))
    click.echo(click.style("  Sorted by estimated engagement score (10 = best):", dim=True))
    click.echo()

    headers = ["Day", "UTC", "Local (EST/PST)", "Engagement Score"]
    rows = [[s.day, s.time_utc, s.local_note, f"{s.engagement_score}/10"] for s in slots]
    _table(headers, rows)

    click.echo()
    click.echo(click.style("  TIP:", bold=True) + " Adjust times by your audience's primary timezone.")
    click.echo("  Check Analytics > Followers > Most Active Time for your specific account.")


@account.command("bio")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--niche", "-n", required=True, help="Your content niche")
@click.option("--handle", "-H", default="", help="Your @handle (optional)")
def account_bio(platform: str, niche: str, handle: str) -> None:
    """Generate optimised bio templates for your niche."""
    from cli_anything.social_trends.core.account_optimizer import generate_bio

    result = generate_bio(platform=platform, niche=niche, handle=handle)

    if _json_mode:
        _out(result)
        return

    click.echo(click.style(f"\n  Bio Templates — {platform.title()} · {niche.title()}", bold=True))
    click.echo()
    for i, template in enumerate(result["templates"], 1):
        click.echo(click.style(f"  Option {i}:", bold=True))
        for line in template.split("\n"):
            click.echo(f"    {line}")
        click.echo()

    click.echo(click.style("  Best Practices:", bold=True))
    for tip in result["tips"]:
        click.echo(f"  • {tip}")


# ── theme-page ────────────────────────────────────────────────────────────────

@main.group("theme-page")
def theme_page() -> None:
    """Build and monetise converting theme pages."""


@theme_page.command("niches")
@click.option("--sort-by", default="monetisation_score", show_default=True,
              type=click.Choice(["monetisation_score", "avg_cpm_usd", "name"]))
def theme_page_niches(sort_by: str) -> None:
    """Rank the most profitable theme page niches."""
    from cli_anything.social_trends.core.theme_page import rank_niches

    niches = rank_niches(sort_by=sort_by)

    if _json_mode:
        _out([n.to_dict() for n in niches])
        return

    click.echo(click.style("\n  Top Theme Page Niches (ranked by monetisation potential)", bold=True))
    headers = ["Niche", "Score/100", "Growth", "Competition", "CPM $", "Affiliate", "Shoutout Range"]
    rows = [
        [
            n.name,
            f"{n.monetisation_score:.0f}",
            n.growth_speed,
            n.competition,
            f"${n.avg_cpm_usd:.2f}",
            n.affiliate_potential,
            f"${n.shoutout_rate_usd[0]}-${n.shoutout_rate_usd[1]}",
        ]
        for n in niches
    ]
    _table(headers, rows)

    click.echo()
    click.echo(click.style("  TIP:", bold=True) +
               " Score considers CPM, affiliate potential, and shoutout rates at 100k followers.")


@theme_page.command("strategy")
@click.option("--niche", "-n", required=True, help="Your chosen niche (e.g. 'Fitness / Gym')")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
def theme_page_strategy(niche: str, platform: str) -> None:
    """Display the full 6-phase theme page launch roadmap."""
    from cli_anything.social_trends.core.theme_page import get_theme_page_roadmap

    steps = get_theme_page_roadmap(niche=niche, platform=platform)

    if _json_mode:
        _out([s.to_dict() for s in steps])
        return

    click.echo(click.style(f"\n  Theme Page Roadmap — {niche} on {platform.title()}", bold=True))

    for step in steps:
        click.echo()
        click.echo(click.style(f"  Phase {step.phase}: {step.title}", fg="cyan", bold=True) +
                   click.style(f"  ({step.duration})", dim=True))
        for action in step.actions:
            click.echo(f"    □  {action}")
        click.echo(click.style(f"    KPI: {step.kpi}", fg="green", dim=True))


@theme_page.command("convert")
@click.option("--niche", "-n", required=True, help="Your content niche")
def theme_page_convert(niche: str) -> None:
    """Display the conversion funnel for turning followers into revenue."""
    from cli_anything.social_trends.core.theme_page import get_conversion_funnel

    funnel = get_conversion_funnel(niche=niche)

    if _json_mode:
        _out([f.to_dict() for f in funnel])
        return

    click.echo(click.style(f"\n  Conversion Funnel — {niche.title()} Theme Page", bold=True))

    for stage in funnel:
        click.echo()
        click.echo(click.style(f"  {stage.stage}: {stage.name}", fg="yellow", bold=True))
        click.echo(f"  {stage.description}")
        click.echo(click.style("  Tactics:", bold=True))
        for tactic in stage.tactics:
            click.echo(f"    • {tactic}")
        click.echo(click.style("  Tools: ", bold=True) + ", ".join(stage.tools))


@theme_page.command("ethics")
def theme_page_ethics() -> None:
    """Show ethical and legal guidelines for reposting content."""
    from cli_anything.social_trends.core.theme_page import get_repost_ethics_guide

    guide = get_repost_ethics_guide()

    if _json_mode:
        _out(guide)
        return

    click.echo(click.style("\n  Content Reposting — Ethics & Legal Guidelines", bold=True))
    for i, rule in enumerate(guide, 1):
        click.echo()
        click.echo(click.style(f"  {i}. {rule['rule']}", bold=True))
        click.echo(f"     HOW: {rule['how']}")
        click.echo(click.style(f"     WHY: {rule['why']}", fg="green", dim=True))


# ── REPL ──────────────────────────────────────────────────────────────────────

@main.command()
def repl() -> None:
    """Start the interactive Social Trends REPL."""
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.styles import Style
    except ImportError:
        click.echo("Install prompt-toolkit: pip install prompt-toolkit", err=True)
        sys.exit(1)

    skin = ReplSkin("social_trends", version="1.0.0")
    skin.print_banner()

    history_file = os.path.expanduser("~/.social_trends_history")
    session: PromptSession = PromptSession(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
    )

    HELP_TEXT = """
  Available commands (type any cli-anything-social-trends command without the prefix):

  trends fetch youtube --region US --category music
  trends fetch tiktok --niche fitness --limit 20
  trends report --region US
  hashtags analyze --platform tiktok --niche gym
  hashtags suggest --niche travel --platform tiktok
  music trending --platform all
  music search "Flowers" "Miley Cyrus"
  account optimize --platform tiktok --niche finance
  account schedule --platform tiktok
  account bio --platform tiktok --niche fitness
  theme-page niches
  theme-page strategy --niche "Fitness / Gym"
  theme-page convert --niche finance
  theme-page ethics
  help  — show this menu
  exit  — quit
"""

    click.echo(HELP_TEXT)

    while True:
        try:
            raw = session.prompt(skin.prompt()).strip()
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not raw:
            continue
        if raw.lower() in ("exit", "quit", "q"):
            skin.print_goodbye()
            break
        if raw.lower() in ("help", "h", "?"):
            click.echo(HELP_TEXT)
            continue

        args = raw.split()
        try:
            main.main(args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as exc:
            skin.error(str(exc))


if __name__ == "__main__":
    main()
