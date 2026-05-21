"""
social — agent-native CLI for social media intelligence.

Commands:
  trends youtube       Fetch YouTube trending videos
  trends tiktok        Fetch TikTok trending hashtags
  trends music         Fetch trending music across platforms
  trends report        Full cross-platform trend report
  hashtags research    Hashtag strategy for a niche
  hashtags score       Score a single hashtag
  hashtags niches      List available niches
  accounts optimize    Full account optimization plan
  accounts audit       Account audit checklist
  theme-pages guide    Theme page creation playbook
  theme-pages niches   List top converting theme page niches
"""
import json
import sys
import click

from cli_anything.social.core.session import Session
from cli_anything.social.core import scraper, hashtags, music, accounts, theme_pages
from cli_anything.social.utils.output import emit

_session = Session()


def _out(data, fmt, cols=None):
    click.echo(emit(data, fmt, cols))


# ─── Root group ──────────────────────────────────────────────────────────────

@click.group()
@click.version_option("1.0.0", prog_name="social")
def main():
    """Social media intelligence CLI — trends, hashtags, music, account optimization."""


# ─── trends ──────────────────────────────────────────────────────────────────

@main.group()
def trends():
    """Fetch viral trends from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region",   default="US",  show_default=True, help="Two-letter country code.")
@click.option("--category", default="all", show_default=True,
              type=click.Choice(["all","music","gaming","sports","tech","entertainment","news"]),
              help="Video category.")
@click.option("--limit",    default=20,    show_default=True, type=int)
@click.option("--output",   default="table", type=click.Choice(["json","table"]), show_default=True)
@click.option("--api-key",  envvar="YOUTUBE_API_KEY", default=None, help="YouTube Data API v3 key (optional).")
def trends_youtube(region, category, limit, output, api_key):
    """Fetch trending YouTube videos. Uses Data API if YOUTUBE_API_KEY is set, else scrapes."""
    try:
        data = scraper.youtube_trending(region=region, category=category, limit=limit, api_key=api_key)
    except Exception as exc:
        click.echo(json.dumps({"error": str(exc), "hint": "Try setting YOUTUBE_API_KEY or check your internet connection."}), err=True)
        sys.exit(1)
    _out(data, output, ["rank","title","channel","views","url"])


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True)
@click.option("--period", default=7,    show_default=True, type=click.Choice(["7","30","120"]),
              help="Trend window in days: 7, 30, or 120.")
@click.option("--limit",  default=20,   show_default=True, type=int)
@click.option("--output", default="table", type=click.Choice(["json","table"]), show_default=True)
def trends_tiktok(region, period, limit, output):
    """Fetch trending TikTok hashtags from Creative Center (no auth required)."""
    try:
        data = scraper.tiktok_trending_hashtags(region=region, period=int(period), limit=limit)
    except Exception as exc:
        click.echo(json.dumps({"error": str(exc), "hint": "TikTok Creative Center may be blocking the request. Try a VPN or check network."}), err=True)
        sys.exit(1)
    _out(data, output, ["rank","hashtag","posts","views","trend","link"])


@trends.command("music")
@click.option("--platform", default="all", type=click.Choice(["all","tiktok","youtube"]), show_default=True)
@click.option("--region",   default="US",  show_default=True)
@click.option("--limit",    default=20,    show_default=True, type=int)
@click.option("--output",   default="json", type=click.Choice(["json","table"]), show_default=True)
def trends_music(platform, region, limit, output):
    """Fetch trending music/sounds on TikTok and YouTube."""
    data = music.get_trending_music(platform=platform, region=region, limit=limit)
    click.echo(emit(data, "json"))  # always JSON for nested structure


@trends.command("report")
@click.option("--region", default="US", show_default=True)
@click.option("--limit",  default=10,   show_default=True, type=int)
@click.option("--output", default="json", type=click.Choice(["json","table"]), show_default=True)
def trends_report(region, limit, output):
    """Full cross-platform viral trend report."""
    report = {"region": region, "platforms": {}}
    errors = []

    try:
        report["platforms"]["youtube"] = scraper.youtube_trending(region=region, limit=limit)
    except Exception as exc:
        errors.append(f"YouTube: {exc}")

    try:
        report["platforms"]["tiktok_hashtags"] = scraper.tiktok_trending_hashtags(region=region, limit=limit)
    except Exception as exc:
        errors.append(f"TikTok hashtags: {exc}")

    try:
        report["platforms"]["tiktok_music"] = scraper.tiktok_trending_music(region=region, limit=limit)
    except Exception as exc:
        errors.append(f"TikTok music: {exc}")

    if errors:
        report["warnings"] = errors

    click.echo(emit(report, "json"))


# ─── hashtags ────────────────────────────────────────────────────────────────

@main.group()
def hashtags_cmd():
    """Hashtag research and strategy."""


# rename the group to avoid shadowing the module
main.add_command(hashtags_cmd, name="hashtags")


@hashtags_cmd.command("research")
@click.argument("niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok","instagram","youtube","twitter"]), show_default=True)
@click.option("--include-viral/--no-viral", default=True, show_default=True)
@click.option("--limit",  default=30,  show_default=True, type=int)
@click.option("--output", default="json", type=click.Choice(["json","table"]), show_default=True)
def hashtags_research(niche, platform, include_viral, limit, output):
    """Research hashtag strategy for NICHE on PLATFORM.

    Example: social hashtags research fitness --platform tiktok
    """
    data = hashtags.research_hashtags(niche=niche, platform=platform, include_viral=include_viral, limit=limit)
    click.echo(emit(data, "json"))


@hashtags_cmd.command("score")
@click.argument("hashtag")
def hashtags_score(hashtag):
    """Score a single hashtag for strategic value."""
    data = hashtags.score_hashtag(hashtag)
    click.echo(emit(data, "json"))


@hashtags_cmd.command("niches")
@click.option("--output", default="table", type=click.Choice(["json","table"]), show_default=True)
def hashtags_niches(output):
    """List all available niche hashtag banks."""
    data = [{"niche": n} for n in hashtags.available_niches()]
    _out(data, output, ["niche"])


# ─── accounts ────────────────────────────────────────────────────────────────

@main.group()
def accounts_cmd():
    """Account optimization and audit tools."""


main.add_command(accounts_cmd, name="accounts")


@accounts_cmd.command("optimize")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok","instagram","youtube","twitter"]), show_default=True)
@click.option("--niche",  default="", help="Your content niche (e.g. fitness, finance).")
@click.option("--stage",  default="growing",
              type=click.Choice(["new_account","growing","monetized"]), show_default=True,
              help="Account growth stage.")
@click.option("--output", default="json", type=click.Choice(["json","table"]), show_default=True)
def accounts_optimize(platform, niche, stage, output):
    """Generate a full account optimization plan."""
    data = accounts.optimize_account(platform=platform, niche=niche, stage=stage)
    click.echo(emit(data, "json"))


@accounts_cmd.command("audit")
@click.argument("handle")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok","instagram","youtube","twitter"]), show_default=True)
def accounts_audit(handle, platform):
    """Run an account audit checklist for HANDLE."""
    data = accounts.audit_account(handle=handle, platform=platform)
    click.echo(emit(data, "json"))


@accounts_cmd.command("add")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok","instagram","youtube","twitter"]))
@click.option("--handle", required=True, help="Account username/handle.")
@click.option("--niche",  default="", help="Content niche.")
@click.option("--session-file", default="social_session.json", show_default=True)
def accounts_add(platform, handle, niche, session_file):
    """Track an account in the session."""
    from pathlib import Path
    sf = Path(session_file)
    if sf.exists():
        _session.load(sf)
    acct = _session.add_account(platform=platform, handle=handle, niche=niche)
    _session.save(sf)
    click.echo(emit(acct, "json"))


@accounts_cmd.command("list")
@click.option("--platform", default=None)
@click.option("--session-file", default="social_session.json", show_default=True)
def accounts_list(platform, session_file):
    """List tracked accounts."""
    from pathlib import Path
    sf = Path(session_file)
    if sf.exists():
        _session.load(sf)
    data = _session.get_accounts(platform=platform)
    click.echo(emit(data, "json"))


# ─── theme-pages ─────────────────────────────────────────────────────────────

@main.group("theme-pages")
def theme_pages_cmd():
    """Theme page creation, strategy, and monetization guides."""


@theme_pages_cmd.command("guide")
@click.option("--niche", default="", help="Filter guide to a specific niche.")
@click.option("--output", default="json", type=click.Choice(["json","table"]), show_default=True)
def theme_pages_guide(niche, output):
    """Full theme page creation and monetization playbook."""
    data = theme_pages.theme_page_guide(niche=niche)
    click.echo(emit(data, "json"))


@theme_pages_cmd.command("niches")
@click.option("--output", default="table", type=click.Choice(["json","table"]), show_default=True)
def theme_pages_niches(output):
    """List top converting theme page niches with monetization data."""
    data = theme_pages.list_niches()
    _out(data, output, ["niche","audience","avg_cpm","competition","difficulty"])
