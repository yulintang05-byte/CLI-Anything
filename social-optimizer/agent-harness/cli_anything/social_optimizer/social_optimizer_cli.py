#!/usr/bin/env python3
"""Social Optimizer CLI — account management, content calendars, and theme page playbook.

Usage:
    cli-anything-social-optimizer account add tiktok @handle --niche fitness
    cli-anything-social-optimizer account list
    cli-anything-social-optimizer account audit @handle
    cli-anything-social-optimizer schedule best-times --platform tiktok --niche fitness
    cli-anything-social-optimizer theme-page guide [--niche fitness] [--output guide.json]
    cli-anything-social-optimizer theme-page niches
    cli-anything-social-optimizer theme-page convert
    cli-anything-social-optimizer content calendar --days 30 --niche fitness
    cli-anything-social-optimizer hashtag strategy <niche> --platform tiktok
    cli-anything-social-optimizer report combined [--output report.json]
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.social_optimizer.utils.optimizer_backend import (
    load_config, save_config,
    add_account, list_accounts, get_account, remove_account,
    SUPPORTED_PLATFORMS, THEME_PAGE_PLAYBOOK,
    generate_content_calendar, POSTING_CADENCE,
    get_hashtag_rules,
)

_json_output = False
_repl_mode = False


def output(data, message: str = ""):
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        if isinstance(data, dict):
            _print_dict(data)
        elif isinstance(data, list):
            _print_list(data)
        elif data is not None:
            click.echo(str(data))


def _print_dict(d: dict, indent: int = 0):
    prefix = "  " * indent
    for k, v in d.items():
        if isinstance(v, dict):
            click.echo(f"{prefix}{k}:")
            _print_dict(v, indent + 1)
        elif isinstance(v, list):
            click.echo(f"{prefix}{k}:")
            _print_list(v, indent + 1)
        else:
            click.echo(f"{prefix}{k}: {v}")


def _print_list(items: list, indent: int = 0):
    prefix = "  " * indent
    for i, item in enumerate(items):
        if isinstance(item, dict):
            click.echo(f"{prefix}[{i}]")
            _print_dict(item, indent + 1)
        elif isinstance(item, str):
            click.echo(f"{prefix}{item}")
        else:
            click.echo(f"{prefix}- {item}")


def handle_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (FileNotFoundError, ValueError, RuntimeError, TimeoutError) as e:
            if _json_output:
                click.echo(json.dumps({"error": str(e), "type": type(e).__name__}))
            else:
                click.echo(f"Error: {e}", err=True)
            if not _repl_mode:
                sys.exit(1)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# ── Main CLI ────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output as JSON")
@click.pass_context
def cli(ctx, use_json):
    """Social Optimizer — account management, content calendars, and theme page playbook."""
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── Account ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Account management — add, list, audit, and remove accounts."""
    pass


@account.command("add")
@click.argument("platform", type=click.Choice(SUPPORTED_PLATFORMS, case_sensitive=False))
@click.argument("handle")
@click.option("--niche", "-n", default="", help="Content niche (e.g. fitness, food)")
@click.option("--goal", "-g", default="", help="Growth goal (e.g. 'reach 10K in 90 days')")
@handle_error
def account_add(platform, handle, niche, goal):
    """Register a social media account for tracking."""
    result = add_account(platform=platform, handle=handle, niche=niche, goal=goal)
    output(result, f"✓ Added @{handle} on {platform}")


@account.command("list")
def account_list():
    """List all registered accounts."""
    accounts = list_accounts()
    if not accounts:
        click.echo("No accounts registered. Run: account add <platform> <handle>")
        return
    output(accounts, f"Registered accounts ({len(accounts)}):")


@account.command("audit")
@click.argument("handle")
@click.option("--platform", "-p",
              type=click.Choice(SUPPORTED_PLATFORMS, case_sensitive=False),
              default=None)
@click.option("--niche", "-n", default=None, help="Override niche for tips")
@handle_error
def account_audit(handle, platform, niche):
    """Get optimization tips for an account."""
    acct = get_account(handle, platform)
    eff_niche = niche or (acct.get("niche") if acct else "") or ""
    eff_platform = platform or (acct.get("platform") if acct else "tiktok")

    if eff_platform in ("tiktok",):
        from cli_anything.tiktok.utils.tiktok_backend import account_audit_tips
        result = account_audit_tips(handle=f"@{handle}", niche=eff_niche, platform=eff_platform)
    else:
        from cli_anything.youtube.utils.yt_backend import channel_audit_tips
        result = channel_audit_tips(niche=eff_niche)
        result["handle"] = f"@{handle}"
        result["platform"] = eff_platform

    output(result, f"\n✓ Account audit for @{handle} [{eff_platform}]:")


@account.command("remove")
@click.argument("handle")
@click.argument("platform", type=click.Choice(SUPPORTED_PLATFORMS, case_sensitive=False))
@handle_error
def account_remove(handle, platform):
    """Remove a registered account."""
    removed = remove_account(handle=handle, platform=platform)
    if removed:
        output({"removed": True}, f"✓ Removed @{handle} from {platform}")
    else:
        output({"removed": False}, f"Account @{handle} not found on {platform}")


# ── Schedule ─────────────────────────────────────────────────────────────

@cli.group()
def schedule():
    """Scheduling tools — best posting times and cadence."""
    pass


@schedule.command("best-times")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube_shorts", "instagram_reels"],
                                case_sensitive=False),
              default="tiktok", show_default=True)
@click.option("--niche", "-n", default="", help="Your niche (informational only)")
@handle_error
def schedule_best_times(platform, niche):
    """Show optimal posting times for a platform."""
    from cli_anything.tiktok.utils.tiktok_backend import get_posting_schedule
    schedule_data = get_posting_schedule(platform)
    result = {
        "platform": platform,
        "niche": niche or "general",
        "best_times": schedule_data,
        "note": (
            "Times shown in your audience's local timezone. "
            "Check platform analytics to confirm your specific audience's peak hours."
        ),
    }
    output(result, f"\nBest posting times for {platform}:")


@schedule.command("cadence")
@click.option("--platform", "-p",
              type=click.Choice(list(POSTING_CADENCE.keys()), case_sensitive=False),
              default="tiktok", show_default=True)
def schedule_cadence(platform):
    """Show recommended posting cadence for a platform."""
    cadence = POSTING_CADENCE.get(platform, {"per_day": 1, "per_week": 7})
    output({"platform": platform, **cadence},
           f"Recommended {platform} cadence:")


# ── Theme Page ───────────────────────────────────────────────────────────

@cli.group(name="theme-page")
def theme_page():
    """Theme page tools — guide, niche selection, and account conversion."""
    pass


@theme_page.command("guide")
@click.option("--niche", "-n", default="", help="Filter tips for a specific niche")
@click.option("--output", "output_file", default=None, help="Save guide to JSON file")
@handle_error
def theme_page_guide(niche, output_file):
    """Complete theme page creation and monetization playbook."""
    guide = dict(THEME_PAGE_PLAYBOOK)

    if niche:
        # Inject niche-specific hashtag info
        try:
            from cli_anything.tiktok.utils.tiktok_backend import get_niche_hashtags
            tags = get_niche_hashtags(niche, limit=15)
            guide["niche_hashtags"] = {
                "niche": niche,
                "hashtags": [f"#{t}" for t in tags],
            }
        except Exception:
            pass

    if output_file:
        import pathlib
        pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)
        click.echo(f"✓ Playbook saved to {output_file}")
    else:
        output(guide, "\nTheme Page Complete Playbook:")


@theme_page.command("niches")
@click.option("--top", "-n", type=int, default=10, show_default=True)
def theme_page_niches(top):
    """List the highest-ROI niches for theme pages."""
    niches = THEME_PAGE_PLAYBOOK["niches_with_highest_roi"][:top]
    if _json_output:
        click.echo(json.dumps({"niches": niches, "count": len(niches)}))
    else:
        click.echo(f"Top {len(niches)} theme page niches by ROI:")
        for i, n in enumerate(niches, 1):
            click.echo(f"  {i:2d}. {n}")


@theme_page.command("convert")
@handle_error
def theme_page_convert():
    """Step-by-step guide for converting a personal brand to a theme page."""
    guide = THEME_PAGE_PLAYBOOK["conversion_from_personal_brand"]
    output(guide, "\nConverting Personal Brand → Theme Page:")


@theme_page.command("mistakes")
def theme_page_mistakes():
    """List common theme page mistakes to avoid."""
    mistakes = THEME_PAGE_PLAYBOOK["mistakes_to_avoid"]
    if _json_output:
        click.echo(json.dumps({"mistakes": mistakes}))
    else:
        click.echo("Common theme page mistakes to avoid:")
        for i, m in enumerate(mistakes, 1):
            click.echo(f"  {i:2d}. {m}")


# ── Content Calendar ─────────────────────────────────────────────────────

@cli.group(name="content")
def content():
    """Content planning tools — calendar generation."""
    pass


@content.command("calendar")
@click.option("--platform", "-p",
              type=click.Choice(list(POSTING_CADENCE.keys()), case_sensitive=False),
              default="tiktok", show_default=True)
@click.option("--niche", "-n", default="fitness", show_default=True)
@click.option("--days", "-d", type=int, default=30, show_default=True,
              help="Number of days to plan")
@click.option("--posts-per-day", type=int, default=None,
              help="Override default posts per day")
@click.option("--output", "output_file", default=None, help="Save calendar to JSON file")
@handle_error
def content_calendar(platform, niche, days, posts_per_day, output_file):
    """Generate a content calendar for your platform and niche."""
    calendar = generate_content_calendar(
        platform=platform, niche=niche, days=days,
        posts_per_day=posts_per_day or 0
    )
    result = {
        "platform": platform,
        "niche": niche,
        "days": days,
        "total_posts": len(calendar),
        "calendar": calendar,
    }
    if output_file:
        import pathlib
        pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"✓ Calendar saved to {output_file} ({len(calendar)} posts planned)")
    else:
        output(result, f"\n✓ Generated {len(calendar)}-post calendar for {platform} / {niche}:")


# ── Hashtag Strategy ─────────────────────────────────────────────────────

@cli.group()
def hashtag():
    """Hashtag strategy — platform rules and niche packs."""
    pass


@hashtag.command("strategy")
@click.argument("niche")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              default="tiktok", show_default=True)
@handle_error
def hashtag_strategy(niche, platform):
    """Build a complete hashtag strategy for a niche and platform."""
    rules = get_hashtag_rules(platform)

    # Get niche-specific hashtags
    try:
        from cli_anything.tiktok.utils.tiktok_backend import suggest_hashtags_strategy
        niche_packs = suggest_hashtags_strategy(niche)
    except (ImportError, AttributeError):
        from cli_anything.tiktok.utils.tiktok_backend import get_niche_hashtags
        tags = get_niche_hashtags(niche, limit=30)
        niche_packs = {"all_hashtags": [f"#{t}" for t in tags]}

    result = {
        "niche": niche,
        "platform": platform,
        "platform_rules": rules,
        "hashtag_pack": niche_packs,
    }
    output(result, f"\n✓ Hashtag strategy for #{niche} on {platform}:")


@hashtag.command("rules")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"], case_sensitive=False),
              default="tiktok", show_default=True)
def hashtag_rules(platform):
    """Show hashtag best practices for a platform."""
    rules = get_hashtag_rules(platform)
    output(rules, f"\nHashtag rules for {platform}:")


# ── Report ───────────────────────────────────────────────────────────────

@cli.group()
def report():
    """Reporting — trend synthesis and account overview."""
    pass


@report.command("combined")
@click.option("--tiktok-file", default=None,
              help="Path to TikTok trends JSON (from: cli-anything-tiktok trends report)")
@click.option("--youtube-file", default=None,
              help="Path to YouTube trends JSON (from: cli-anything-youtube trends fetch)")
@click.option("--niche", "-n", default="")
@click.option("--output", "output_file", default=None)
@handle_error
def report_combined(tiktok_file, youtube_file, niche, output_file):
    """Combine TikTok and YouTube trend data into a cross-platform report."""
    from cli_anything.social_optimizer.utils.optimizer_backend import build_combined_report

    tt_data = None
    yt_data = None

    if tiktok_file:
        with open(tiktok_file) as f:
            tt_data = json.load(f)
    if youtube_file:
        with open(youtube_file) as f:
            yt_data = json.load(f)

    result = build_combined_report(tiktok_data=tt_data, youtube_data=yt_data, niche=niche)

    if output_file:
        import pathlib
        pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2, default=str)
        click.echo(f"✓ Combined report saved to {output_file}")
    else:
        output(result, "\n✓ Combined Trend Report:")


@report.command("accounts")
def report_accounts():
    """Show summary of all registered accounts."""
    accounts = list_accounts()
    if not accounts:
        click.echo("No accounts registered. Run: account add <platform> <handle>")
        return
    output({
        "total_accounts": len(accounts),
        "by_platform": _group_by(accounts, "platform"),
        "accounts": accounts,
    }, f"Account Overview ({len(accounts)} total):")


def _group_by(items: list, key: str) -> dict:
    result: dict = {}
    for item in items:
        k = item.get(key, "unknown")
        result.setdefault(k, []).append(item.get("handle", ""))
    return result


# ── Config ──────────────────────────────────────────────────────────────

@cli.group()
def config():
    """Configuration management."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key, value):
    """Set a config value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    output({"key": key, "value": value}, f"✓ Set {key}")


@config.command("get")
@click.argument("key", required=False)
def config_get(key):
    """Show config value(s)."""
    cfg = load_config()
    if key:
        output({"key": key, "value": cfg.get(key)})
    else:
        output(cfg if cfg else {}, "Config:")


# ── REPL ─────────────────────────────────────────────────────────────────

@cli.command("repl", hidden=True)
def repl():
    """Enter interactive REPL mode."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
    skin = ReplSkin("social_optimizer", version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    commands = {
        "account add <platform> <handle>":          "Register an account",
        "account list":                             "List all accounts",
        "account audit <handle>":                   "Get optimization tips",
        "schedule best-times [--platform tiktok]":  "Best posting times",
        "theme-page guide [--niche fitness]":        "Full theme page playbook",
        "theme-page niches [--top 10]":              "Top ROI niches",
        "theme-page convert":                       "Convert personal brand guide",
        "theme-page mistakes":                      "Mistakes to avoid",
        "content calendar [--days 30]":             "Generate content calendar",
        "hashtag strategy <niche>":                 "Hashtag strategy by niche",
        "hashtag rules [--platform tiktok]":        "Platform hashtag rules",
        "report combined":                          "Cross-platform trend report",
        "report accounts":                          "Account overview",
        "help":                                     "Show this help",
        "quit / exit":                              "Exit REPL",
    }

    while True:
        try:
            line = skin.get_input(pt_session, context="social-optimizer")
        except (EOFError, KeyboardInterrupt):
            skin.print_goodbye()
            break

        if not line:
            continue
        if line in ("quit", "exit", "q"):
            skin.print_goodbye()
            break
        if line == "help":
            skin.help(commands)
            continue

        parts = line.split()
        try:
            cli.main(parts, standalone_mode=False)
        except SystemExit:
            pass
        except click.exceptions.UsageError as e:
            skin.error(str(e))
        except Exception as e:
            skin.error(str(e))


def main():
    cli()


if __name__ == "__main__":
    main()
