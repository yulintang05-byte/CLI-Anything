"""viral-trends — agent-native CLI for viral trend intelligence."""
import json
import sys
import click

from . import youtube_scraper as yt
from . import tiktok_scraper as tt
from . import analyzer
from . import optimizer
from . import theme_pages as tp


def _out(data, fmt: str = "json") -> None:
    if fmt == "json":
        click.echo(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        if isinstance(data, list):
            for item in data:
                click.echo(json.dumps(item, ensure_ascii=False))
        else:
            click.echo(json.dumps(data, ensure_ascii=False))


def _err(msg: str) -> None:
    click.echo(json.dumps({"error": msg}), err=True)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
@click.group()
@click.version_option("1.0.0", prog_name="viral-trends")
def main():
    """viral-trends: scrape YouTube & TikTok trends, optimize accounts, and learn theme pages."""


# ---------------------------------------------------------------------------
# `trending` group
# ---------------------------------------------------------------------------
@main.group()
def trending():
    """Fetch trending content from YouTube or TikTok."""


@trending.command("youtube")
@click.option("--category", "-c",
              type=click.Choice(["general", "music", "gaming", "films"]),
              default="general", show_default=True,
              help="Trending category.")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of videos to fetch.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def trending_youtube(category, limit, fmt):
    """Fetch YouTube trending videos."""
    try:
        results = yt.fetch_trending(category=category, limit=limit)
        _out(results, fmt)
    except RuntimeError as exc:
        _err(str(exc))


@trending.command("tiktok")
@click.option("--hashtag", "-h", required=True, help="TikTok hashtag to explore (without #).")
@click.option("--limit", "-n", default=10, show_default=True, help="Number of videos to fetch.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def trending_tiktok(hashtag, limit, fmt):
    """Fetch top TikTok videos for a hashtag."""
    try:
        results = tt.fetch_hashtag_videos(hashtag, limit=limit)
        _out(results, fmt)
    except RuntimeError as exc:
        _err(str(exc))


# ---------------------------------------------------------------------------
# `hashtags` group
# ---------------------------------------------------------------------------
@main.group()
def hashtags():
    """Extract and rank trending hashtags."""


@hashtags.command("youtube")
@click.option("--category", "-c",
              type=click.Choice(["general", "music", "gaming", "films"]),
              default="general", show_default=True)
@click.option("--limit", "-n", default=20, show_default=True, help="Videos to sample.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def hashtags_youtube(category, limit, fmt):
    """Top hashtags from YouTube trending."""
    try:
        results = yt.top_hashtags_from_trending(category=category, limit=limit)
        _out(results, fmt)
    except RuntimeError as exc:
        _err(str(exc))


@hashtags.command("tiktok")
@click.option("--hashtag", "-h", required=True, help="Seed hashtag to sample (without #).")
@click.option("--limit", "-n", default=10, show_default=True, help="Videos to sample.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def hashtags_tiktok(hashtag, limit, fmt):
    """Top hashtags from TikTok videos under a seed hashtag."""
    try:
        videos = tt.fetch_hashtag_videos(hashtag, limit=limit)
        results = tt.aggregate_hashtags(videos)
        _out(results, fmt)
    except RuntimeError as exc:
        _err(str(exc))


@hashtags.command("cross-platform")
@click.option("--yt-category", default="general", show_default=True,
              type=click.Choice(["general", "music", "gaming", "films"]))
@click.option("--tt-hashtag", "-h", required=True, help="TikTok seed hashtag (without #).")
@click.option("--limit", "-n", default=20, show_default=True, help="Videos to sample per platform.")
@click.option("--top", default=15, show_default=True, help="Top N results to return.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def hashtags_cross(yt_category, tt_hashtag, limit, top, fmt):
    """Merge YouTube + TikTok hashtags into a unified virality ranking."""
    try:
        yt_tags = yt.top_hashtags_from_trending(category=yt_category, limit=limit)
        tt_videos = tt.fetch_hashtag_videos(tt_hashtag, limit=limit)
        tt_tags = tt.aggregate_hashtags(tt_videos)
        results = analyzer.cross_platform_hashtags(yt_tags, tt_tags, top_n=top)
        _out(results, fmt)
    except RuntimeError as exc:
        _err(str(exc))


# ---------------------------------------------------------------------------
# `music` group
# ---------------------------------------------------------------------------
@main.group()
def music():
    """Discover trending sounds and music."""


@music.command("tiktok")
@click.option("--hashtag", "-h", required=True, help="TikTok seed hashtag (without #).")
@click.option("--limit", "-n", default=20, show_default=True, help="Videos to sample.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def music_tiktok(hashtag, limit, fmt):
    """Rank trending sounds/music from TikTok videos."""
    try:
        videos = tt.fetch_hashtag_videos(hashtag, limit=limit)
        sounds = tt.fetch_trending_sounds_from_videos(videos)
        report = analyzer.trending_music_report(sounds)
        _out(report, fmt)
    except RuntimeError as exc:
        _err(str(exc))


# ---------------------------------------------------------------------------
# `optimize` command
# ---------------------------------------------------------------------------
@main.command("optimize")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True, help="Platform to optimize for.")
@click.option("--niche", "-n", required=True, help="Your content niche (e.g. 'fitness', 'finance').")
@click.option("--tt-hashtag", default=None,
              help="TikTok seed hashtag to pull trending tags from (without #). Defaults to --niche.")
@click.option("--yt-category", default="general",
              type=click.Choice(["general", "music", "gaming", "films"]))
@click.option("--niche-tags", default="", help="Comma-separated niche/brand hashtags to include.")
@click.option("--cta", default="link in bio", show_default=True, help="Your call-to-action text.")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def optimize(platform, niche, tt_hashtag, yt_category, niche_tags, cta, fmt):
    """Run a full account optimization audit for a platform + niche."""
    seed = tt_hashtag or niche.replace(" ", "")
    niche_tag_list = [t.strip() for t in niche_tags.split(",") if t.strip()]
    try:
        yt_tags = yt.top_hashtags_from_trending(category=yt_category, limit=20)
        tt_videos = tt.fetch_hashtag_videos(seed, limit=15)
        tt_tags = tt.aggregate_hashtags(tt_videos)
        trending_tags = analyzer.cross_platform_hashtags(yt_tags, tt_tags, top_n=20)
        report = optimizer.full_account_audit(
            platform=platform,
            niche=niche,
            trending_tags=trending_tags,
            niche_tags=niche_tag_list,
            cta=cta,
        )
        _out(report, fmt)
    except RuntimeError as exc:
        _err(str(exc))


# ---------------------------------------------------------------------------
# `theme-pages` group
# ---------------------------------------------------------------------------
@main.group("theme-pages")
def theme_pages():
    """Learn how to build and monetize converting theme pages."""


@theme_pages.command("guide")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def theme_guide(fmt):
    """Print the full theme page creation and monetization guide."""
    _out(tp.get_guide(), fmt)


@theme_pages.command("step")
@click.argument("number", type=int)
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def theme_step(number, fmt):
    """Print a specific step (1-7) from the theme page guide."""
    try:
        _out(tp.get_step(number), fmt)
    except ValueError as exc:
        _err(str(exc))


@theme_pages.command("monetize")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def theme_monetize(fmt):
    """Print the monetization phase timeline."""
    _out(tp.get_monetization_timeline(), fmt)


@theme_pages.command("content-pillars")
@click.argument("niche")
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def theme_content_pillars(niche, fmt):
    """Get a content pillar framework for your niche."""
    _out(optimizer.content_pillars(niche), fmt)


# ---------------------------------------------------------------------------
# `niche-opps` command — proactive opportunity detection
# ---------------------------------------------------------------------------
@main.command("niche-opps")
@click.option("--tt-hashtag", "-h", required=True, help="TikTok seed hashtag (without #).")
@click.option("--yt-category", default="general",
              type=click.Choice(["general", "music", "gaming", "films"]))
@click.option("--limit", "-n", default=20, show_default=True)
@click.option("--format", "fmt", type=click.Choice(["json", "lines"]), default="json")
def niche_opps(tt_hashtag, yt_category, limit, fmt):
    """
    Find hashtags viral on TikTok but underused on YouTube — cross-posting opportunities.
    """
    try:
        yt_tags = yt.top_hashtags_from_trending(category=yt_category, limit=limit)
        tt_videos = tt.fetch_hashtag_videos(tt_hashtag, limit=limit)
        tt_tags = tt.aggregate_hashtags(tt_videos)
        opps = analyzer.niche_opportunity_tags(yt_tags, tt_tags)
        _out(opps, fmt)
    except RuntimeError as exc:
        _err(str(exc))


if __name__ == "__main__":
    main()
