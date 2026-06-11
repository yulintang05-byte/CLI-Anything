"""trends commands — fetch viral videos and music from YouTube and TikTok."""
import json
import sys
import click
from ..utils.youtube_scraper import (
    fetch_trending_videos as yt_trending,
    fetch_music_trends as yt_music,
    extract_hashtags_from_videos,
)
from ..utils.tiktok_scraper import (
    fetch_trending_videos as tt_trending,
    fetch_trending_music as tt_music,
)


def _out(data, fmt: str):
    if fmt == "json":
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        _table(data)


def _table(data):
    if not data:
        click.echo("No results.")
        return
    if isinstance(data, list) and data and isinstance(data[0], dict):
        keys = list(data[0].keys())[:6]
        widths = {k: max(len(k), max((len(str(row.get(k, ""))) for row in data), default=0))
                  for k in keys}
        header = "  ".join(k.ljust(widths[k]) for k in keys)
        click.echo(header)
        click.echo("-" * len(header))
        for row in data:
            click.echo("  ".join(str(row.get(k, "")).ljust(widths[k]) for k in keys))
    else:
        click.echo(json.dumps(data, indent=2, default=str))


@click.group()
def trends():
    """Fetch and display viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", "-r", default="US", show_default=True,
              help="ISO region code (US, GB, CA, AU…)")
@click.option("--category", "-c",
              type=click.Choice(["all", "music", "gaming", "news",
                                  "entertainment", "sports", "howto", "science"]),
              default="all", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def yt_trends_cmd(region, category, limit, fmt):
    """Fetch trending YouTube videos."""
    click.echo(f"Fetching YouTube trending ({category}) for region {region}…", err=True)
    try:
        videos = yt_trending(region=region, category=category, max_results=limit)
    except EnvironmentError as e:
        click.echo(f"[warn] {e} — using scrape mode.", err=True)
        from ..utils.youtube_scraper import fetch_trending_videos_scrape
        videos = fetch_trending_videos_scrape(region=region, category=category, max_results=limit)
    _out(videos, fmt)


@trends.command("tiktok")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=25, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def tt_trends_cmd(region, limit, fmt):
    """Fetch trending TikTok videos."""
    click.echo(f"Fetching TikTok trending for region {region}…", err=True)
    videos = tt_trending(region=region, max_results=limit)
    _out(videos, fmt)


@trends.command("music")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "both"]),
              default="both", show_default=True)
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def music_cmd(platform, region, limit, fmt):
    """Fetch trending music/audio across platforms."""
    results = []
    if platform in ("youtube", "both"):
        click.echo("Fetching YouTube music trends…", err=True)
        yt = yt_music(region=region, max_results=limit)
        for v in yt:
            v["platform"] = "youtube"
        results += yt
    if platform in ("tiktok", "both"):
        click.echo("Fetching TikTok music trends…", err=True)
        tt = tt_music(region=region, max_results=limit)
        for t in tt:
            t["platform"] = "tiktok"
        results += tt
    _out(results, fmt)


@trends.command("all")
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=15, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="json", show_default=True)
def all_trends_cmd(region, limit, fmt):
    """Fetch all trending data (videos + music + hashtags) in one call."""
    click.echo("Fetching all trends…", err=True)
    yt_vids = yt_trending(region=region, max_results=limit)
    tt_vids = tt_trending(region=region, max_results=limit)
    yt_mus  = yt_music(region=region, max_results=10)
    tt_mus  = tt_music(region=region, max_results=10)
    yt_tags = extract_hashtags_from_videos(yt_vids)[:20]

    report = {
        "region": region,
        "youtube_trending": yt_vids,
        "tiktok_trending":  tt_vids,
        "youtube_music":    yt_mus,
        "tiktok_music":     tt_mus,
        "youtube_hashtags": yt_tags,
        "summary": {
            "yt_videos":  len(yt_vids),
            "tt_videos":  len(tt_vids),
            "music_tracks": len(yt_mus) + len(tt_mus),
            "hashtags":   len(yt_tags),
        },
    }
    _out(report, fmt)
