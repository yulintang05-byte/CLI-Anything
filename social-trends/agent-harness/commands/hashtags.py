"""hashtags commands — analyze, score, and generate optimal hashtag sets."""
import json
import click
from ..utils.hashtag_analyzer import (
    score_hashtags,
    build_hashtag_set,
    cross_platform_merge,
    recommend_for_niche,
    analyze_description,
    NICHE_HASHTAGS,
)
from ..utils.youtube_scraper import fetch_trending_videos as yt_vids, extract_hashtags_from_videos
from ..utils.tiktok_scraper import fetch_trending_hashtags as tt_hashtags


def _out(data, fmt):
    if fmt == "json":
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if isinstance(data, list):
            if data and isinstance(data[0], dict):
                keys = list(data[0].keys())[:7]
                widths = {k: max(len(k), max(len(str(r.get(k, ""))) for r in data), default=8)
                          for k in keys}
                click.echo("  ".join(k.ljust(widths[k]) for k in keys))
                click.echo("-" * sum(widths[k] + 2 for k in keys))
                for row in data:
                    click.echo("  ".join(str(row.get(k, "")).ljust(widths[k]) for k in keys))
            else:
                for item in data:
                    click.echo(f"  {item}")
        else:
            click.echo(json.dumps(data, indent=2, default=str))


@click.group()
def hashtags():
    """Analyze, score, and generate optimal hashtag sets."""


@hashtags.command("trending")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "both"]),
              default="both", show_default=True)
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--limit", "-n", default=30, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def trending_hashtags(platform, region, limit, fmt):
    """Fetch and score trending hashtags from YouTube and/or TikTok."""
    if platform in ("youtube", "both"):
        click.echo("Pulling YouTube hashtags…", err=True)
        vids = yt_vids(region=region, max_results=50)
        yt_raw = extract_hashtags_from_videos(vids)
    else:
        yt_raw = []

    if platform in ("tiktok", "both"):
        click.echo("Pulling TikTok hashtags…", err=True)
        tt_raw = tt_hashtags(region=region, count=50)
    else:
        tt_raw = []

    if platform == "both":
        merged = cross_platform_merge(yt_raw, tt_raw)
        results = [h.to_dict() for h in merged[:limit]]
    elif platform == "youtube":
        results = [h.to_dict() for h in score_hashtags(yt_raw, "youtube")[:limit]]
    else:
        results = [h.to_dict() for h in score_hashtags(tt_raw, "tiktok")[:limit]]

    _out(results, fmt)


@hashtags.command("generate")
@click.option("--niche", "-n", required=True,
              type=click.Choice(list(NICHE_HASHTAGS.keys())),
              help="Target niche for hashtag generation")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "both"]),
              default="tiktok", show_default=True)
@click.option("--count", "-c", default=30, show_default=True,
              help="Number of hashtags to generate")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["list", "caption", "json"]),
              default="caption", show_default=True)
def generate_hashtags(niche, platform, count, fmt):
    """Generate an optimized hashtag set for a niche."""
    tags = recommend_for_niche(niche, platform)[:count]
    if fmt == "json":
        click.echo(json.dumps({"niche": niche, "platform": platform, "hashtags": tags}, indent=2))
    elif fmt == "caption":
        click.echo(" ".join(tags))
    else:
        for t in tags:
            click.echo(t)


@hashtags.command("analyze")
@click.argument("text")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def analyze_text(text, fmt):
    """Analyze hashtags in a caption/description text."""
    result = analyze_description(text)
    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
        return
    click.echo(f"Found {result['count']} hashtags | Avg score: {result['avg_score']}")
    if result["strong_tags"]:
        click.echo(f"  Strong tags:   {' '.join(result['strong_tags'])}")
    if result["weak_tags"]:
        click.echo(f"  Weak tags:     {' '.join(result['weak_tags'])}")
    if result["mega_tags"]:
        click.echo(f"  Mega tags:     {' '.join(result['mega_tags'])} (consider replacing)")
    if result["suggestions"]:
        click.echo(f"  Suggestion:    {result['suggestions']}")


@hashtags.command("build-set")
@click.option("--platform", "-p",
              type=click.Choice(["youtube", "tiktok", "both"]),
              default="both", show_default=True)
@click.option("--niche", "-n",
              type=click.Choice(list(NICHE_HASHTAGS.keys())),
              default=None)
@click.option("--region", "-r", default="US", show_default=True)
@click.option("--count", "-c", default=30, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["caption", "list", "json"]),
              default="caption", show_default=True)
def build_set_cmd(platform, niche, region, count, fmt):
    """Build an optimal hashtag set combining trending data + niche tags."""
    click.echo("Building optimal hashtag set…", err=True)

    yt_raw, tt_raw = [], []
    if platform in ("youtube", "both"):
        vids = yt_vids(region=region, max_results=50)
        yt_raw = extract_hashtags_from_videos(vids)
    if platform in ("tiktok", "both"):
        tt_raw = tt_hashtags(region=region, count=50)

    if platform == "both":
        scored = cross_platform_merge(yt_raw, tt_raw)
    elif platform == "youtube":
        scored = score_hashtags(yt_raw, "youtube")
    else:
        scored = score_hashtags(tt_raw, "tiktok")

    result_tags = build_hashtag_set(scored, target_count=count, niche=niche)

    # Supplement with niche-specific if provided
    if niche:
        niche_tags = recommend_for_niche(niche, platform)
        combined = list(dict.fromkeys(result_tags + niche_tags))[:count]
    else:
        combined = result_tags

    if fmt == "json":
        click.echo(json.dumps({"hashtags": combined, "count": len(combined)}, indent=2))
    elif fmt == "caption":
        click.echo(" ".join(combined))
    else:
        for t in combined:
            click.echo(t)
