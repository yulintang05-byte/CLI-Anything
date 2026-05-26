#!/usr/bin/env python3
"""Social Trends CLI — scrape viral trends, hashtags, and music from YouTube & TikTok.

Commands:
    trends fetch    -- Fetch trending videos from one or both platforms
    trends hashtags -- Get ranked trending hashtags
    trends music    -- Get trending sounds/music
    trends analyze  -- Cross-platform virality analysis + content calendar
    account optimize -- Per-platform account optimization report
    account theme-guide -- Full theme page conversion playbook (print to terminal)
    config set-key  -- Store API keys for YouTube / TikTok

Environment variables:
    YOUTUBE_API_KEY     -- YouTube Data API v3 key (enables richer data)
    TIKTOK_SESSION_ID   -- TikTok browser sessionid cookie (improves scraping)
    TIKTOK_CLIENT_KEY   -- TikTok Research API client key
    TIKTOK_CLIENT_SECRET -- TikTok Research API client secret
"""

import os
import sys
import json
import click

from cli_anything.social_trends.scrapers import (
    yt_videos, yt_hashtags, yt_music,
    tt_videos, tt_hashtags, tt_sounds,
)
from cli_anything.social_trends.analyzers import (
    rank_trends, extract_all_hashtags, find_crossover_trends, generate_content_calendar,
)
from cli_anything.social_trends.optimizer import (
    get_full_optimization_report, get_optimization_checklist,
)
from cli_anything.social_trends.theme_page_guide import THEME_PAGE_GUIDE

_json_mode = False


def _out(data, message: str = ""):
    if _json_mode:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data, indent: int = 0):
    pad = "  " * indent
    if isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, dict):
                click.echo(f"{pad}[{i + 1}]")
                _pretty(item, indent + 1)
            else:
                click.echo(f"{pad}  {item}")
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{k}:")
                _pretty(v, indent + 1)
            else:
                click.echo(f"{pad}{k}: {v}")
    else:
        click.echo(f"{pad}{data}")


def _error(msg: str):
    click.echo(f"ERROR: {msg}", err=True)
    sys.exit(1)


# ─── Root group ──────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "use_json", is_flag=True, help="Output raw JSON")
def main(use_json: bool):
    """Social Trends CLI — viral trend intelligence for YouTube & TikTok."""
    global _json_mode
    _json_mode = use_json


# ─── trends group ─────────────────────────────────────────────────────────────

@main.group()
def trends():
    """Fetch and analyze viral trends."""


@trends.command("fetch")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              help="Which platform to pull from")
@click.option("--limit", "-n", default=20, show_default=True, help="Number of results")
@click.option("--region", default="US", show_default=True, help="Region code (YouTube only)")
def trends_fetch(platform: str, limit: int, region: str):
    """Fetch currently trending videos."""
    results = {}
    p = platform.lower()
    if p in ("youtube", "all"):
        click.echo("Fetching YouTube trending...", err=True)
        try:
            results["youtube"] = yt_videos(limit=limit, region=region)
        except Exception as e:
            results["youtube_error"] = str(e)
    if p in ("tiktok", "all"):
        click.echo("Fetching TikTok trending...", err=True)
        try:
            results["tiktok"] = tt_videos(limit=limit)
        except Exception as e:
            results["tiktok_error"] = str(e)
    _out(results, f"\n=== Trending Videos ({platform.upper()}) ===")


@trends.command("hashtags")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False))
@click.option("--limit", "-n", default=30, show_default=True)
@click.option("--crossover-only", is_flag=True, help="Show only hashtags on both platforms")
def trends_hashtags(platform: str, limit: int, crossover_only: bool):
    """Get ranked trending hashtags."""
    p = platform.lower()
    yt_v, tt_v = [], []

    if p in ("youtube", "all"):
        click.echo("Fetching YouTube hashtags...", err=True)
        try:
            yt_v = yt_videos(limit=50)
        except Exception as e:
            click.echo(f"  YouTube: {e}", err=True)

    if p in ("tiktok", "all"):
        click.echo("Fetching TikTok hashtags...", err=True)
        try:
            tt_v = tt_videos(limit=50)
            tt_ht = tt_hashtags(limit=limit)
            # Merge TikTok dedicated hashtag data into tt_v
            for ht in tt_ht:
                if not any(ht["hashtag"] in v.get("hashtags", []) for v in tt_v):
                    tt_v.append({
                        "platform": "tiktok",
                        "hashtags": [ht["hashtag"].lstrip("#")],
                        "plays": ht.get("view_count", 0),
                        "post_count": ht.get("post_count", 0),
                    })
        except Exception as e:
            click.echo(f"  TikTok: {e}", err=True)

    if p == "all":
        all_tags = extract_all_hashtags(yt_v, tt_v)
        if crossover_only:
            all_tags = [t for t in all_tags if t.get("crossover")]
        _out(all_tags[:limit], f"\n=== Trending Hashtags (Both Platforms) ===")
    elif p == "youtube":
        tags = yt_hashtags(limit=limit) if not yt_v else extract_all_hashtags(yt_v, [])
        _out(tags[:limit], "\n=== Trending YouTube Hashtags ===")
    else:
        tags = extract_all_hashtags([], tt_v)[:limit]
        _out(tags, "\n=== Trending TikTok Hashtags ===")


@trends.command("music")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False))
@click.option("--limit", "-n", default=20, show_default=True)
def trends_music(platform: str, limit: int):
    """Get trending music and sounds."""
    p = platform.lower()
    results = {}
    if p in ("youtube", "all"):
        click.echo("Fetching YouTube trending music...", err=True)
        try:
            results["youtube"] = yt_music(limit=limit)
        except Exception as e:
            results["youtube_error"] = str(e)
    if p in ("tiktok", "all"):
        click.echo("Fetching TikTok trending sounds...", err=True)
        try:
            results["tiktok"] = tt_sounds(limit=limit)
        except Exception as e:
            results["tiktok_error"] = str(e)
    _out(results, f"\n=== Trending Music/Sounds ({platform.upper()}) ===")


@trends.command("analyze")
@click.option("--limit", "-n", default=30, show_default=True, help="Videos to analyze per platform")
@click.option("--calendar-days", default=7, show_default=True, help="Days for content calendar")
def trends_analyze(limit: int, calendar_days: int):
    """Full cross-platform virality analysis + content calendar."""
    click.echo("Running cross-platform trend analysis...", err=True)
    yt_v, tt_v = [], []
    try:
        yt_v = yt_videos(limit=limit)
    except Exception as e:
        click.echo(f"  YouTube: {e}", err=True)
    try:
        tt_v = tt_videos(limit=limit)
    except Exception as e:
        click.echo(f"  TikTok: {e}", err=True)

    all_items = rank_trends(yt_v + tt_v)
    crossover = find_crossover_trends(yt_v, tt_v)
    hashtags = extract_all_hashtags(yt_v, tt_v)[:20]
    calendar = generate_content_calendar(all_items, days=calendar_days)

    report = {
        "summary": {
            "youtube_videos_analyzed": len(yt_v),
            "tiktok_videos_analyzed": len(tt_v),
            "crossover_trends": len(crossover),
        },
        "top_crossover_hashtags": crossover[:10],
        "top_hashtags": hashtags,
        "top_videos_by_virality": [
            {k: v for k, v in item.items() if k != "description"}
            for item in all_items[:10]
        ],
        "content_calendar": calendar,
    }
    _out(report, "\n=== Cross-Platform Trend Analysis ===")


# ─── account group ────────────────────────────────────────────────────────────

@main.group()
def account():
    """Account optimization tools."""


@account.command("optimize")
@click.option("--platform", "-p", default="all",
              type=click.Choice(["tiktok", "youtube", "instagram", "all"], case_sensitive=False))
@click.option("--niche", default="content creator", show_default=True,
              help="Your content niche (e.g. 'fitness', 'cooking', 'gaming')")
def account_optimize(platform: str, niche: str):
    """Generate a full account optimization report."""
    platforms = ["tiktok", "youtube", "instagram"] if platform == "all" else [platform.lower()]
    for p in platforms:
        click.echo(f"\nFetching trends for {p.upper()} optimization...", err=True)
        try:
            if p == "tiktok":
                trends_data = tt_hashtags(limit=20)
            elif p == "youtube":
                trends_data = yt_hashtags(limit=20)
            else:
                trends_data = []
        except Exception:
            trends_data = []
        report = get_full_optimization_report(p, niche=niche, trends=trends_data)
        _out(report, f"\n{'='*60}\n=== {p.upper()} ACCOUNT OPTIMIZATION REPORT ===\n{'='*60}")


@account.command("theme-guide")
@click.option("--format", "fmt", default="terminal",
              type=click.Choice(["terminal", "json", "markdown"]),
              help="Output format")
def account_theme_guide(fmt: str):
    """Print the complete theme page conversion playbook."""
    if fmt == "json":
        click.echo(json.dumps({"guide": THEME_PAGE_GUIDE}, indent=2))
    elif fmt == "markdown":
        md = "# Theme Page Conversion Playbook\n\n"
        for section, content in THEME_PAGE_GUIDE.items():
            md += f"## {section}\n\n"
            if isinstance(content, list):
                for item in content:
                    md += f"- {item}\n"
            elif isinstance(content, dict):
                for k, v in content.items():
                    md += f"### {k}\n"
                    if isinstance(v, list):
                        for item in v:
                            md += f"- {item}\n"
                    else:
                        md += f"{v}\n"
            md += "\n"
        click.echo(md)
    else:
        _pretty_guide(THEME_PAGE_GUIDE)


def _pretty_guide(guide: dict):
    width = 70
    click.echo("\n" + "=" * width)
    click.echo(" THEME PAGE CONVERSION PLAYBOOK ".center(width))
    click.echo("=" * width)
    for section, content in guide.items():
        click.echo(f"\n{'─'*width}")
        click.echo(f"  {section.upper()}")
        click.echo(f"{'─'*width}")
        if isinstance(content, list):
            for item in content:
                wrapped = _wrap(item, width - 6)
                lines = wrapped.split("\n")
                click.echo(f"  • {lines[0]}")
                for line in lines[1:]:
                    click.echo(f"    {line}")
        elif isinstance(content, dict):
            for k, v in content.items():
                click.echo(f"\n  [{k}]")
                if isinstance(v, list):
                    for item in v:
                        wrapped = _wrap(item, width - 8)
                        lines = wrapped.split("\n")
                        click.echo(f"    • {lines[0]}")
                        for line in lines[1:]:
                            click.echo(f"      {line}")
                elif isinstance(v, dict):
                    for kk, vv in v.items():
                        click.echo(f"    {kk}: {vv}")
                else:
                    click.echo(f"    {v}")
    click.echo("\n" + "=" * width + "\n")


def _wrap(text: str, width: int) -> str:
    words = text.split()
    lines, line = [], []
    length = 0
    for w in words:
        if length + len(w) + 1 > width:
            lines.append(" ".join(line))
            line, length = [w], len(w)
        else:
            line.append(w)
            length += len(w) + 1
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines)


# ─── config group ─────────────────────────────────────────────────────────────

@main.group()
def config():
    """Configure API keys and settings."""


@config.command("set-key")
@click.option("--platform", "-p", required=True,
              type=click.Choice(["youtube", "tiktok"], case_sensitive=False))
@click.option("--key", required=True, help="API key value")
def config_set_key(platform: str, key: str):
    """Store an API key (writes to .env in current directory)."""
    env_vars = {
        "youtube": "YOUTUBE_API_KEY",
        "tiktok": "TIKTOK_SESSION_ID",
    }
    var = env_vars[platform.lower()]
    env_file = os.path.join(os.getcwd(), ".env")
    lines = []
    if os.path.exists(env_file):
        with open(env_file) as f:
            lines = [l for l in f.readlines() if not l.startswith(f"{var}=")]
    lines.append(f"{var}={key}\n")
    with open(env_file, "w") as f:
        f.writelines(lines)
    click.echo(f"Set {var} in {env_file}")
    click.echo(f"Run: export {var}={key}  (or source .env)")


@config.command("show")
def config_show():
    """Show current API key configuration status."""
    keys = {
        "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY"),
        "TIKTOK_SESSION_ID": os.environ.get("TIKTOK_SESSION_ID"),
        "TIKTOK_CLIENT_KEY": os.environ.get("TIKTOK_CLIENT_KEY"),
        "TIKTOK_CLIENT_SECRET": os.environ.get("TIKTOK_CLIENT_SECRET"),
    }
    for k, v in keys.items():
        status = f"[SET - {v[:6]}...]" if v else "[NOT SET]"
        click.echo(f"  {k}: {status}")


if __name__ == "__main__":
    main()
