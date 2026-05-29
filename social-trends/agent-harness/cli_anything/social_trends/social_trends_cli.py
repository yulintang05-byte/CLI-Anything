"""Social Trends CLI — agent-native social media trend & growth tool.

Scrapes YouTube & TikTok for viral trends, hashtags, and music.
Optimizes social media accounts and provides theme-page strategy.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Any, Optional

from cli_anything.social_trends.core.store import Store
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod
from cli_anything.social_trends.core import scheduler as sched_mod

# ── Global state ──────────────────────────────────────────────────────────────

_store: Optional[Store] = None
_json_output: bool = False
_repl_mode: bool = False


def get_store() -> Store:
    global _store
    if _store is None:
        _store = Store()
    return _store


# ── Output helpers ────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)


def _print_dict(d: dict, indent: int = 2) -> None:
    pad = " " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{pad}{k}:")
            _print_dict(v, indent + 2)
        elif isinstance(v, list):
            if v and isinstance(v[0], str):
                click.echo(f"{pad}{k}:")
                for item in v:
                    click.echo(f"{pad}  - {item}")
            else:
                click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst:
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if not isinstance(v, (dict, list)):
                    parts.append(f"{k}={v}")
            click.echo("  " + "  ".join(parts))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


# ── Error handling decorator ──────────────────────────────────────────────────

def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, FileNotFoundError, RuntimeError) as e:
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
@click.version_option("1.0.0", prog_name="social-trends")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """Social Trends — agent-native viral trend & growth tool.

    Scrape YouTube & TikTok trends, research hashtags, track music,
    optimize social accounts, and build theme page strategies.

    \b
    Quick start:
      social-trends trends fetch --platform both --limit 10
      social-trends hashtags research fitness --platform tiktok
      social-trends accounts add --platform tiktok --username mypage --niche fitness
      social-trends theme-pages guide --niche finance
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Viral trend scraping from YouTube and TikTok."""
    pass


@trends.command("fetch")
@click.option("--platform", default="both", show_default=True,
              type=click.Choice(["youtube", "tiktok", "both"]),
              help="Platform to fetch from")
@click.option("--category", default=None, help="Filter by category (fitness, finance, gaming, etc.)")
@click.option("--limit", default=10, show_default=True, help="Max results per platform")
@handle_error
def trends_fetch(platform: str, category: Optional[str], limit: int) -> None:
    """Fetch viral trends from YouTube and/or TikTok."""
    store = get_store()
    if not _json_output:
        click.echo(f"Fetching trends from {platform}...")
    results = trends_mod.fetch_trends(store, platform=platform, category=category, limit=limit)
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.success(f"Fetched {len(results)} trends")
        skin.table(
            ["#", "Platform", "Title", "Views", "Category", "Source"],
            [[t.get("rank",""), t.get("platform",""), t.get("title","")[:40],
              t.get("views",""), t.get("category",""), t.get("source","")] for t in results]
        )


@trends.command("list")
@handle_error
def trends_list() -> None:
    """List cached trends from last fetch."""
    store = get_store()
    results = trends_mod.list_trends(store)
    if not results:
        click.echo("  No cached trends. Run 'trends fetch' first.")
        return
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Platform", "Title", "Views", "Category"],
            [[t.get("rank",""), t.get("platform",""), t.get("title","")[:40],
              t.get("views",""), t.get("category","")] for t in results]
        )


@trends.command("search")
@click.argument("keyword")
@click.option("--platform", default=None, help="Filter by platform")
@handle_error
def trends_search(keyword: str, platform: Optional[str]) -> None:
    """Search cached trends by keyword."""
    store = get_store()
    results = trends_mod.search_trends(store, keyword, platform)
    if not results:
        click.echo(f"  No trends matching '{keyword}'.")
        return
    output(results, f"Found {len(results)} trends matching '{keyword}':")


@trends.command("export")
@click.option("-o", "--output", "output_path", required=True, help="Output JSON file path")
@handle_error
def trends_export(output_path: str) -> None:
    """Export cached trends to a JSON file."""
    store = get_store()
    result = trends_mod.export_trends(store, output_path)
    output(result, f"Exported {result['count']} trends to {output_path}")


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag research, ranking, and suggestion engine."""
    pass


@hashtags.command("research")
@click.argument("niche")
@click.option("--platform", default="both", show_default=True, help="Target platform")
@click.option("--limit", default=12, show_default=True, help="Max hashtags to return")
@handle_error
def hashtags_research(niche: str, platform: str, limit: int) -> None:
    """Research top hashtags for a niche."""
    store = get_store()
    results = hashtags_mod.research_hashtags(store, niche, platform, limit)
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.success(f"Found {len(results)} hashtags for '{niche}'")
        skin.table(
            ["Tag", "Posts", "Avg Views", "Competition", "Engagement %"],
            [[h["tag"], h["posts"], h["avg_views"], h["competition"], str(h["engagement_rate"])]
             for h in results]
        )


@hashtags.command("rank")
@click.option("--by", default="engagement", show_default=True,
              type=click.Choice(["views", "posts", "engagement"]),
              help="Ranking metric")
@handle_error
def hashtags_rank(by: str) -> None:
    """Rank cached hashtags by a metric."""
    store = get_store()
    results = hashtags_mod.rank_hashtags(store, by)
    if not results:
        click.echo("  No hashtags cached. Run 'hashtags research' first.")
        return
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Tag", "Posts", "Avg Views", "Competition", "Engagement %"],
            [[h["tag"], h["posts"], h["avg_views"], h["competition"], str(h["engagement_rate"])]
             for h in results]
        )


@hashtags.command("suggest")
@click.option("--niche", required=True, help="Target niche")
@click.option("--count", default=30, show_default=True, help="Total hashtags to suggest")
@handle_error
def hashtags_suggest(niche: str, count: int) -> None:
    """Suggest an optimal hashtag mix (high/medium/low competition)."""
    store = get_store()
    result = hashtags_mod.suggest_hashtags(store, niche, count)
    output(result, f"Hashtag mix for '{niche}' ({count} total):")


@hashtags.command("export")
@click.option("-o", "--output", "output_path", required=True, help="Output JSON file path")
@handle_error
def hashtags_export(output_path: str) -> None:
    """Export hashtag sets to a JSON file."""
    store = get_store()
    result = hashtags_mod.export_hashtags(store, output_path)
    output(result, f"Exported {result['count']} hashtags to {output_path}")


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Trending audio and music tracker."""
    pass


@music.command("trending")
@click.option("--platform", default="both", show_default=True,
              type=click.Choice(["tiktok", "youtube", "both"]),
              help="Platform to fetch from")
@click.option("--genre", default=None, help="Filter by genre (pop, hiphop, rock, etc.)")
@click.option("--limit", default=10, show_default=True, help="Max results per platform")
@handle_error
def music_trending(platform: str, genre: Optional[str], limit: int) -> None:
    """Fetch trending audio and music."""
    store = get_store()
    results = music_mod.fetch_music(store, platform=platform, genre=genre, limit=limit)
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.success(f"Found {len(results)} trending tracks")
        skin.table(
            ["#", "Platform", "Title", "Artist", "Genre", "Uses/Views"],
            [[m.get("rank",""), m.get("platform",""), m.get("title","")[:30],
              m.get("artist","")[:20], m.get("genre",""),
              m.get("uses", m.get("views",""))] for m in results]
        )


@music.command("list")
@handle_error
def music_list() -> None:
    """List cached trending music."""
    store = get_store()
    results = music_mod.list_music(store)
    if not results:
        click.echo("  No cached music. Run 'music trending' first.")
        return
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["#", "Platform", "Title", "Artist", "Genre"],
            [[m.get("rank",""), m.get("platform",""), m.get("title","")[:30],
              m.get("artist","")[:20], m.get("genre","")] for m in results]
        )


@music.command("search")
@click.argument("query")
@handle_error
def music_search(query: str) -> None:
    """Search cached music by title or artist."""
    store = get_store()
    results = music_mod.search_music(store, query)
    if not results:
        click.echo(f"  No music matching '{query}'.")
        return
    output(results, f"Found {len(results)} tracks matching '{query}':")


@music.command("export")
@click.option("-o", "--output", "output_path", required=True, help="Output JSON file path")
@handle_error
def music_export(output_path: str) -> None:
    """Export trending music list to a JSON file."""
    store = get_store()
    result = music_mod.export_music(store, output_path)
    output(result, f"Exported {result['count']} tracks to {output_path}")


# ── accounts group ────────────────────────────────────────────────────────────

@cli.group()
def accounts():
    """Social media account profile management and optimization."""
    pass


@accounts.command("add")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              help="Social platform")
@click.option("--username", required=True, help="Account username or handle")
@click.option("--niche", required=True, help="Account niche (fitness, finance, etc.)")
@handle_error
def accounts_add(platform: str, username: str, niche: str) -> None:
    """Register a social media account profile."""
    store = get_store()
    result = accounts_mod.add_account(store, platform, username, niche)
    output(result, f"Added account '{username}' on {platform} (ID: {result['id']})")


@accounts.command("list")
@handle_error
def accounts_list() -> None:
    """List all registered accounts."""
    store = get_store()
    results = accounts_mod.list_accounts(store)
    if not results:
        click.echo("  No accounts. Use 'accounts add' to register one.")
        return
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Platform", "Username", "Niche", "Opt. Score"],
            [[a["id"], a["platform"], a["username"], a["niche"],
              str(a.get("optimization_score", 0))] for a in results]
        )


@accounts.command("optimize")
@click.argument("account_id")
@handle_error
def accounts_optimize(account_id: str) -> None:
    """Generate a full optimization report for an account."""
    store = get_store()
    result = accounts_mod.optimize_account(store, account_id)
    output(result, f"Optimization report for {result['username']} ({result['platform']}):")


@accounts.command("score")
@click.argument("account_id")
@handle_error
def accounts_score(account_id: str) -> None:
    """Score an account's optimization level (0-100)."""
    store = get_store()
    result = accounts_mod.score_account(store, account_id)
    output(result, f"Score for {account_id}: {result['score']}/100 (Grade: {result['grade']})")


@accounts.command("export")
@click.option("-o", "--output", "output_path", required=True, help="Output JSON file path")
@handle_error
def accounts_export(output_path: str) -> None:
    """Export account profiles and reports to a JSON file."""
    store = get_store()
    result = accounts_mod.export_accounts(store, output_path)
    output(result, f"Exported {result['count']} accounts to {output_path}")


# ── theme-pages group ─────────────────────────────────────────────────────────

@cli.group("theme-pages")
def theme_pages():
    """Theme page creation, strategy, and conversion guide."""
    pass


@theme_pages.command("niches")
@handle_error
def theme_pages_niches() -> None:
    """List profitable theme page niches with conversion scores."""
    results = theme_mod.list_niches()
    if _json_output:
        output(results)
    else:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Conversion Score", "Est. RPM", "Avg Follower Value", "Top Platforms"],
            [[n["name"], str(n["conversion_potential"]), n["estimated_rpm"],
              n["avg_follower_value"], ", ".join(n["top_platforms"][:2])] for n in results]
        )


@theme_pages.command("guide")
@click.option("--niche", required=True, help="Target niche")
@handle_error
def theme_pages_guide(niche: str) -> None:
    """Print step-by-step theme page creation and monetization guide."""
    result = theme_mod.get_guide(niche)
    output(result, f"Theme Page Guide: {result['name']}")


@theme_pages.command("strategy")
@click.argument("niche")
@handle_error
def theme_pages_strategy(niche: str) -> None:
    """Full strategy: content mix, monetization, and conversion tactics."""
    result = theme_mod.get_strategy(niche)
    output(result, f"Strategy for '{niche}':")


@theme_pages.command("convert")
@click.argument("account_id")
@click.option("--to", "target_niche", required=True, help="Target niche to convert to")
@handle_error
def theme_pages_convert(account_id: str, target_niche: str) -> None:
    """Generate a conversion plan to turn an account into a theme page."""
    store = get_store()
    result = theme_mod.get_conversion_plan(store, account_id, target_niche)
    output(result, f"Conversion plan: {result['from_niche']} → {result['to_niche']}")


# ── schedule group ────────────────────────────────────────────────────────────

@cli.group()
def schedule():
    """Content calendar and posting schedule optimizer."""
    pass


@schedule.command("optimize")
@click.argument("account_id")
@click.option("--platform", default=None, help="Override account platform")
@handle_error
def schedule_optimize(account_id: str, platform: Optional[str]) -> None:
    """Generate optimal posting schedule for an account."""
    store = get_store()
    result = sched_mod.optimize_schedule(store, account_id, platform)
    output(result, f"Optimal schedule for {account_id} on {result['platform']}:")


@schedule.command("calendar")
@click.argument("account_id")
@click.option("--days", default=7, show_default=True, help="Number of days to generate")
@handle_error
def schedule_calendar(account_id: str, days: int) -> None:
    """Output a content calendar with topics, formats, and hashtags."""
    store = get_store()
    results = sched_mod.generate_calendar(store, account_id, days)
    if _json_output:
        output(results)
    else:
        click.echo(f"\n  Content calendar for {account_id} — {days} days:\n")
        for day in results:
            click.echo(f"  [{day['date']}] {day['day']}")
            for post in day["posts"]:
                click.echo(f"    {post['time']} — {post['content_type']} ({post['format']})")
                click.echo(f"      Hook: {post['hook_idea'][:60]}")
                click.echo(f"      Tags: {post['hashtags'][:60]}")
            click.echo()


@schedule.command("export")
@click.argument("account_id")
@click.option("-o", "--output", "output_path", required=True, help="Output JSON file path")
@handle_error
def schedule_export(account_id: str, output_path: str) -> None:
    """Export 30-day schedule and calendar to a JSON file."""
    store = get_store()
    result = sched_mod.export_schedule(store, account_id, output_path)
    output(result, f"Exported 30-day schedule to {output_path}")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    store = get_store()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends fetch --platform both":             "Fetch viral trends from YouTube & TikTok",
        "trends list":                              "List cached trends",
        "trends search KEYWORD":                    "Search trends by keyword",
        "hashtags research NICHE":                  "Research hashtags for a niche",
        "hashtags suggest --niche NICHE":           "Get optimal hashtag mix",
        "hashtags rank --by engagement":            "Rank hashtags by metric",
        "music trending --platform tiktok":         "Fetch trending audio",
        "music search QUERY":                       "Search music by title/artist",
        "accounts add --platform PLATFORM --username NAME --niche NICHE": "Add an account",
        "accounts list":                            "List registered accounts",
        "accounts optimize ACCOUNT_ID":             "Full optimization report",
        "accounts score ACCOUNT_ID":                "Score account (0-100)",
        "theme-pages niches":                       "List profitable niches",
        "theme-pages guide --niche NICHE":          "Step-by-step guide",
        "theme-pages strategy NICHE":               "Full growth strategy",
        "theme-pages convert ACCOUNT_ID --to NICHE":"Pivot/convert account",
        "schedule optimize ACCOUNT_ID":             "Optimal posting schedule",
        "schedule calendar ACCOUNT_ID --days 7":    "7-day content calendar",
        "help":                                     "Show this help",
        "quit / exit":                              "Exit the REPL",
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
