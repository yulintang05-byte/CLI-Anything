"""
CLI-Anything Social Manager
─────────────────────────────────────────────
Viral trend scraping, account optimization, and theme page playbook.

Usage:
  cli-anything-social trends tiktok
  cli-anything-social trends youtube
  cli-anything-social trends report
  cli-anything-social optimize hashtags --niche finance --platform tiktok
  cli-anything-social optimize schedule --platform tiktok
  cli-anything-social optimize profile --platform tiktok --handle @mypage --niche finance
  cli-anything-social theme guide
  cli-anything-social theme niches
  cli-anything-social theme monetize
  cli-anything-social theme tools
  cli-anything-social accounts add --platform tiktok --handle @mypage --niche finance
  cli-anything-social accounts list
  cli-anything-social config set youtube_api_key YOUR_KEY
  cli-anything-social config show
"""
import json
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from cli_anything.social_manager.core import trends as trends_core
from cli_anything.social_manager.core import optimizer as opt_core
from cli_anything.social_manager.core import theme_pages as theme_core
from cli_anything.social_manager.utils import config as cfg

console = Console()


def _json_or_rich(data, json_flag: bool):
    if json_flag:
        click.echo(json.dumps(data, indent=2, default=str))
    return data


# ─────────────────────────────────────────────────────────────
# Root CLI
# ─────────────────────────────────────────────────────────────
@click.group()
@click.option("--json", "json_out", is_flag=True, default=False, help="Output raw JSON (for agents)")
@click.pass_context
def cli(ctx, json_out):
    """CLI-Anything Social Manager — viral trends, account optimization, theme pages."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = json_out


# ─────────────────────────────────────────────────────────────
# TRENDS group
# ─────────────────────────────────────────────────────────────
@cli.group()
def trends():
    """Fetch viral trends from TikTok and YouTube."""


@trends.command("tiktok")
@click.option("--region", default="US", show_default=True, help="Region code e.g. US, UK, AU")
@click.option("--period", default=7, show_default=True, type=click.Choice(["7", "30", "120"]), help="Trend period in days")
@click.option("--limit", default=15, show_default=True, help="Number of results")
@click.pass_context
def trends_tiktok(ctx, region, period, limit):
    """Show trending TikTok hashtags and viral sounds."""
    data = trends_core.get_tiktok_trends(region=region, period=int(period), limit=limit)
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit(
        f"[bold magenta]TikTok Viral Trends[/] · Region: [cyan]{region}[/] · Period: [cyan]{period}d[/]",
        border_style="magenta",
    ))

    # Hashtags table
    ht = Table(title="🔥 Trending Hashtags", box=box.ROUNDED, border_style="magenta")
    ht.add_column("Rank", style="cyan", width=6)
    ht.add_column("Hashtag", style="bold white")
    ht.add_column("Views", style="green", justify="right")
    ht.add_column("Posts", style="yellow", justify="right")
    ht.add_column("Trend", style="red")
    for h in data["trending_hashtags"]:
        ht.add_row(
            str(h.get("rank", "")),
            h["hashtag"],
            f"{h['view_count']:,}",
            f"{h['post_count']:,}",
            h.get("trend", ""),
        )
    console.print(ht)

    # Sounds table
    st = Table(title="🎵 Trending Sounds / Music", box=box.ROUNDED, border_style="cyan")
    st.add_column("Rank", style="cyan", width=6)
    st.add_column("Title", style="bold white")
    st.add_column("Artist", style="magenta")
    st.add_column("Used In", style="green", justify="right")
    for s in data["trending_sounds"]:
        st.add_row(
            str(s.get("rank", "")),
            s["title"],
            s["artist"],
            f"{s['usage_count']:,} videos",
        )
    console.print(st)
    console.print(f"\n[dim]Fetched: {data['fetched_at']}[/]")


@trends.command("youtube")
@click.option("--region", default="US", show_default=True)
@click.option("--category", default="", help="Category ID (10=Music, 24=Entertainment, leave blank for all)")
@click.option("--limit", default=20, show_default=True)
@click.pass_context
def trends_youtube(ctx, region, category, limit):
    """Show trending YouTube videos, hashtags, and music."""
    data = trends_core.get_youtube_trends(region=region, category=category, max_results=limit)
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2, default=str))
        return

    console.print(Panel.fit(
        f"[bold red]YouTube Viral Trends[/] · Region: [cyan]{region}[/]",
        border_style="red",
    ))

    if "error" in data:
        console.print(f"[red]Error:[/] {data['error']}")
        return

    # Topics
    if "trending_topics" in data:
        console.print(Panel(
            "\n".join(f"• {t}" for t in data["trending_topics"]),
            title="[bold]📈 Trending Topics (June 2026)[/]",
            border_style="red",
        ))

    # Hashtags
    ht = Table(title="# Top YouTube Hashtags", box=box.ROUNDED, border_style="red")
    ht.add_column("Hashtag", style="bold white")
    ht.add_column("Frequency", style="green", justify="right")
    for tag, count in (data.get("top_hashtags") or [])[:15]:
        ht.add_row(tag, str(count))
    console.print(ht)

    # Music
    if "trending_music" in data:
        mt = Table(title="🎵 Trending Music", box=box.ROUNDED, border_style="yellow")
        mt.add_column("Title", style="bold white")
        mt.add_column("Artist", style="magenta")
        mt.add_column("Trend Context", style="cyan")
        for m in data["trending_music"]:
            mt.add_row(m.get("title", ""), m.get("artist", ""), m.get("trend", ""))
        console.print(mt)

    # Full video list if available
    if "trending_videos" in data:
        vt = Table(title="📹 Trending Videos", box=box.ROUNDED, border_style="green")
        vt.add_column("Title", style="white", max_width=40)
        vt.add_column("Channel", style="cyan")
        vt.add_column("Views", style="green", justify="right")
        vt.add_column("Likes", style="yellow", justify="right")
        for v in data["trending_videos"][:10]:
            vt.add_row(v["title"][:40], v["channel"], f"{v['views']:,}", f"{v['likes']:,}")
        console.print(vt)

    if "note" in data:
        console.print(f"\n[yellow]Note:[/] {data['note']}")


@trends.command("report")
@click.option("--region", default="US", show_default=True)
@click.pass_context
def trends_report(ctx, region):
    """Generate a full cross-platform viral intelligence report."""
    json_mode = ctx.obj.get("json")
    if not json_mode:
        console.print("[bold]Fetching viral intelligence report...[/]", end=" ")
    data = trends_core.generate_trend_report(region=region)
    if json_mode:
        click.echo(json.dumps(data, indent=2, default=str))
        return
    console.print("[green]done[/]")

    console.print(Panel.fit(
        f"[bold]🌐 Cross-Platform Viral Intelligence Report[/]\nRegion: [cyan]{region}[/]  |  Date: [cyan]{data['report_date']}[/]",
        border_style="bright_white",
    ))

    ct = Table(title="🚀 Cross-Platform Trending Now", box=box.ROUNDED, border_style="bright_white")
    ct.add_column("Topic", style="bold white")
    for topic in data["cross_platform_trends"]:
        ct.add_row(topic)
    console.print(ct)

    console.print("\n[bold magenta]TikTok Snapshot[/]")
    for h in data["tiktok"]["trending_hashtags"][:5]:
        console.print(f"  {h['hashtag']} — [green]{h['view_count']:,}[/] views")

    console.print("\n[bold red]YouTube Snapshot[/]")
    for tag, count in (data["youtube"].get("top_hashtags") or [])[:5]:
        console.print(f"  {tag} — [green]{count}[/] occurrences")

    console.print(f"\n[dim]Run 'cli-anything-social trends tiktok' or 'trends youtube' for full data.[/]")


# ─────────────────────────────────────────────────────────────
# OPTIMIZE group
# ─────────────────────────────────────────────────────────────
@cli.group()
def optimize():
    """Optimize hashtags, posting schedule, and account profile."""


@optimize.command("hashtags")
@click.option("--niche", required=True, help="Your content niche e.g. finance, fitness, travel")
@click.option("--platform", default="tiktok", show_default=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.pass_context
def optimize_hashtags(ctx, niche, platform):
    """Get an optimized hashtag strategy for your niche."""
    data = opt_core.get_hashtag_strategy(niche=niche, platform=platform)
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit(
        f"[bold]# Hashtag Strategy[/] · Niche: [cyan]{niche}[/] · Platform: [cyan]{platform}[/]",
        border_style="bright_green",
    ))
    console.print(f"[dim]{data['strategy']}[/]\n")

    for group, tags in data["tag_groups"].items():
        console.print(f"[bold]{group.upper()}:[/] {' '.join(tags)}")

    console.print(Panel(
        " ".join(data["recommended_set"]),
        title="[bold green]✅ Recommended Set (copy-paste ready)[/]",
        border_style="green",
    ))

    console.print("\n[bold]Tips:[/]")
    for tip in data["tips"]:
        console.print(f"  • {tip}")


@optimize.command("schedule")
@click.option("--platform", default="tiktok", show_default=True, type=click.Choice(["tiktok", "youtube", "instagram"]))
@click.option("--frequency", default="daily", show_default=True, type=click.Choice(["daily", "2x", "3x", "weekly"]))
@click.pass_context
def optimize_schedule(ctx, platform, frequency):
    """Get best posting times for your platform."""
    data = opt_core.get_posting_schedule(platform=platform, frequency=frequency)
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit(
        f"[bold]📅 Posting Schedule[/] · Platform: [cyan]{platform}[/]",
        border_style="cyan",
    ))
    console.print(f"[bold]Recommended frequency:[/] {data['recommended_frequency']}\n")

    st = Table(title="Best Posting Times (EST)", box=box.ROUNDED, border_style="cyan")
    st.add_column("Day", style="bold white", width=12)
    st.add_column("Best Times", style="green")
    for window in data["posting_windows_est"]:
        st.add_row(window["day"], " / ".join(window["times"]))
    console.print(st)

    console.print(f"\n[bold]Best days:[/] {', '.join(data['best_days'])}")
    console.print(f"[bold]Avoid:[/] {', '.join(data['worst_days'])}\n")
    console.print("[bold]Pro tips:[/]")
    for tip in data["pro_tips"]:
        console.print(f"  • {tip}")


@optimize.command("profile")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "facebook"]))
@click.option("--handle", required=True, help="Your account handle e.g. @mypage")
@click.option("--niche", required=True, help="Your content niche")
@click.pass_context
def optimize_profile(ctx, platform, handle, niche):
    """Get a profile audit and optimization checklist."""
    data = opt_core.generate_profile_audit(platform=platform, handle=handle, niche=niche)
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit(
        f"[bold]👤 Profile Audit[/] · {platform.title()} · {handle}",
        border_style="yellow",
    ))

    at = Table(title="Optimization Checklist", box=box.ROUNDED, border_style="yellow")
    at.add_column("Area", style="bold white", width=20)
    at.add_column("Action", style="cyan")
    for item in data["profile_checklist"]:
        at.add_row(item["item"], item["tip"])
    console.print(at)

    console.print(Panel(
        "\n".join(f"✅ {w}" for w in data["quick_wins"]),
        title="[bold green]Quick Wins — Do These Today[/]",
        border_style="green",
    ))


# ─────────────────────────────────────────────────────────────
# THEME PAGES group
# ─────────────────────────────────────────────────────────────
@cli.group()
def theme():
    """Theme page creation guide, niche selection, and monetization roadmap."""


@theme.command("guide")
@click.pass_context
def theme_guide(ctx):
    """Full step-by-step theme page setup guide."""
    data = theme_core.get_setup_guide()
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit(
        "[bold bright_white]📖 Theme Page Complete Setup Guide[/]",
        border_style="bright_white",
    ))
    console.print(Panel(
        data["overview"]["what_is_a_theme_page"],
        title="What is a Theme Page?",
        border_style="dim",
    ))

    for step in data["steps"]:
        console.print(f"\n[bold cyan]Step {step['step']}: {step['title']}[/]")
        for d in step["details"]:
            console.print(f"  • {d}")


@theme.command("niches")
@click.pass_context
def theme_niches(ctx):
    """Show the most profitable theme page niches for 2026."""
    data = theme_core.get_niche_recommendations()
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit("[bold]🎯 Top Theme Page Niches — 2026[/]", border_style="magenta"))
    nt = Table(box=box.ROUNDED, border_style="magenta")
    nt.add_column("Niche", style="bold white", width=22)
    nt.add_column("Platforms", style="cyan")
    nt.add_column("Revenue $$", style="green", justify="center")
    nt.add_column("Competition", style="yellow")
    nt.add_column("Why It Works", style="dim", max_width=40)
    for n in data:
        nt.add_row(
            n["niche"],
            ", ".join(n["platforms"]),
            n["revenue_potential"],
            n["competition"],
            n["why"],
        )
    console.print(nt)

    console.print("\n[bold]Content ideas by niche:[/]")
    for n in data:
        console.print(f"\n  [bold cyan]{n['niche']}[/]: {' | '.join(n['content_ideas'])}")


@theme.command("monetize")
@click.pass_context
def theme_monetize(ctx):
    """Show all monetization strategies with income ranges and how-to."""
    data = theme_core.get_monetization_breakdown()
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit("[bold green]💰 Monetization Strategies[/]", border_style="green"))
    mt = Table(box=box.ROUNDED, border_style="green")
    mt.add_column("Method", style="bold white", width=25)
    mt.add_column("Difficulty", style="yellow")
    mt.add_column("Timeline", style="cyan")
    mt.add_column("Income Potential", style="green")
    mt.add_column("How", style="dim", max_width=45)
    for m in data:
        mt.add_row(
            m["method"],
            m["difficulty"],
            m["timeline"],
            m["income_potential"],
            m["how"],
        )
    console.print(mt)


@theme.command("tools")
@click.pass_context
def theme_tools(ctx):
    """Show the full tool stack for content discovery, creation, scheduling, and analytics."""
    data = theme_core.get_tools_stack()
    if ctx.obj.get("json"):
        click.echo(json.dumps(data, indent=2))
        return

    console.print(Panel.fit("[bold]🛠️  Recommended Tool Stack[/]", border_style="blue"))
    for category, tools in data.items():
        console.print(f"\n[bold cyan]{category.replace('_', ' ').title()}[/]")
        for tool in tools:
            console.print(f"  • {tool}")


# ─────────────────────────────────────────────────────────────
# ACCOUNTS group
# ─────────────────────────────────────────────────────────────
@cli.group()
def accounts():
    """Manage your social media accounts."""


@accounts.command("add")
@click.option("--platform", required=True, type=click.Choice(["tiktok", "youtube", "instagram", "facebook", "x"]))
@click.option("--handle", required=True, help="Account handle e.g. @mypage")
@click.option("--niche", default="", help="Content niche")
@click.option("--notes", default="", help="Optional notes")
@click.pass_context
def accounts_add(ctx, platform, handle, niche, notes):
    """Add a social media account to track."""
    entry = cfg.add_account(platform=platform, handle=handle, niche=niche, notes=notes)
    if ctx.obj.get("json"):
        click.echo(json.dumps(entry, indent=2))
        return
    console.print(f"[green]✅ Added:[/] {platform.title()} {handle} (niche: {niche or 'unset'})")
    console.print("[dim]Run 'cli-anything-social accounts list' to see all accounts.[/]")


@accounts.command("list")
@click.pass_context
def accounts_list(ctx):
    """List all tracked accounts."""
    accs = cfg.load_accounts()
    if ctx.obj.get("json"):
        click.echo(json.dumps(accs, indent=2))
        return
    if not accs:
        console.print("[yellow]No accounts added yet. Use 'accounts add' to add one.[/]")
        return
    at = Table(title="📱 Your Social Accounts", box=box.ROUNDED)
    at.add_column("Platform", style="cyan")
    at.add_column("Handle", style="bold white")
    at.add_column("Niche", style="magenta")
    at.add_column("Notes", style="dim")
    for a in accs:
        at.add_row(a["platform"].title(), a["handle"], a.get("niche", ""), a.get("notes", ""))
    console.print(at)


# ─────────────────────────────────────────────────────────────
# CONFIG group
# ─────────────────────────────────────────────────────────────
@cli.group()
def config():
    """Manage API keys and configuration."""


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.pass_context
def config_set(ctx, key, value):
    """Set a config value. E.g.: config set youtube_api_key AIza..."""
    cfg.save_config({key: value})
    if ctx.obj.get("json"):
        click.echo(json.dumps({"key": key, "status": "saved"}))
        return
    console.print(f"[green]✅ Saved:[/] {key}")


@config.command("show")
@click.pass_context
def config_show(ctx):
    """Show current configuration (API keys masked)."""
    data = cfg.load_config()
    masked = {}
    for k, v in data.items():
        masked[k] = (v[:6] + "..." + v[-4:]) if len(str(v)) > 12 and "key" in k.lower() else v
    if ctx.obj.get("json"):
        click.echo(json.dumps(masked, indent=2))
        return
    if not data:
        console.print("[yellow]No config set. Use 'config set KEY VALUE' to add.[/]")
        return
    ct = Table(title="⚙️  Config", box=box.ROUNDED)
    ct.add_column("Key", style="cyan")
    ct.add_column("Value", style="white")
    for k, v in masked.items():
        ct.add_row(k, str(v))
    console.print(ct)


if __name__ == "__main__":
    cli()
