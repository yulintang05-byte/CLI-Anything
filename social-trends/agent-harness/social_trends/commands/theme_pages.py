"""theme-pages commands — create, plan, and optimize converting theme pages."""
import json
import click
from social_trends.utils.theme_page_engine import (
    list_niches,
    launch_blueprint,
    generate_content_calendar,
    get_hook_templates,
    analyze_competitor,
    CONVERSION_STRATEGIES,
    NICHES,
)


def _out(data, fmt):
    if fmt == "json":
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        click.echo(json.dumps(data, indent=2, default=str))


@click.group("theme-pages")
def theme_pages():
    """Plan and optimize converting niche theme pages."""


@theme_pages.command("list-niches")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def list_niches_cmd(fmt):
    """List all available niches with stats."""
    niches = list_niches()
    if fmt == "json":
        click.echo(json.dumps(niches, indent=2))
        return
    click.echo(f"\n  {'Niche':<22} {'Saturation':<12} {'Growth':<18} {'Avg CPM':<10} Best Platforms")
    click.echo("  " + "-" * 80)
    for n in niches:
        plat = ", ".join(n["best_platforms"][:2])
        click.echo(f"  {n['niche']:<22} {n['saturation']:<12} {n['growth_speed']:<18} "
                   f"${n['avg_cpm_usd']:<9} {plat}")
    click.echo()


@theme_pages.command("blueprint")
@click.argument("niche", type=click.Choice(list(NICHES.keys())))
@click.option("--format", "-f", "fmt",
              type=click.Choice(["summary", "full", "json"]),
              default="summary", show_default=True)
def blueprint_cmd(niche, fmt):
    """Generate a full launch blueprint for a theme page niche."""
    click.echo(f"Generating launch blueprint for: {niche}…", err=True)
    bp = launch_blueprint(niche)

    if "error" in bp:
        click.echo(f"Error: {bp['error']}", err=True)
        return

    if fmt == "json":
        click.echo(json.dumps(bp, indent=2, default=str))
        return

    nd = bp["niche_data"]
    click.echo(f"\n{'='*65}")
    click.echo(f"  THEME PAGE LAUNCH BLUEPRINT — {niche.upper().replace('_', ' ')}")
    click.echo(f"{'='*65}")
    click.echo(f"\n  Description:    {nd['description']}")
    click.echo(f"  Saturation:     {nd['saturation']}")
    click.echo(f"  Growth Speed:   {nd['growth_speed']}")
    click.echo(f"  Best Platforms: {', '.join(nd['best_platforms'])}")
    click.echo(f"  Avg CPM:        ${nd['avg_cpm_usd']}/1000 views")

    click.echo(f"\n  Content Pillars:")
    for p in nd["content_pillars"]:
        click.echo(f"    • {p}")

    click.echo(f"\n  Viral Formula:")
    click.echo(f"    {bp['viral_formula']}")

    click.echo(f"\n  Hook Templates:")
    for h in nd["hook_templates"]:
        click.echo(f"    \"{h}\"")

    click.echo(f"\n  Week 1 Goals:")
    for g in bp["week1_goals"]:
        click.echo(f"    □ {g}")

    click.echo(f"\n  Week 2 Goals:")
    for g in bp["week2_goals"]:
        click.echo(f"    □ {g}")

    click.echo(f"\n  Month 1 Targets:")
    m1 = bp["month1_targets"]
    click.echo(f"    Min followers:    {m1['followers_min']:,}")
    click.echo(f"    Stretch:          {m1['followers_stretch']:,}")
    click.echo(f"    Posts:            {m1['posts']}")
    click.echo(f"    Engagement rate:  {m1['avg_engagement_pct']}%")

    click.echo(f"\n  Monetization Roadmap:")
    for m in bp["monetization_roadmap"]:
        click.echo(f"    {m['milestone']:<20} → {m['action']}")

    click.echo(f"\n  Monetization Methods:")
    for m in nd["monetization"]:
        click.echo(f"    • {m}")

    if fmt == "full":
        click.echo(f"\n  Content Calendar (First 2 Weeks):")
        click.echo(f"  {'Day':<5} {'Type':<20} {'Pillar':<25} Hook Example")
        click.echo("  " + "-" * 90)
        for e in bp["content_calendar"][:10]:
            hook = e['hook_example'][:40] + "…" if len(e['hook_example']) > 40 else e['hook_example']
            click.echo(f"  {e['day']:<5} {e['content_type']:<20} {e['content_pillar']:<25} {hook}")

        click.echo(f"\n  Conversion Strategies:")
        for cs in bp["conversion_strategies"]:
            click.echo(f"\n  [{cs['name']}]")
            click.echo(f"    {cs['description']}")
            click.echo(f"    Conversion: {cs['conversion_rate']}")
            for step in cs["steps"]:
                click.echo(f"    • {step}")

    click.echo(f"\n{'='*65}\n")


@theme_pages.command("calendar")
@click.argument("niche", type=click.Choice(list(NICHES.keys())))
@click.option("--frequency", "-f",
              type=click.Choice(["3x_week", "5x_week", "daily"]),
              default="5x_week", show_default=True)
@click.option("--weeks", "-w", default=4, show_default=True)
@click.option("--format", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def calendar_cmd(niche, frequency, weeks, fmt):
    """Generate a content posting calendar."""
    cal = generate_content_calendar(niche, frequency, weeks)
    if fmt == "json":
        click.echo(json.dumps(cal, indent=2))
        return
    click.echo(f"\n  Content Calendar — {niche} ({frequency}, {weeks} weeks)")
    click.echo(f"  {'Wk':<4} {'Day':<5} {'Type':<22} {'Pillar':<25} Hook")
    click.echo("  " + "-" * 95)
    for e in cal:
        hook = e['hook_example'][:35] + "…" if len(e['hook_example']) > 35 else e['hook_example']
        click.echo(f"  {e['week']:<4} {e['day']:<5} {e['content_type']:<22} "
                   f"{e['content_pillar']:<25} {hook}")
    click.echo()


@theme_pages.command("hooks")
@click.argument("niche", type=click.Choice(list(NICHES.keys())))
def hooks_cmd(niche):
    """Get viral hook templates for a niche."""
    hooks = get_hook_templates(niche)
    click.echo(f"\n  Viral Hook Templates for {niche}:")
    for i, h in enumerate(hooks, 1):
        click.echo(f"  {i}. \"{h}\"")
    click.echo()


@theme_pages.command("conversions")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["summary", "json"]), default="summary", show_default=True)
def conversions_cmd(fmt):
    """Show all conversion strategies with step-by-step implementation."""
    if fmt == "json":
        click.echo(json.dumps(CONVERSION_STRATEGIES, indent=2))
        return
    for cs in CONVERSION_STRATEGIES:
        click.echo(f"\n  [{cs['name']}]")
        click.echo(f"  {cs['description']}")
        click.echo(f"  Conversion Rate:       {cs['conversion_rate']}")
        click.echo(f"  Time to Implement:     {cs['time_to_implement']}")
        click.echo(f"  Steps:")
        for step in cs["steps"]:
            click.echo(f"    • {step}")
    click.echo()


@theme_pages.command("analyze-competitor")
@click.argument("username")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--followers", type=int, required=True)
@click.option("--avg-likes", type=int, default=0)
@click.option("--post-count", type=int, default=50)
@click.option("--account-age-days", type=int, default=90)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def analyze_competitor_cmd(username, platform, followers, avg_likes,
                            post_count, account_age_days, fmt):
    """Reverse-engineer a competitor's growth strategy."""
    stats = {
        "followers":        followers,
        "avg_likes":        avg_likes,
        "post_count":       post_count,
        "account_age_days": account_age_days,
    }
    result = analyze_competitor(username, platform, stats)
    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
        return
    click.echo(f"\n  Competitor Analysis: @{username} ({platform.upper()})")
    click.echo(f"  Followers:        {result['followers']:,}")
    click.echo(f"  Engagement Rate:  {result['engagement_rate']}%")
    click.echo(f"  Daily Growth:     +{result['daily_growth']:,.0f}/day")
    click.echo(f"  Posts/Day:        {result['posts_per_day']}")
    click.echo(f"\n  Insights:")
    for ins in result["insights"]:
        click.echo(f"    • {ins}")
    click.echo(f"\n  How to Replicate:")
    for r in result["replicate"]:
        click.echo(f"    → {r}")
    click.echo()
