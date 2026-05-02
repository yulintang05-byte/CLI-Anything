"""Social Trends CLI — agent-native social media trends, hashtags, music, and account optimizer.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends   (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any

from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import account as account_mod
from cli_anything.social_trends.core import theme_page as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


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
        except (ValueError, KeyError, FileNotFoundError, RuntimeError) as e:
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
    """Social Trends — agent-native social media trends tracker & account optimizer.

    Track viral trends, get hashtag strategies, discover trending music, optimize
    accounts, and build converting theme pages across TikTok, YouTube, and Instagram.

    \b
    Quick start:
      social-trends trends fetch --platform all
      social-trends trends list --platform tiktok
      social-trends hashtags suggest --niche fitness --platform tiktok
      social-trends music trending --platform tiktok
      social-trends account optimize --platform youtube
      social-trends theme-page create --niche ai_tools
    """
    global _json_output
    _json_output = use_json

    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Viral trend scraping and management (fetch, list, show, add, cache-info)."""
    pass


@trends.command("fetch")
@click.option(
    "--platform", default="all", show_default=True,
    type=click.Choice(["tiktok", "youtube", "all"]),
    help="Platform to fetch trends for",
)
@click.option("--force", is_flag=True, help="Force refresh even if cache is fresh")
@handle_error
def trends_fetch(platform: str, force: bool) -> None:
    """Fetch latest viral trends. Tries live data (yt-dlp) then falls back to seed data."""
    result = trends_mod.fetch_trends(platform, force)
    output(result, f"Trends fetched ({platform}):")


@trends.command("list")
@click.option(
    "--platform", default="all", show_default=True,
    type=click.Choice(["tiktok", "youtube", "all"]),
)
@click.option("--status", default=None, help="Filter by status: peaking, growing, evergreen, fading")
@click.option("--category", default=None, help="Filter by category")
@handle_error
def trends_list(platform: str, status: Optional[str], category: Optional[str]) -> None:
    """List all cached trends."""
    all_trends = trends_mod.list_trends(platform)
    if status:
        all_trends = [t for t in all_trends if t.get("status") == status]
    if category:
        all_trends = [t for t in all_trends if t.get("category", "").lower() == category.lower()]

    if not all_trends:
        click.echo("  No trends found. Run 'trends fetch' first.")
        return

    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Platform", "Title", "Category", "Status", "Views Est."],
            [
                [
                    t.get("id", ""),
                    t.get("platform", ""),
                    t.get("title", "")[:30],
                    t.get("category", ""),
                    t.get("status", ""),
                    t.get("views_est", ""),
                ]
                for t in all_trends
            ],
        )
    else:
        output(all_trends)


@trends.command("show")
@click.argument("trend_id")
@handle_error
def trends_show(trend_id: str) -> None:
    """Show full details about a specific trend."""
    result = trends_mod.show_trend(trend_id)
    output(result, f"Trend: {result.get('title', trend_id)}")


@trends.command("add")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube"]))
@click.option("--title", required=True, help="Trend name/title")
@click.option("--category", default="other", show_default=True, help="Content category")
@click.option("--description", default="", help="Brief description")
@click.option("--hashtags", default="", help="Comma-separated hashtag list (e.g. '#fyp,#viral')")
@click.option("--sound", default="", help="Associated sound/music")
@handle_error
def trends_add(platform: str, title: str, category: str, description: str,
               hashtags: str, sound: str) -> None:
    """Add a manually observed trend to local cache."""
    tag_list = [h.strip() for h in hashtags.split(",") if h.strip()] if hashtags else []
    result = trends_mod.add_custom_trend(platform, title, category, description, tag_list, sound)
    output(result, f"Added custom trend '{title}' to {platform}")


@trends.command("cache-info")
@handle_error
def trends_cache_info() -> None:
    """Show cache metadata (freshness, source, counts)."""
    result = trends_mod.get_cache_info()
    output(result, "Trend cache info:")


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Hashtag strategy engine (suggest, all-platforms, trending, niches, platforms)."""
    pass


@hashtags.command("suggest")
@click.option("--niche", required=True, help=f"Content niche (run 'hashtags niches' to list)")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"]),
    help="Target platform",
)
@click.option(
    "--goal", default="viral", show_default=True,
    type=click.Choice(["viral", "growth", "engagement", "sales", "community"]),
    help="Optimization goal",
)
@handle_error
def hashtags_suggest(niche: str, platform: str, goal: str) -> None:
    """Get an optimized hashtag set for a niche/platform/goal combination."""
    result = hashtags_mod.suggest_hashtags(niche, platform, goal)
    if not _json_output:
        click.echo(f"\nPrimary set ({result['optimal_count']} tags for {platform}):")
        click.echo(f"  {result['copy_paste']}")
        click.echo(f"\nExtended set ({len(result['extended_set'])} tags):")
        click.echo(f"  {' '.join(result['extended_set'])}")
        click.echo(f"\nNote: {result['platform_note']}")
    else:
        output(result)


@hashtags.command("all-platforms")
@click.option("--niche", required=True, help="Content niche")
@click.option(
    "--goal", default="viral", show_default=True,
    type=click.Choice(["viral", "growth", "engagement", "sales", "community"]),
)
@handle_error
def hashtags_all_platforms(niche: str, goal: str) -> None:
    """Get optimized hashtag sets for all platforms at once."""
    result = hashtags_mod.hashtag_set_all_platforms(niche, goal)
    if not _json_output:
        for platform, data in result.items():
            click.echo(f"\n{platform.upper()} ({data['optimal_count']} tags):")
            click.echo(f"  {data['copy_paste']}")
    else:
        output(result)


@hashtags.command("trending")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"]),
)
@handle_error
def hashtags_trending(platform: str) -> None:
    """Show current trending hashtags for a platform."""
    result = hashtags_mod.trending_hashtags(platform)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Tag", "Reach", "Category"],
            [[t["tag"], t["reach"], t["category"]] for t in result],
        )
    else:
        output(result)


@hashtags.command("niches")
@handle_error
def hashtags_niches() -> None:
    """List all available content niches."""
    niches = hashtags_mod.list_niches()
    if not _json_output:
        click.echo("Available niches:")
        for n in niches:
            click.echo(f"  {n}")
    else:
        output(niches)


@hashtags.command("platforms")
@handle_error
def hashtags_platforms() -> None:
    """List supported platforms with hashtag best practices."""
    from cli_anything.social_trends.core.hashtags import _PLATFORM_CONFIG
    if not _json_output:
        for p, config in _PLATFORM_CONFIG.items():
            click.echo(f"\n{p.upper()}:")
            click.echo(f"  Optimal count: {config['optimal_count']}")
            click.echo(f"  Max count: {config['max_count']}")
            click.echo(f"  Note: {config['note']}")
    else:
        output(_PLATFORM_CONFIG)


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Trending music and sounds (trending, search, by-trend, by-use-case, genres)."""
    pass


@music.command("trending")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube"]),
)
@handle_error
def music_trending(platform: str) -> None:
    """Show trending music/sounds for a platform."""
    result = music_mod.trending_music(platform)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Title", "Artist", "Genre", "Status", "Use Case"],
            [
                [
                    t["id"],
                    t["title"][:30],
                    t["artist"][:20],
                    t["genre"][:15],
                    t["status"],
                    t["use_case"][:35],
                ]
                for t in result
            ],
        )
        click.echo("\nRun 'music show <id>' for full details including tips.")
    else:
        output(result)


@music.command("show")
@click.argument("music_id")
@handle_error
def music_show(music_id: str) -> None:
    """Show full details for a specific music entry."""
    all_music = music_mod.search_music("", "all")
    match = next((m for m in all_music if m.get("id") == music_id), None)
    if not match:
        _err(f"Music ID '{music_id}' not found. Run 'music trending' to see IDs.")
        if not _repl_mode:
            sys.exit(1)
        return
    output(match, f"Music: {match['title']}")


@music.command("search")
@click.argument("query")
@click.option(
    "--platform", default="all", show_default=True,
    type=click.Choice(["tiktok", "youtube", "all"]),
)
@handle_error
def music_search(query: str, platform: str) -> None:
    """Search trending music by title, artist, genre, or use case."""
    results = music_mod.search_music(query, platform)
    if not results:
        click.echo(f"  No music found matching '{query}'.")
        return
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Platform", "Title", "Artist", "Genre", "Status"],
            [
                [m["id"], m["platform"], m["title"][:30], m["artist"][:20], m["genre"][:15], m["status"]]
                for m in results
            ],
        )
    else:
        output(results)


@music.command("by-trend")
@click.argument("trend_name")
@handle_error
def music_by_trend(trend_name: str) -> None:
    """Find music associated with a specific trend name."""
    results = music_mod.get_music_by_trend(trend_name)
    if not results:
        click.echo(f"  No music found for trend '{trend_name}'.")
        return
    output(results, f"Music for trend '{trend_name}':")


@music.command("by-use-case")
@click.argument("use_case")
@click.option(
    "--platform", default="all", show_default=True,
    type=click.Choice(["tiktok", "youtube", "all"]),
)
@handle_error
def music_by_use_case(use_case: str, platform: str) -> None:
    """Find music that fits a content use case (e.g. 'morning routine', 'gym')."""
    results = music_mod.music_by_use_case(use_case, platform)
    if not results:
        click.echo(f"  No music found for use case '{use_case}'.")
        return
    output(results, f"Music for '{use_case}':")


@music.command("genres")
@click.option(
    "--platform", default="all", show_default=True,
    type=click.Choice(["tiktok", "youtube", "all"]),
)
@handle_error
def music_genres(platform: str) -> None:
    """List available genres in the music database."""
    genres = music_mod.list_genres(platform)
    if not _json_output:
        click.echo("Available genres:")
        for g in genres:
            click.echo(f"  {g}")
    else:
        output(genres)


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account optimization (optimize, schedule, analyze, roadmap, platforms)."""
    pass


@account.command("optimize")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"]),
)
@handle_error
def account_optimize(platform: str) -> None:
    """Show the full optimization checklist for a platform."""
    result = account_mod.optimize_account(platform)
    if not _json_output:
        click.echo(f"\n{platform.upper()} OPTIMIZATION CHECKLIST")
        click.echo(f"  Max possible score: {result['total_possible_score']} pts\n")

        click.echo("  [CRITICAL — do these first]")
        for item in result["critical_items"]:
            click.echo(f"  [ ] {item['item']}")
            click.echo(f"      Impact: {item['impact']}")

        click.echo("\n  [HIGH PRIORITY]")
        for item in result["high_items"]:
            click.echo(f"  [ ] {item['item']}")

        click.echo("\n  [MEDIUM PRIORITY]")
        for item in result["medium_items"]:
            click.echo(f"  [ ] {item['item']}")
    else:
        output(result)


@account.command("schedule")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"]),
)
@handle_error
def account_schedule(platform: str) -> None:
    """Show optimal posting schedule for a platform."""
    result = account_mod.account_schedule(platform)
    output(result, f"{platform.upper()} Posting Schedule:")


@account.command("analyze")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"]),
)
@click.option("--niche", default="general", help="Your content niche")
@click.option(
    "--completed", default="",
    help="Comma-separated list of completed checklist items (wrap in quotes)",
)
@handle_error
def account_analyze(platform: str, niche: str, completed: str) -> None:
    """Score your account against the optimization checklist."""
    completed_list = [c.strip() for c in completed.split(",") if c.strip()] if completed else []
    result = account_mod.analyze_account(platform, niche, completed_list)
    if not _json_output:
        click.echo(f"\nAccount Score: {result['score']}/{result['max_score']} ({result['score_pct']}%) — Grade: {result['grade']}")
        click.echo(f"Status: {result['status']}")
        click.echo(f"\nNext actions:")
        for action in result["next_actions"]:
            click.echo(f"  → {action['item']}")
    else:
        output(result)


@account.command("roadmap")
@click.option(
    "--platform", required=True,
    type=click.Choice(["tiktok", "youtube", "instagram"]),
)
@click.option("--followers", required=True, type=int, help="Current follower count")
@handle_error
def account_roadmap(platform: str, followers: int) -> None:
    """Get a growth roadmap based on your current follower count."""
    result = account_mod.growth_roadmap(platform, followers)
    if not _json_output:
        click.echo(f"\n{platform.upper()} Growth Roadmap")
        click.echo(f"  Current followers: {followers:,}")
        click.echo(f"  Current phase: {result['current_phase']}")
        click.echo(f"  Focus: {result['current_focus']}")
        if result["next_milestone"]:
            click.echo(f"  Next milestone: {result['next_milestone']:,} followers ({result['followers_to_next']:,} to go)")
    else:
        output(result)


@account.command("platforms")
@handle_error
def account_platforms() -> None:
    """List all supported platforms."""
    platforms = account_mod.list_platforms()
    if not _json_output:
        click.echo("Supported platforms:")
        for p in platforms:
            click.echo(f"  {p}")
    else:
        output(platforms)


# ── theme-page group ──────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page():
    """Theme page strategy (create, niches, compare, monetize, content-calendar)."""
    pass


@theme_page.command("create")
@click.option("--niche", required=True, help="Theme page niche (run 'theme-page niches' to list)")
@handle_error
def theme_page_create(niche: str) -> None:
    """Generate a complete theme page blueprint with setup plan, content strategy, and monetization."""
    result = theme_mod.create_theme_page(niche)
    if not _json_output:
        click.echo(f"\n{'='*60}")
        click.echo(f"THEME PAGE BLUEPRINT: {result['name'].upper()}")
        click.echo(f"{'='*60}")
        click.echo(f"\nDifficulty: {result['difficulty']}  |  Growth Speed: {result['growth_speed']}")
        click.echo(f"Monthly Potential: {result['monthly_potential']}")
        click.echo(f"Saturation: {result['saturation']}")
        click.echo(f"\nBrand Voice: {result['brand_voice']}")
        click.echo(f"Target Audience: {result['target_audience']}")
        click.echo(f"Top Platforms: {', '.join(result['top_platforms'])}")
        click.echo(f"\nConversion Hook:")
        click.echo(f"  {result['conversion_hook']}")
        click.echo(f"\nMonetization Stack: {' → '.join(result['monetization_stack'])}")
        click.echo(f"\nBest Post Formats:")
        for fmt in result["best_post_formats"]:
            click.echo(f"  • {fmt}")
        click.echo(f"\nFirst 30 Days Plan:")
        for step in result["first_30_days"]:
            click.echo(f"  {step}")
        click.echo(f"\nSetup Action Plan:")
        for step in result["setup_action_plan"]:
            click.echo(f"  {step}")
        click.echo(f"\nRun 'theme-page monetize --niche {niche}' for full monetization details.")
        click.echo(f"Run 'theme-page content-calendar --niche {niche}' for 30-day content plan.")
    else:
        output(result)


@theme_page.command("niches")
@handle_error
def theme_page_niches() -> None:
    """List all profitable theme page niches with key metrics."""
    result = theme_mod.list_niches()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Name", "Difficulty", "Growth", "Monthly $", "Saturation"],
            [
                [
                    n["niche"],
                    n["name"][:25],
                    n["difficulty"],
                    n["growth_speed"],
                    n["monthly_potential"],
                    n["saturation"],
                ]
                for n in result
            ],
        )
    else:
        output(result)


@theme_page.command("compare")
@click.argument("niches", nargs=-1, required=True)
@handle_error
def theme_page_compare(niches: tuple) -> None:
    """Compare multiple niches side by side (e.g. theme-page compare finance ai_tools fitness)."""
    result = theme_mod.compare_niches(list(niches))
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Niche", "Difficulty", "Growth", "Monthly $", "Saturation", "RPM"],
            [
                [n["niche"], n["difficulty"], n["growth_speed"], n["monthly_potential"],
                 n["saturation"], n["avg_rpm"]]
                for n in result
            ],
        )
    else:
        output(result)


@theme_page.command("monetize")
@click.option("--niche", required=True, help="Theme page niche")
@handle_error
def theme_page_monetize(niche: str) -> None:
    """Show detailed monetization strategy for a niche including action steps."""
    result = theme_mod.monetize(niche)
    if not _json_output:
        click.echo(f"\nMonetization Strategy: {result['name']}")
        click.echo(f"Monthly Potential: {result['monthly_potential']}")
        click.echo(f"Stack: {result['stack_summary']}")
        click.echo(f"\nNote: {result['diversification_note']}")
        for method in result["all_methods"]:
            click.echo(f"\n--- {method['name']} ---")
            click.echo(f"  Setup time: {method['setup_time']}")
            click.echo(f"  Earning potential: {method['earning_potential']}")
            click.echo(f"  Platforms: {', '.join(method['platforms'])}")
            click.echo(f"  Action steps:")
            for step in method["action_steps"]:
                click.echo(f"    → {step}")
    else:
        output(result)


@theme_page.command("content-calendar")
@click.option("--niche", required=True, help="Theme page niche")
@click.option("--days", default=30, show_default=True, type=int, help="Number of days to generate")
@handle_error
def theme_page_content_calendar(niche: str, days: int) -> None:
    """Generate a content posting calendar with formats, hooks, and CTAs."""
    result = theme_mod.content_calendar(niche, days)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        peak_marker = lambda r: "★" if r["is_peak_day"] else " "
        skin.table(
            ["Day", "Date", "Weekday", "P", "Format", "Hook"],
            [
                [
                    str(r["day"]),
                    r["date"],
                    r["weekday"][:3],
                    peak_marker(r),
                    r["format"][:25],
                    r["hook_idea"][:40],
                ]
                for r in result
            ],
        )
        click.echo("\n  ★ = peak posting day")
    else:
        output(result)


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "trends fetch [--platform all|tiktok|youtube]": "Fetch latest viral trends",
        "trends list [--platform <p>] [--status <s>]": "List cached trends",
        "trends show <id>": "Show trend details",
        "trends add --platform <p> --title <t>": "Add custom observed trend",
        "hashtags suggest --niche <n> --platform <p>": "Get optimized hashtag set",
        "hashtags all-platforms --niche <n>": "Hashtags for all platforms",
        "hashtags trending --platform <p>": "Show trending hashtags",
        "hashtags niches": "List available niches",
        "music trending --platform <p>": "Show trending music",
        "music search <query>": "Search music database",
        "music by-use-case <use_case>": "Find music by content type",
        "account optimize --platform <p>": "Full optimization checklist",
        "account schedule --platform <p>": "Best posting times",
        "account roadmap --platform <p> --followers <n>": "Growth roadmap",
        "theme-page create --niche <n>": "Full theme page blueprint",
        "theme-page niches": "List profitable niches",
        "theme-page compare <n1> <n2>": "Compare niches side-by-side",
        "theme-page monetize --niche <n>": "Detailed monetization strategy",
        "theme-page content-calendar --niche <n>": "30-day content calendar",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            raw = skin.get_input(pt_session, "social-trends", False)
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
