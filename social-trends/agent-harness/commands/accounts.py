"""accounts commands — audit and optimize social media accounts."""
import json
import click
from ..utils.account_optimizer import (
    full_account_audit,
    monetization_readiness,
    project_growth,
    calculate_engagement_rate,
    OPTIMAL_TIMES,
)
from ..utils.tiktok_scraper import fetch_user_stats as tt_user_stats


def _out(data, fmt):
    if fmt == "json":
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        _pretty_audit(data)


def _pretty_audit(audit: dict):
    p = audit.get("platform", "?").upper()
    click.echo(f"\n{'='*60}")
    click.echo(f"  ACCOUNT AUDIT — {p}")
    click.echo(f"{'='*60}")
    click.echo(f"  Overall Score:   {audit.get('overall_score', 0):.1f} / 100")
    click.echo(f"  Phase:           {audit.get('phase', '').upper()} — {audit.get('phase_description', '')}")
    click.echo(f"  Engagement Rate: {audit.get('engagement_rate', 0):.2f}%  "
               f"({audit.get('engagement_health', {}).get('level', '?')})")
    click.echo(f"  FF Ratio:        {audit.get('ff_ratio', 0):.2f}  ({audit.get('ff_advice', '')})")
    if audit.get("reach_rate_pct") is not None:
        click.echo(f"  Reach Rate:      {audit.get('reach_rate_pct', 0):.1f}%")
    click.echo(f"  Posting Freq:    {audit.get('posting_frequency', '?')}")

    click.echo(f"\n  Best Posting Times (EST):")
    for t in audit.get("optimal_times", []):
        click.echo(f"    {t['day']:<12} {t['hours']}  (score: {t['score']})")

    actions = audit.get("priority_actions", [])
    if actions:
        click.echo(f"\n  Priority Actions:")
        for i, a in enumerate(actions, 1):
            click.echo(f"    {i}. {a}")
    click.echo(f"{'='*60}\n")


@click.group()
def accounts():
    """Audit and optimize your social media accounts."""


@accounts.command("audit")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--followers", type=int, required=True)
@click.option("--following", type=int, default=0)
@click.option("--avg-likes", type=int, default=0)
@click.option("--avg-comments", type=int, default=0)
@click.option("--avg-shares", type=int, default=0)
@click.option("--avg-views", type=int, default=0)
@click.option("--post-frequency", type=float, default=1.0,
              help="Posts per week")
@click.option("--account-age-days", type=int, default=90)
@click.option("--niche", default=None)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def audit_cmd(platform, followers, following, avg_likes, avg_comments,
              avg_shares, avg_views, post_frequency, account_age_days, niche, fmt):
    """Run a full account health audit."""
    stats = {
        "followers":        followers,
        "following":        following,
        "avg_likes":        avg_likes,
        "avg_comments":     avg_comments,
        "avg_shares":       avg_shares,
        "avg_views":        avg_views,
        "post_frequency":   post_frequency,
        "account_age_days": account_age_days,
        "niche":            niche,
    }
    audit = full_account_audit(stats, platform)
    _out(audit, fmt)


@accounts.command("tiktok-stats")
@click.argument("username")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def tiktok_stats_cmd(username, fmt):
    """Fetch public TikTok account stats and run audit."""
    click.echo(f"Fetching stats for @{username}…", err=True)
    stats = tt_user_stats(username)
    if "error" in stats:
        click.echo(f"Error: {stats['error']}", err=True)
        return

    click.echo(f"  Username:  @{stats.get('username', username)}")
    click.echo(f"  Followers: {stats.get('followers', 0):,}")
    click.echo(f"  Following: {stats.get('following', 0):,}")
    click.echo(f"  Likes:     {stats.get('likes', 0):,}")
    click.echo(f"  Videos:    {stats.get('video_count', stats.get('videos', 0)):,}")
    click.echo(f"  URL:       {stats.get('url', '')}")

    if fmt == "json":
        click.echo(json.dumps(stats, indent=2, default=str))


@accounts.command("monetize")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--followers", type=int, required=True)
@click.option("--engagement-rate", type=float, required=True,
              help="Current engagement rate as percentage (e.g. 3.5)")
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def monetize_cmd(platform, followers, engagement_rate, fmt):
    """Check monetization readiness for each revenue tier."""
    result = monetization_readiness(followers, engagement_rate, platform)
    if fmt == "json":
        click.echo(json.dumps(result, indent=2))
        return

    click.echo(f"\n  Monetization Readiness — {platform.upper()} ({followers:,} followers, {engagement_rate}% ER)")
    click.echo("  " + "-" * 58)
    for tier, info in result.items():
        status = "READY" if info["ready"] else f"{info['progress_pct']}% there"
        click.echo(f"  {tier:<28} {status:<12} {info['requires']}")
        if info.get("note"):
            click.echo(f"  {'':28} Note: {info['note']}")
    click.echo()


@accounts.command("project-growth")
@click.option("--followers", type=int, required=True)
@click.option("--weekly-gain", type=int, required=True,
              help="Current average weekly follower gain")
@click.option("--weeks", type=int, default=12, show_default=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def project_growth_cmd(followers, weekly_gain, weeks, fmt):
    """Project follower count growth over N weeks."""
    projections = project_growth(followers, weekly_gain, weeks)
    if fmt == "json":
        click.echo(json.dumps(projections, indent=2))
        return
    click.echo(f"  Week  Followers      Gain")
    click.echo("  " + "-" * 30)
    for p in projections:
        click.echo(f"  {p['week']:<5} {p['followers']:>12,}  +{p['gain']:,}")


@accounts.command("best-times")
@click.option("--platform", "-p",
              type=click.Choice(["tiktok", "youtube", "instagram"]),
              required=True)
@click.option("--format", "-f", "fmt",
              type=click.Choice(["table", "json"]), default="table", show_default=True)
def best_times_cmd(platform, fmt):
    """Show optimal posting times for a platform."""
    times = OPTIMAL_TIMES.get(platform, [])
    if fmt == "json":
        click.echo(json.dumps(times, indent=2))
        return
    click.echo(f"\n  Best Posting Times for {platform.upper()} (EST):")
    click.echo("  " + "-" * 40)
    for t in times:
        click.echo(f"  {t['day']:<12} {t['hours']:<14} Score: {t['score']}")
    click.echo()
