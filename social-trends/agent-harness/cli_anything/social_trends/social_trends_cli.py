"""Social Trends CLI - Agent-native social media trend intelligence tool.

Scrapes YouTube & TikTok for viral trends, hashtags, and music.
Optimizes social media accounts. Teaches and builds converting theme pages.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Optional, Any, List

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


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
            if v and isinstance(v[0], dict):
                click.echo(f"{pad}{k}: [{len(v)} items]")
                for item in v[:5]:
                    _print_dict(item, indent + 4)
                if len(v) > 5:
                    click.echo(f"{' ' * (indent + 4)}... and {len(v) - 5} more")
            else:
                click.echo(f"{pad}{k}: {', '.join(str(x) for x in v[:10])}")
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
            click.echo("  " + "  ".join(parts[:6]))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


# ── Error handling ────────────────────────────────────────────────────────────

def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, RuntimeError, FileNotFoundError) as e:
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
    """Social Trends — viral trend intelligence & account optimizer.

    Scrape YouTube & TikTok trends, find viral hashtags and music,
    optimize your social accounts, and build converting theme pages.

    \b
    Quick start:
      social-trends config set-key youtube <YOUR_KEY>
      social-trends trends fetch --platform both
      social-trends trends hashtags --niche fitness
      social-trends accounts add tiktok @mypage fitness
      social-trends accounts audit tiktok_mypage
      social-trends theme-page learn
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── config group ──────────────────────────────────────────────────────────────

@cli.group("config")
def config_group():
    """Configuration commands (set-key, show, save)."""
    pass


@config_group.command("set-key")
@click.argument("key_name", type=click.Choice(["youtube", "tiktok_apify", "rapidapi"]))
@click.argument("value")
@handle_error
def config_set_key(key_name: str, value: str) -> None:
    """Set an API key. KEY_NAME: youtube | tiktok_apify | rapidapi"""
    sess = get_session()
    sess.snapshot(f"set api key {key_name}")
    sess.config["api_keys"][key_name] = value
    sess.save_config()
    masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
    output({"success": True, "key": key_name, "value": masked},
           f"API key '{key_name}' saved: {masked}")


@config_group.command("show")
@handle_error
def config_show() -> None:
    """Show current configuration (API keys are masked)."""
    sess = get_session()
    cfg = dict(sess.config)
    # Mask keys
    masked_keys = {}
    for k, v in cfg.get("api_keys", {}).items():
        if v:
            masked_keys[k] = v[:4] + "..." + v[-4:] if len(v) > 8 else "****"
        else:
            masked_keys[k] = "(not set)"
    cfg["api_keys"] = masked_keys
    output(cfg, "Current configuration:")


@config_group.command("save")
@click.argument("path", required=False, default=None)
@handle_error
def config_save(path: Optional[str]) -> None:
    """Save configuration to disk."""
    sess = get_session()
    saved_path = sess.save_config(path)
    output({"success": True, "path": saved_path}, f"Configuration saved to {saved_path}")


@config_group.command("set-niche")
@click.argument("niches", nargs=-1, required=True)
@handle_error
def config_set_niche(niches: tuple) -> None:
    """Set your target niches (e.g. fitness finance travel)."""
    sess = get_session()
    sess.snapshot("set niches")
    sess.config["niches"] = list(niches)
    sess.save_config()
    output({"success": True, "niches": list(niches)},
           f"Niches set: {', '.join(niches)}")


@config_group.command("set-region")
@click.argument("regions", nargs=-1, required=True)
@handle_error
def config_set_region(regions: tuple) -> None:
    """Set target regions (e.g. US GB CA AU)."""
    sess = get_session()
    sess.snapshot("set regions")
    sess.config["target_regions"] = list(regions)
    sess.save_config()
    output({"success": True, "regions": list(regions)},
           f"Target regions: {', '.join(regions)}")


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Trend intelligence commands (fetch, hashtags, music, viral-patterns)."""
    pass


@trends.command("fetch")
@click.option("--platform", default="both",
              type=click.Choice(["youtube", "tiktok", "both"]),
              show_default=True, help="Platform to fetch trends from")
@click.option("--region", default="US", show_default=True,
              help="Region code (US, GB, CA, AU, etc.)")
@click.option("--max", "max_results", default=20, show_default=True,
              help="Max results per platform")
@click.option("--refresh", is_flag=True, help="Force refresh (bypass 30-min cache)")
@handle_error
def trends_fetch(platform: str, region: str, max_results: int, refresh: bool) -> None:
    """Fetch viral trends from YouTube and/or TikTok."""
    sess = get_session()
    if not _json_output:
        click.echo(f"Fetching {platform} trends for region {region}...")

    if platform == "both":
        result = trends_mod.fetch_all_trends(sess, region, max_results, refresh)
        if not _json_output:
            _print_trends_summary(result)
        else:
            output(result)
    elif platform == "youtube":
        result = trends_mod.fetch_youtube_trends(sess, region, max_results=max_results,
                                                  force_refresh=refresh)
        if not _json_output:
            _print_platform_trends(result, "YouTube")
        else:
            output(result)
    else:
        result = trends_mod.fetch_tiktok_trends(sess, region, max_results, refresh)
        if not _json_output:
            _print_platform_trends(result, "TikTok")
        else:
            output(result)


def _print_trends_summary(result: dict) -> None:
    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    yt = result.get("youtube", {})
    tt = result.get("tiktok", {})

    if yt.get("warning"):
        skin.warning(yt["warning"])
    if tt.get("warning"):
        skin.warning(tt["warning"])

    skin.section("YouTube Trending")
    _print_video_table(skin, yt.get("videos", [])[:5], "yt")

    skin.section("TikTok Trending")
    _print_video_table(skin, tt.get("videos", [])[:5], "tt")

    skin.section("Cross-Platform Top Hashtags")
    tags = result.get("cross_platform_hashtags", [])[:15]
    skin.table(
        ["Hashtag", "Score"],
        [[t["tag"], str(t["score"])] for t in tags]
    )

    music = tt.get("top_music", [])
    if music:
        skin.section("Trending Music on TikTok")
        skin.table(
            ["Track", "Frequency"],
            [[m["track"][:50], str(m["frequency"])] for m in music[:8]]
        )
    print()


def _print_platform_trends(result: dict, platform_name: str) -> None:
    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin()

    if result.get("warning"):
        skin.warning(result["warning"])

    prefix = "tt" if "tiktok" in platform_name.lower() else "yt"
    skin.section(f"{platform_name} Trending Videos")
    _print_video_table(skin, result.get("videos", [])[:10], prefix)

    skin.section("Top Hashtags")
    tags = result.get("top_hashtags", [])[:20]
    skin.table(["Hashtag", "Frequency"], [[t["tag"], str(t["frequency"])] for t in tags])

    if result.get("top_music"):
        skin.section("Trending Music")
        skin.table(["Track", "Frequency"],
                   [[m["track"][:50], str(m["frequency"])] for m in result["top_music"][:8]])
    print()


def _print_video_table(skin, videos: list, prefix: str) -> None:
    if not videos:
        skin.hint("  No videos. Check API key configuration.")
        return
    if prefix == "yt":
        skin.table(
            ["Title", "Channel", "Views", "Likes"],
            [[v.get("title", "")[:40], v.get("channel", "")[:20],
              f"{v.get('views', 0):,}", f"{v.get('likes', 0):,}"]
             for v in videos]
        )
    else:
        skin.table(
            ["Description", "Author", "Views", "Likes", "Shares"],
            [[v.get("description", "")[:40], v.get("author", "")[:18],
              f"{v.get('views', 0):,}", f"{v.get('likes', 0):,}",
              f"{v.get('shares', 0):,}"]
             for v in videos]
        )


@trends.command("hashtags")
@click.option("--niche", required=True, help="Your content niche (fitness, finance, travel, etc.)")
@click.option("--platform", default="all",
              type=click.Choice(["all", "tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--no-viral", is_flag=True, help="Exclude general viral hashtags")
@handle_error
def trends_hashtags(niche: str, platform: str, no_viral: bool) -> None:
    """Get trending hashtags for a niche and platform."""
    sess = get_session()
    result = trends_mod.get_hashtags_for_niche(sess, niche, platform, not no_viral)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Hashtags for #{result['niche']} ({platform})")
        for set_name, tags in result["sets"].items():
            click.echo(f"\n  {set_name}:")
            click.echo("    " + "  ".join(tags[:15]))
        skin.section("Recommended Mix (copy-paste ready)")
        click.echo("  " + " ".join(result["recommended_mix"][:20]))
        skin.hint(f"\n  Tip: {result['tip']}")
    else:
        output(result)


@trends.command("music")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              show_default=True)
@click.option("--type", "trend_type", default="all",
              type=click.Choice(["all", "rising", "peak", "evergreen"]),
              show_default=True, help="Filter by trend lifecycle stage")
@handle_error
def trends_music(platform: str, trend_type: str) -> None:
    """Show trending music and sounds to use in your content."""
    sess = get_session()
    result = trends_mod.get_trending_music(sess, platform, trend_type)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        src = result.get("source", "")
        skin.section(f"Trending Sounds — {platform.title()} ({trend_type}){' [cached]' if src == 'cache' else ''}")
        skin.table(
            ["Title", "Artist", "Uses", "Stage"],
            [[t["title"], t["artist"], t["uses"], t["trend"]] for t in result["tracks"]]
        )
        skin.hint(f"\n  Strategy: {result['strategy_tip']}")
    else:
        output(result)


@trends.command("viral-patterns")
@click.option("--platform", default="both",
              type=click.Choice(["tiktok", "youtube", "both"]),
              show_default=True)
@handle_error
def trends_viral_patterns(platform: str) -> None:
    """Show viral content formats, hooks, and optimal posting times."""
    sess = get_session()
    result = trends_mod.analyze_viral_patterns(sess, platform)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("High-Performing Content Formats")
        skin.table(
            ["Format", "Avg Boost", "Best For"],
            [[f["format"][:45], f["avg_engagement_boost"], f["best_for"][:35]]
             for f in result["content_formats"]]
        )
        skin.section("Optimal Posting Windows")
        for plt, info in result["optimal_length"].items():
            skin.status(f"{plt} sweet spot", info["sweet_spot"])
        print()
        for plt, times in result["posting_windows"].items():
            skin.status(f"{plt} peak times", "  |  ".join(times))
        skin.section("Proven Hook Formulas")
        for h in result["hook_formulas"]:
            click.echo(f"  • {h}")
        print()
    else:
        output(result)


# ── accounts group ────────────────────────────────────────────────────────────

@cli.group()
def accounts():
    """Account management & optimization (add, list, audit, optimize-bio, schedule)."""
    pass


@accounts.command("add")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube", "twitter"]))
@click.argument("username")
@click.argument("niche")
@click.option("--followers", default=0, show_default=True, help="Current follower count")
@click.option("--bio", default="", help="Current bio text")
@click.option("--goals", default=None, help="Comma-separated goals (e.g. 'grow,monetize')")
@handle_error
def accounts_add(platform: str, username: str, niche: str,
                 followers: int, bio: str, goals: Optional[str]) -> None:
    """Add a social media account to manage."""
    sess = get_session()
    goals_list = [g.strip() for g in goals.split(",")] if goals else None
    result = accounts_mod.add_account(sess, platform, username, niche,
                                       followers, bio, goals_list)
    sess.save_config()
    output(result, f"Added account: {platform}/{username} [{niche}]")


@accounts.command("remove")
@click.argument("account_id")
@handle_error
def accounts_remove(account_id: str) -> None:
    """Remove an account by ID."""
    sess = get_session()
    result = accounts_mod.remove_account(sess, account_id)
    sess.save_config()
    output(result, f"Removed account '{result['username']}'")


@accounts.command("list")
@handle_error
def accounts_list() -> None:
    """List all managed accounts."""
    sess = get_session()
    result = accounts_mod.list_accounts(sess)
    if not _json_output:
        if not result:
            click.echo("  No accounts. Use 'accounts add <platform> <username> <niche>'")
            return
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Platform", "Username", "Niche", "Followers", "Score"],
            [
                [a["id"][:25], a["platform"], a["username"][:20],
                 a["niche"][:15], f"{a.get('followers', 0):,}",
                 str(a.get("content_score") or "—")]
                for a in result
            ]
        )
    else:
        output(result)


@accounts.command("audit")
@click.argument("account_id")
@handle_error
def accounts_audit(account_id: str) -> None:
    """Run a full optimization audit on an account."""
    sess = get_session()
    result = accounts_mod.audit_account(sess, account_id)
    sess.save_config()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        score = result["score"]
        grade = result["grade"]
        skin.section(f"Account Audit: @{result['username']} ({result['platform']})")
        click.echo(f"\n  Score: {score}/100  Grade: {grade}")

        if result["wins"]:
            skin.section("Wins")
            for w in result["wins"]:
                skin.success(w)

        if result["issues"]:
            skin.section("Issues")
            for issue in result["issues"]:
                sev = issue["severity"]
                msg = f"[{sev.upper()}] {issue['field']}: {issue['issue']}"
                if sev == "high":
                    skin.error(msg)
                elif sev == "medium":
                    skin.warning(msg)
                else:
                    skin.info(msg)

        skin.section("Recommendations")
        for rec in result["recommendations"]:
            click.echo(f"\n  {rec['priority']}. {rec['action']}")
            skin.hint(f"     Why: {rec['why']}")

        skin.section("Platform Best Practices")
        bp = result.get("best_practices", {})
        if bp:
            skin.status("Post frequency", bp.get("posting_frequency", ""))
            skin.status("Video length", bp.get("optimal_video_length", ""))
            click.echo()
    else:
        output(result)


@accounts.command("bulk-audit")
@handle_error
def accounts_bulk_audit() -> None:
    """Audit all managed accounts and show a summary."""
    sess = get_session()
    result = accounts_mod.bulk_audit(sess)
    sess.save_config()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Bulk Audit — {result['total_accounts']} accounts (avg score: {result['avg_score']})")
        skin.table(
            ["Account ID", "Platform", "Username", "Score", "Grade", "Top Issue"],
            [
                [a.get("account_id", "")[:25], a.get("platform", ""),
                 a.get("username", "")[:18], str(a.get("score", "err")),
                 a.get("grade", ""), a.get("top_issue", "")[:40]]
                for a in result["accounts"]
            ]
        )
    else:
        output(result)


@accounts.command("optimize-bio")
@click.argument("account_id")
@click.option("--niche", default=None, help="Override niche for bio generation")
@click.option("--tone", default="professional",
              type=click.Choice(["professional", "casual", "authority", "community"]),
              show_default=True)
@click.option("--cta", "cta_type", default="link",
              type=click.Choice(["link", "dm", "shop", "collab", "follow", "subscribe"]),
              show_default=True, help="Call-to-action type")
@handle_error
def accounts_optimize_bio(account_id: str, niche: Optional[str],
                           tone: str, cta_type: str) -> None:
    """Generate optimized bio variants for an account."""
    sess = get_session()
    account = accounts_mod.get_account(sess, account_id)
    effective_niche = niche or account.get("niche", "general")
    result = accounts_mod.optimize_bio(sess, account_id, effective_niche, tone, True, cta_type)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Bio Optimization — @{account['username']} ({account['platform']})")
        skin.status("Char limit", str(result["char_limit"]))
        skin.section("Recommended Bio")
        click.echo()
        for line in result["recommended_bio"].split("\n"):
            click.echo(f"  {line}")
        click.echo(f"\n  ({result['char_count']} chars)")
        skin.section("Alternative Tones")
        skin.table(
            ["Tone", "Chars", "Fits Limit", "Preview"],
            [[a["tone"], a["char_count"], a["within_limit"],
              a["bio"][:50].replace("\n", " ")]
             for a in result["alternatives"]]
        )
        skin.section("Tips")
        for tip in result["tips"]:
            skin.hint(f"  • {tip}")
        print()
    else:
        output(result)


@accounts.command("update")
@click.argument("account_id")
@click.option("--bio", default=None, help="New bio text")
@click.option("--followers", default=None, type=int, help="Updated follower count")
@click.option("--niche", default=None, help="Update niche")
@handle_error
def accounts_update(account_id: str, bio: Optional[str],
                    followers: Optional[int], niche: Optional[str]) -> None:
    """Update account details."""
    sess = get_session()
    result = accounts_mod.update_account(sess, account_id, bio=bio,
                                          followers=followers, niche=niche)
    sess.save_config()
    output(result, f"Updated {account_id}: {', '.join(result['updated_fields'])}")


@accounts.command("schedule")
@click.argument("account_id")
@click.option("--frequency", default="daily",
              type=click.Choice(["daily", "aggressive", "weekly"]),
              show_default=True)
@handle_error
def accounts_schedule(account_id: str, frequency: str) -> None:
    """Generate a posting schedule for an account."""
    sess = get_session()
    result = accounts_mod.get_posting_schedule(sess, account_id, frequency)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Posting Schedule — @{result.get('niche', '')} ({result['platform']})")
        schedule = result["schedule"]
        for k, v in schedule.items():
            if isinstance(v, list):
                skin.status(k, ", ".join(v))
            else:
                skin.status(k, str(v))
        skin.section("7-Day Content Calendar")
        skin.table(
            ["Day", "Content Type"],
            [[c["day"], c["content_type"]] for c in result["content_calendar_template"]]
        )
        skin.hint(f"\n  Tip: {result['tip']}")
        print()
    else:
        output(result)


# ── theme-page group ──────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page_group():
    """Theme page creation, strategy & conversion education."""
    pass


@theme_page_group.command("learn")
@handle_error
def theme_page_learn() -> None:
    """Complete beginner guide to building converting theme pages."""
    result = theme_mod.learn_theme_page_basics()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("What Is a Theme Page?")
        click.echo(f"  {result['what_is_a_theme_page']}\n")

        skin.section("Why Theme Pages Work")
        for reason in result["why_theme_pages_work"]:
            click.echo(f"  • {reason}")

        skin.section("The 5 Types of Theme Pages")
        skin.table(
            ["Type", "Effort", "Monetization", "Best For"],
            [[p["type"][:35], p["effort"], p["monetization"][:15], p["best_for"]]
             for p in result["the_5_page_types"]]
        )

        skin.section("Income Streams (Ranked by ROI)")
        for s in result["income_streams_ranked"]:
            click.echo(f"  {s['rank']}. {s['stream']}")
            skin.hint(f"     {s['why']}")

        skin.section("30-Day Action Plan")
        for step in result["30_day_action_plan"]:
            click.echo(f"  • {step}")

        skin.section("Mistakes to Avoid")
        for m in result["mistakes_to_avoid"]:
            skin.warning(m)

        skin.section("Essential Tools")
        for category, tools in result["resources"].items():
            skin.status(category.title(), ", ".join(tools))
        print()
    else:
        output(result)


@theme_page_group.command("niches")
@click.option("--sort-by", default="monetization",
              type=click.Choice(["monetization", "growth", "difficulty_asc"]),
              show_default=True)
@handle_error
def theme_page_niches(sort_by: str) -> None:
    """List all supported niches sorted by monetization potential."""
    result = theme_mod.list_niches(sort_by=sort_by)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Available Niches (sorted by {sort_by})")
        skin.table(
            ["ID", "Niche", "Difficulty", "Competition", "Monetization", "Growth Speed"],
            [[n["id"], n["display"], n["difficulty"], n["competition"],
              n["monetization_potential"], n["growth_speed"]]
             for n in result]
        )
        click.echo("\n  Use 'theme-page niche-detail <ID>' for full details\n")
    else:
        output(result)


@theme_page_group.command("niche-detail")
@click.argument("niche_id")
@handle_error
def theme_page_niche_detail(niche_id: str) -> None:
    """Show full detail for a niche including monetization paths."""
    result = theme_mod.get_niche_detail(niche_id)
    output(result, f"Niche: {result['display']}")


@theme_page_group.command("create")
@click.argument("name")
@click.argument("niche_id")
@click.argument("platforms", nargs=-1, required=True)
@click.option("--strategy", default="repost_curate",
              type=click.Choice(["repost_curate", "ai_generated", "ugc_submissions", "aggregator"]),
              show_default=True, help="Content creation strategy")
@handle_error
def theme_page_create(name: str, niche_id: str, platforms: tuple, strategy: str) -> None:
    """Create a new theme page with a launch plan.

    \b
    Example:
      theme-page create "FitLife Daily" fitness_motivation tiktok instagram
    """
    sess = get_session()
    result = theme_mod.create_theme_page(sess, name, niche_id, list(platforms), strategy)
    sess.save_config()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        page = result["page"]
        skin.section(f"Theme Page Created: {page['name']}")
        skin.status("Niche", page["niche_display"])
        skin.status("Platforms", ", ".join(page["platforms"]))
        skin.status("Strategy", page["content_strategy"])
        skin.status("Page ID", page["id"])
        skin.section("Monetization Paths")
        for path in page["monetization_paths"]:
            click.echo(f"  • {path}")
        skin.section("Launch Plan")
        for step in result["quick_start"]:
            click.echo(f"  → {step}")
        skin.section("Growth Milestones")
        skin.table(
            ["Target", "Focus"],
            [[m["target"], m["focus"]] for m in page["milestones"]]
        )
        print()
    else:
        output(result)


@theme_page_group.command("list")
@handle_error
def theme_page_list() -> None:
    """List all theme pages."""
    sess = get_session()
    result = theme_mod.list_theme_pages(sess)
    if not _json_output:
        if not result:
            click.echo("  No theme pages. Use 'theme-page create' to add one.")
            return
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["ID", "Name", "Niche", "Platforms", "Strategy", "Status"],
            [[p["id"][:20], p["name"][:25], p["niche_display"][:20],
              ", ".join(p["platforms"])[:20], p["content_strategy"][:18], p["status"]]
             for p in result]
        )
    else:
        output(result)


@theme_page_group.command("funnels")
@handle_error
def theme_page_funnels() -> None:
    """List available conversion funnel types."""
    result = theme_mod.list_funnels()
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Conversion Funnel Types")
        skin.table(
            ["ID", "Funnel", "Complexity", "Conv. Rate", "Best For"],
            [[f["id"], f["display"][:28], f["complexity"],
              f["conversion_rate"], f["best_for"][:35]]
             for f in result]
        )
        click.echo("\n  Use 'theme-page playbook <funnel_id>' for the step-by-step guide\n")
    else:
        output(result)


@theme_page_group.command("playbook")
@click.argument("funnel_type", default="dm_funnel")
@click.option("--niche", default=None, help="Your niche for personalized tips")
@handle_error
def theme_page_playbook(funnel_type: str, niche: Optional[str]) -> None:
    """Get the step-by-step conversion playbook for a funnel type."""
    sess = get_session()
    result = theme_mod.get_conversion_playbook(sess, funnel_type, niche)
    if not _json_output:
        from cli_anything.social_trends.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Conversion Playbook: {result['display']}")
        skin.status("Complexity", result["complexity"])
        skin.status("Expected Conv. Rate", result["conversion_rate"])
        click.echo(f"\n  {result['description']}\n")

        skin.section("Steps")
        for step in result.get("steps", []):
            click.echo(f"  {step}")

        skin.section("Tools")
        for tool in result.get("tools", []):
            click.echo(f"  • {tool}")

        if result.get("commission_examples"):
            skin.section("Commission Examples")
            for product, rate in result["commission_examples"].items():
                skin.status(product, rate)

        if result.get("niche_specific_tips"):
            skin.section("Niche-Specific Tips")
            for tip in result["niche_specific_tips"]:
                skin.trend(tip)

        skin.section("KPIs to Track")
        for kpi in result.get("kpis_to_track", []):
            click.echo(f"  • {kpi}")

        skin.section("Pitfalls to Avoid")
        for warning in result.get("red_flags_to_avoid", []):
            skin.warning(warning)
        print()
    else:
        output(result)


# ── session group ─────────────────────────────────────────────────────────────

@cli.group("session")
def session_group():
    """Session commands (undo, redo, status, history)."""
    pass


@session_group.command("undo")
@handle_error
def session_undo() -> None:
    """Undo the last configuration change."""
    sess = get_session()
    description = sess.undo()
    output({"success": True, "undone": description}, f"Undone: {description}")


@session_group.command("redo")
@handle_error
def session_redo() -> None:
    """Redo the last undone change."""
    sess = get_session()
    description = sess.redo()
    output({"success": True, "redone": description}, f"Redone: {description}")


@session_group.command("status")
@handle_error
def session_status() -> None:
    """Show session status (accounts, pages, API keys, etc.)."""
    sess = get_session()
    result = sess.status()
    output(result, "Session status:")


@session_group.command("history")
@handle_error
def session_history() -> None:
    """Show the undo history."""
    sess = get_session()
    result = sess.list_history()
    output(result, f"History ({len(result)} entries):")


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive REPL session."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_trends.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    sess = get_session()
    status = sess.status()
    skin.info(f"Loaded: {status['accounts_count']} accounts, "
              f"{status['theme_pages_count']} theme pages")
    if not status["youtube_api_key_set"]:
        skin.warning("YouTube API key not set — run: config set-key youtube <key>")
    if not status["tiktok_api_key_set"]:
        skin.warning("TikTok API key not set — run: config set-key tiktok_apify <key>")

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "config set-key youtube <key>": "Set YouTube Data API key",
        "config set-key tiktok_apify <key>": "Set Apify TikTok key",
        "config set-key rapidapi <key>": "Set RapidAPI key",
        "config set-niche fitness finance": "Set your target niches",
        "config show": "Show current config",
        "trends fetch --platform both": "Fetch viral trends (YouTube + TikTok)",
        "trends hashtags --niche fitness": "Get niche hashtags",
        "trends music": "Show trending sounds",
        "trends viral-patterns": "Show viral content formats & hooks",
        "accounts add tiktok @user fitness": "Add an account to manage",
        "accounts list": "List all accounts",
        "accounts audit <account_id>": "Full account optimization audit",
        "accounts bulk-audit": "Audit all accounts at once",
        "accounts optimize-bio <account_id>": "Generate optimized bio variants",
        "accounts schedule <account_id>": "Get a posting schedule",
        "theme-page learn": "Complete beginner guide to theme pages",
        "theme-page niches": "Browse monetizable niches",
        "theme-page create <name> <niche> <platforms>": "Create a theme page plan",
        "theme-page funnels": "List conversion funnel types",
        "theme-page playbook <funnel_type>": "Step-by-step conversion playbook",
        "session status": "Show session status",
        "session undo": "Undo last change",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
    }

    while True:
        try:
            context_parts = []
            niches = sess.config.get("niches", [])
            if niches:
                context_parts.append(niches[0])
            acct_count = len(sess.config.get("accounts", {}))
            if acct_count:
                context_parts.append(f"{acct_count} accts")
            context = " · ".join(context_parts)
            raw = skin.get_input(pt_session, context, sess._modified)
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
