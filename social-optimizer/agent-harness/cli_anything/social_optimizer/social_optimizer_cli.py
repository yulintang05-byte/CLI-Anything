"""SocialOptimizer CLI — account optimization, posting strategy, and theme page engine.

Usage:
    python3 -m cli_anything.social_optimizer [--json] <command>
    python3 -m cli_anything.social_optimizer  (launches REPL)
"""

import json
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything.social_optimizer.core import config as config_mod
from cli_anything.social_optimizer.core import accounts as accounts_mod
from cli_anything.social_optimizer.core import schedule as schedule_mod
from cli_anything.social_optimizer.core import strategy as strategy_mod
from cli_anything.social_optimizer.core import theme_page as theme_mod

# ── Global state ──────────────────────────────────────────────────────────────

_json_output: bool = False
_repl_mode: bool = False


# ── Output helpers ─────────────────────────────────────────────────────────────

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
            click.echo(f"{pad}{k}: [{len(v)} items]")
        else:
            click.echo(f"{pad}{k}: {v}")


def _print_list(lst: list) -> None:
    if not lst:
        click.echo("  (empty)")
        return
    for item in lst:
        if isinstance(item, dict):
            parts = [f"{k}={v}" for k, v in item.items() if not isinstance(v, (dict, list))]
            click.echo("  " + "  ".join(parts))
        else:
            click.echo(f"  {item}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}), err=True)
    else:
        click.echo(f"Error: {msg}", err=True)


def handle_error(func):
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (RuntimeError, ValueError, KeyError, FileNotFoundError) as e:
            _err(str(e))
            if not _repl_mode:
                sys.exit(1)
        except Exception as e:
            _err(f"Unexpected error: {e}")
            if not _repl_mode:
                sys.exit(1)

    return wrapper


# ── Root CLI ───────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.version_option("1.0.0", prog_name="social-optimizer")
@click.pass_context
def cli(ctx: click.Context, use_json: bool) -> None:
    """SocialOptimizer — optimize accounts, build posting strategy, and master theme pages.

    Manage all your social accounts, get platform-specific optimization checklists,
    build viral content strategies, generate posting schedules, and learn the full
    theme page creation and conversion framework.

    \b
    Quick start:
      social-optimizer account add --name "Fitness Page" --platform tiktok --handle fitdaily --niche fitness
      social-optimizer account optimize --platform tiktok --niche fitness
      social-optimizer strategy viral --niche fitness --platform tiktok
      social-optimizer schedule generate --platform tiktok --posts-per-day 3
      social-optimizer theme-page guide
      social-optimizer theme-page niche fitness
    """
    global _json_output
    _json_output = use_json
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)


# ── account group ─────────────────────────────────────────────────────────────

@cli.group()
def account():
    """Manage and optimize social media accounts."""
    pass


@account.command("add")
@click.option("--name", required=True, help="Account display name")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]),
              help="Platform")
@click.option("--handle", required=True, help="Account handle/username (without @)")
@click.option("--niche", default=None, help="Content niche (fitness, food, gaming, etc.)")
@click.option("--notes", default=None, help="Optional notes")
@handle_error
def account_add(name: str, platform: str, handle: str, niche: Optional[str], notes: Optional[str]) -> None:
    """Add a social media account to track and optimize."""
    result = config_mod.add_account(name=name, platform=platform, handle=handle, niche=niche, notes=notes)
    output(result, f"Added account @{handle} on {platform}")


@account.command("remove")
@click.argument("handle")
@click.option("--platform", default=None, help="Platform filter")
@handle_error
def account_remove(handle: str, platform: Optional[str]) -> None:
    """Remove an account."""
    result = config_mod.remove_account(handle, platform)
    output(result, f"Removed @{result['handle']} from {result['platform']}")


@account.command("list")
@click.option("--platform", default=None, help="Filter by platform")
@handle_error
def account_list(platform: Optional[str]) -> None:
    """List all tracked accounts."""
    accounts = config_mod.list_accounts(platform)
    if not _json_output:
        if not accounts:
            click.echo("  No accounts tracked. Use 'account add' to add one.")
            return
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Handle", "Platform", "Name", "Niche", "Notes"],
            [[a["handle"], a["platform"], a["name"][:25], a.get("niche", ""), a.get("notes", "")[:30]]
             for a in accounts]
        )
    else:
        output(accounts)


@account.command("optimize")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@click.option("--niche", default=None, help="Your content niche for niche-specific tips")
@handle_error
def account_optimize(platform: str, niche: Optional[str]) -> None:
    """Get full optimization checklist for a platform account."""
    result = accounts_mod.optimize_account(platform, niche)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        skin.section(f"Optimization Checklist — {platform.upper()}")
        if niche:
            click.echo(f"  Niche: {niche}\n")

        skin.section("High Priority (Do These First)")
        skin.table(
            ["Item", "What to do"],
            [[i["item"], i["detail"][:60]] for i in result["high_priority"]]
        )

        skin.section("Medium Priority")
        skin.table(
            ["Item", "What to do"],
            [[i["item"], i["detail"][:60]] for i in result["medium_priority"]]
        )

        if result["low_priority"]:
            skin.section("Low Priority")
            skin.table(
                ["Item", "What to do"],
                [[i["item"], i["detail"][:60]] for i in result["low_priority"]]
            )

        if result.get("niche_specific_tips"):
            skin.section(f"Niche Tips — {niche}")
            for tip in result["niche_specific_tips"]:
                click.echo(f"  → {tip.get('tip', '')}")
    else:
        output(result)


@account.command("audit-all")
@handle_error
def account_audit_all() -> None:
    """Run optimization audit across all tracked accounts."""
    accounts = config_mod.list_accounts()
    if not accounts:
        _err("No accounts tracked. Add accounts first with 'account add'.")
        return

    results = accounts_mod.audit_all_accounts(accounts)
    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.table(
            ["Handle", "Platform", "Niche", "High Priority Items", "Niche Tips"],
            [
                [
                    r.get("handle", ""),
                    r.get("platform", ""),
                    r.get("niche", ""),
                    str(r.get("high_priority_count", "")),
                    str(r.get("niche_tips_count", "")),
                ]
                for r in results
            ]
        )
    else:
        output(results)


# ── strategy group ────────────────────────────────────────────────────────────

@cli.group()
def strategy():
    """Viral content strategy and hook/CTA templates."""
    pass


@strategy.command("viral")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@handle_error
def strategy_viral(niche: str, platform: str) -> None:
    """Get viral content frameworks and a 7-day content plan for your niche."""
    frameworks = strategy_mod.get_viral_frameworks(niche)
    plan = strategy_mod.generate_content_plan(niche, platform)
    hooks = strategy_mod.get_hook_templates(niche, 5)
    ctas = strategy_mod.get_cta_templates(platform, niche)
    checklist = strategy_mod.viral_checklist(platform)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()

        skin.section("Viral Content Frameworks")
        for fw in frameworks[:5]:
            click.echo(f"\n  {fw['name']}")
            click.echo(f"    Structure: {fw['structure']}")
            click.echo(f"    Example:   {fw['example']}")

        skin.section("7-Day Content Plan")
        skin.table(
            ["Day", "Framework", "Content Type", "Suggested Hook"],
            [[
                p["day"],
                p["framework"],
                p["content_type"][:30],
                p["suggested_hook"][:40],
            ] for p in plan]
        )

        skin.section("Hook Templates")
        for i, h in enumerate(hooks, 1):
            click.echo(f"  {i}. {h}")

        skin.section("CTA Templates")
        for i, c in enumerate(ctas, 1):
            click.echo(f"  {i}. {c}")

        skin.section("Pre-Post Checklist")
        for item in checklist:
            click.echo(f"  ☐  {item['item']}")
            click.echo(f"       {item['check']}")
    else:
        output({
            "frameworks": frameworks,
            "7_day_plan": plan,
            "hook_templates": hooks,
            "cta_templates": ctas,
            "viral_checklist": checklist,
        })


@strategy.command("hooks")
@click.option("--niche", required=True, help="Your content niche")
@click.option("--count", default=10, show_default=True, type=int)
@handle_error
def strategy_hooks(niche: str, count: int) -> None:
    """Get scroll-stopping hook templates for your niche."""
    hooks = strategy_mod.get_hook_templates(niche, count)
    if not _json_output:
        click.echo(f"\n  Hook templates for niche: {niche}\n")
        for i, h in enumerate(hooks, 1):
            click.echo(f"  {i:2}. {h}")
    else:
        output(hooks)


@strategy.command("cta")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@click.option("--niche", default="content", show_default=True)
@click.option("--handle", default="you", show_default=True, help="Your handle")
@handle_error
def strategy_cta(platform: str, niche: str, handle: str) -> None:
    """Get CTA (call-to-action) templates for a platform."""
    ctas = strategy_mod.get_cta_templates(platform, niche, handle)
    if not _json_output:
        click.echo(f"\n  CTA templates for {platform} [{niche}]\n")
        for i, c in enumerate(ctas, 1):
            click.echo(f"  {i}. {c}")
    else:
        output(ctas)


@strategy.command("checklist")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@handle_error
def strategy_checklist(platform: str) -> None:
    """Get pre-post viral checklist for a platform."""
    checklist = strategy_mod.viral_checklist(platform)
    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        click.echo(f"\n  Pre-post checklist for {platform.upper()}\n")
        for item in checklist:
            click.echo(f"  ☐  {item['item']}")
            click.echo(f"       → {item['check']}")
            click.echo()
    else:
        output(checklist)


# ── schedule group ────────────────────────────────────────────────────────────

@cli.group()
def schedule():
    """Posting schedule optimization."""
    pass


@schedule.command("best-times")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@handle_error
def schedule_best_times(platform: str) -> None:
    """Show best posting times for a platform."""
    times = schedule_mod.get_best_times(platform)
    advice = schedule_mod.schedule_frequency_advice(platform)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Best Posting Times — {platform.upper()}")
        skin.table(
            ["Day", "Best Times"],
            [[day.capitalize(), ", ".join(hours)] for day, hours in times.items()]
        )
        skin.section("Frequency Advice")
        click.echo(f"  Weekly target:  {advice['weekly_target']}")
        click.echo(f"  Optimal/day:    {advice['optimal_posts_per_day']}")
        click.echo(f"  Note:           {advice['note']}")
        click.echo(f"\n  Content mix:")
        for item in advice.get("content_mix", []):
            click.echo(f"    • {item}")
    else:
        output({"best_times": times, "frequency_advice": advice})


@schedule.command("generate")
@click.option("--platform", required=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "twitter", "facebook"]))
@click.option("--posts-per-day", default=1, show_default=True, type=int)
@click.option("--timezone", default="US/Eastern", show_default=True)
@handle_error
def schedule_generate(platform: str, posts_per_day: int, timezone: str) -> None:
    """Generate a weekly posting schedule."""
    sched = schedule_mod.generate_schedule(platform, posts_per_day, timezone)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Weekly Posting Schedule — {platform.upper()} ({posts_per_day}×/day)")
        skin.table(
            ["Day", "Time", "TZ", "Post Type"],
            [[s["day"], s["time"], s["timezone"], s["post_type"][:40]] for s in sched]
        )
        click.echo(f"\n  Total weekly posts: {len(sched)}")
    else:
        output(sched)


# ── theme-page group ──────────────────────────────────────────────────────────

@cli.group("theme-page")
def theme_page_group():
    """Theme page creation, niche research, and monetization."""
    pass


@theme_page_group.command("guide")
@click.option("--phase", default=None, type=int, help="Show a specific phase (1-6)")
@handle_error
def theme_page_guide(phase: Optional[int]) -> None:
    """Full step-by-step theme page creation guide (all 6 phases)."""
    guide = theme_mod.get_creation_guide(phase)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        for p in guide:
            skin.section(f"Phase {p['phase']}: {p['title']}  [{p['time_estimate']}]")
            for i, step in enumerate(p["steps"], 1):
                click.echo(f"  {i}. {step}")
        click.echo()
    else:
        output(guide)


@theme_page_group.command("niche")
@click.argument("keyword")
@handle_error
def theme_page_niche(keyword: str) -> None:
    """Research a niche for theme page potential."""
    data = theme_mod.niche_research(keyword)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section(f"Niche Research: {keyword.capitalize()}")
        for k, v in data.items():
            if k == "keyword":
                continue
            if isinstance(v, list):
                click.echo(f"  {k}:")
                for item in v:
                    click.echo(f"    • {item}")
            else:
                click.echo(f"  {k}: {v}")
    else:
        output(data)


@theme_page_group.command("list-niches")
@click.option("--min-monetization", default=0, show_default=True, type=int,
              help="Filter by minimum monetization score (1-10)")
@handle_error
def theme_page_list_niches(min_monetization: int) -> None:
    """List all tracked niches ranked by monetization potential."""
    niches = theme_mod.list_niches(min_monetization)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Niches by Monetization Potential")
        skin.table(
            ["Niche", "Demand", "Competition", "$$$ Score", "Avg CPM", "Speed", "Platforms"],
            [
                [n["niche"], n["demand"], n["competition"],
                 str(n["monetization"]) + "/10", n["avg_cpm"],
                 n["growth_speed"], n["platforms"][:30]]
                for n in niches
            ]
        )
    else:
        output(niches)


@theme_page_group.command("convert")
@handle_error
def theme_page_convert() -> None:
    """Learn the full follower → buyer conversion funnel for theme pages."""
    guide = theme_mod.get_converting_guide()

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Theme Page Conversion Funnel")
        for stage in guide:
            click.echo(f"\n  ── {stage['stage']} ──")
            for tactic in stage["tactics"]:
                click.echo(f"    → {tactic}")
        click.echo()
    else:
        output(guide)


@theme_page_group.command("monetize")
@click.option("--niche", default=None, help="Filter strategies by niche")
@handle_error
def theme_page_monetize(niche: Optional[str]) -> None:
    """Monetization strategies for theme pages."""
    strategies = theme_mod.monetization_strategies(niche)

    if not _json_output:
        from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
        skin = ReplSkin()
        skin.section("Monetization Strategies" + (f" — {niche}" if niche else ""))
        for s in strategies:
            click.echo(f"\n  {s['strategy']}")
            click.echo(f"    {s['description']}")
            click.echo(f"    Entry:   {s['entry_point']}")
            click.echo(f"    Revenue: {s['revenue_range']}")
            if s.get("recommended_for_niche"):
                click.echo(f"    ★ Recommended for {niche} niche")
        click.echo()
    else:
        output(strategies)


# ── REPL ──────────────────────────────────────────────────────────────────────

@cli.command()
def repl() -> None:
    """Start an interactive SocialOptimizer REPL."""
    global _repl_mode
    _repl_mode = True

    from cli_anything.social_optimizer.utils.repl_skin import ReplSkin
    skin = ReplSkin(version="1.0.0")
    skin.print_banner()

    pt_session = skin.create_prompt_session()

    _repl_commands = {
        "account add --name <n> --platform <p> --handle <h>": "Add an account",
        "account list [--platform <p>]": "List tracked accounts",
        "account optimize --platform <p> --niche <n>": "Optimization checklist",
        "account audit-all": "Audit all accounts",
        "strategy viral --niche <n> --platform <p>": "Viral content plan",
        "strategy hooks --niche <n>": "Hook templates",
        "strategy cta --platform <p> --niche <n>": "CTA templates",
        "strategy checklist --platform <p>": "Pre-post viral checklist",
        "schedule best-times --platform <p>": "Best posting times",
        "schedule generate --platform <p> --posts-per-day N": "Generate weekly schedule",
        "theme-page guide [--phase N]": "Theme page creation guide",
        "theme-page niche <keyword>": "Research a niche",
        "theme-page list-niches": "All niches ranked by monetization",
        "theme-page convert": "Follower → buyer conversion guide",
        "theme-page monetize [--niche <n>]": "Monetization strategies",
        "help": "Show this help",
        "quit / exit": "Exit the REPL",
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


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    cli()


if __name__ == "__main__":
    main()
