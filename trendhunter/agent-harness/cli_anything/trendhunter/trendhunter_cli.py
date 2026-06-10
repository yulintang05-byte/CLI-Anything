"""TrendHunter CLI — viral trends, account optimization, and theme page playbooks.

Commands:
  trends fetch-all      — Scrape YouTube + TikTok for viral trends
  trends youtube        — YouTube trending only
  trends tiktok         — TikTok trending only
  trends analyze        — Cross-platform trend report
  trends music          — Trending music/sounds
  trends hashtags       — Recommended hashtag sets for a niche

  account optimize      — Full account optimization report
  account schedule      — Optimal posting schedule
  account tactics       — Engagement tactics playbook
  account growth        — Growth estimate projection
  account bio           — Bio formula templates

  theme analyze-niche   — Niche monetization analysis
  theme playbook        — Step-by-step growth playbook
  theme funnel          — Conversion funnel blueprint
  theme monetize        — Revenue stream breakdown
  theme cta             — CTA template library
  theme metrics         — Calculate conversion rates
"""

import json
import sys
import click

from cli_anything.trendhunter.__init__ import __version__
from cli_anything.trendhunter.utils.repl_skin import ReplSkin

skin = ReplSkin("trendhunter", version=__version__)


def _out(data, json_mode: bool):
    """Print either JSON or human-readable output."""
    if json_mode:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        return data  # callers handle human output


def _json_flag(f):
    return click.option("--json", "json_mode", is_flag=True,
                        help="Output as JSON")(f)


def _region_opt(f):
    return click.option("--region", default="US", show_default=True,
                        help="Region code (US, GB, AU, etc.)")(f)


# ═══════════════════════════════════════════════════════════════════════
# Root CLI
# ═══════════════════════════════════════════════════════════════════════

@click.group()
@click.version_option(__version__, prog_name="cli-anything-trendhunter")
def cli():
    """TrendHunter — viral trend scraping, account optimization & theme page playbooks."""
    pass


# ═══════════════════════════════════════════════════════════════════════
# trends group
# ═══════════════════════════════════════════════════════════════════════

@cli.group()
def trends():
    """Scrape and analyze viral trends on YouTube and TikTok."""
    pass


@trends.command("fetch-all")
@_region_opt
@click.option("--api-key", default="", envvar="YOUTUBE_API_KEY",
              help="YouTube Data API v3 key (optional — uses RSS if omitted)")
@click.option("--max", "max_results", default=25, show_default=True)
@_json_flag
def trends_fetch_all(region, api_key, max_results, json_mode):
    """Fetch trending content from both YouTube and TikTok."""
    from cli_anything.trendhunter.core.youtube_scraper import fetch_youtube_trends
    from cli_anything.trendhunter.core.tiktok_scraper import fetch_tiktok_trends
    from cli_anything.trendhunter.core.trend_analyzer import analyze_trends

    skin.print_banner()
    skin.info(f"Fetching YouTube trends ({region})…")
    yt = fetch_youtube_trends(region=region, max_results=max_results, api_key=api_key)

    skin.info("Fetching TikTok trends…")
    tt = fetch_tiktok_trends(region=region, max_hashtags=max_results)

    skin.info("Analyzing cross-platform trends…")
    report = analyze_trends(yt, tt)

    if json_mode:
        click.echo(json.dumps(report.to_dict(), indent=2))
        return

    skin.section("Top Cross-Platform Trends")
    rows = [[f"#{t.tag}", f"{t.score:.0f}/100",
             "/".join(t.platforms), ", ".join(t.niches) or "—"]
            for t in report.top_trends[:15]]
    skin.table(["Hashtag", "Score", "Platforms", "Niches"], rows)

    if report.trending_music:
        skin.section("Trending Music")
        music_rows = [[m.get("title","?"), m.get("source","?")]
                      for m in report.trending_music[:10]]
        skin.table(["Track", "Source"], music_rows)

    if report.viral_hooks:
        skin.section("Viral Hook Templates")
        for h in report.viral_hooks[:6]:
            skin.info(h)

    skin.success(f"Scraped {len(yt.videos)} YouTube videos, "
                 f"{len(tt.hashtags)} TikTok hashtags")


@trends.command("youtube")
@_region_opt
@click.option("--api-key", default="", envvar="YOUTUBE_API_KEY")
@click.option("--max", "max_results", default=25, show_default=True)
@_json_flag
def trends_youtube(region, api_key, max_results, json_mode):
    """Fetch YouTube trending videos and hashtags."""
    from cli_anything.trendhunter.core.youtube_scraper import fetch_youtube_trends

    skin.info(f"Fetching YouTube trending ({region}, source={'api' if api_key else 'rss'})…")
    yt = fetch_youtube_trends(region=region, max_results=max_results, api_key=api_key)

    if json_mode:
        click.echo(json.dumps(yt.to_dict(), indent=2))
        return

    skin.section(f"YouTube Trending — {region}")
    rows = [[v.title[:55], v.channel[:25], ", ".join(v.hashtags[:4]) or "—"]
            for v in yt.videos[:15]]
    skin.table(["Title", "Channel", "Hashtags"], rows)

    if yt.trending_hashtags:
        skin.section("Top Hashtags from Trending")
        skin.info("  " + "  ".join(f"#{t}" for t in yt.trending_hashtags[:15]))

    if yt.trending_music:
        skin.section("Trending on YouTube Music")
        for m in yt.trending_music[:8]:
            skin.status("  Track", m.get("title", "?"))

    skin.success(f"{len(yt.videos)} videos, {len(yt.trending_hashtags)} hashtags")


@trends.command("tiktok")
@_region_opt
@click.option("--max", "max_results", default=25, show_default=True)
@_json_flag
def trends_tiktok(region, max_results, json_mode):
    """Fetch TikTok trending hashtags and sounds."""
    from cli_anything.trendhunter.core.tiktok_scraper import fetch_tiktok_trends

    skin.info("Fetching TikTok trending hashtags and sounds…")
    tt = fetch_tiktok_trends(region=region, max_hashtags=max_results)

    if json_mode:
        click.echo(json.dumps(tt.to_dict(), indent=2))
        return

    skin.section(f"TikTok Trending Hashtags — {region}")
    rows = [[f"#{h.name}",
             _fmt_views(h.view_count),
             str(h.video_count) if h.video_count else "—"]
            for h in tt.hashtags[:20]]
    skin.table(["Hashtag", "Views", "Videos"], rows)

    if tt.sounds:
        skin.section("Trending Sounds")
        for s in tt.sounds[:8]:
            skin.info(f"  🎵 {s.name}")

    if tt.trending_creators:
        skin.section("Trending Creators to Study")
        skin.info("  " + "  @".join([""] + tt.trending_creators[:5]).strip())


@trends.command("hashtags")
@click.argument("niche")
@_region_opt
@click.option("--count", default=15, show_default=True)
@click.option("--mix/--no-mix", default=True, show_default=True,
              help="Use 30/30/30/10 hashtag strategy mix")
@_json_flag
def trends_hashtags(niche, region, count, mix, json_mode):
    """Get recommended hashtag set for a niche (strategy-mixed)."""
    from cli_anything.trendhunter.core.youtube_scraper import fetch_youtube_trends
    from cli_anything.trendhunter.core.tiktok_scraper import fetch_tiktok_trends
    from cli_anything.trendhunter.core.trend_analyzer import analyze_trends, get_recommended_hashtags

    skin.info(f"Building hashtag set for '{niche}' niche…")
    yt = fetch_youtube_trends(region=region, max_results=20)
    tt = fetch_tiktok_trends(region=region, max_hashtags=20)
    report = analyze_trends(yt, tt)
    tags = get_recommended_hashtags(niche, report, mix=mix, count=count)

    if json_mode:
        click.echo(json.dumps({"niche": niche, "hashtags": tags}, indent=2))
        return

    skin.section(f"Recommended Hashtags — {niche}")
    skin.info(" ".join(tags))
    skin.hint("\nStrategy: 30% mega-reach | 30% mid-tier | 30% niche | 10% branded")
    skin.hint("Tip: Rotate this set every 2 weeks to avoid shadowban")


@trends.command("music")
@_region_opt
@_json_flag
def trends_music(region, json_mode):
    """Get trending music and sounds across platforms."""
    from cli_anything.trendhunter.core.youtube_scraper import fetch_trending_music_yt
    from cli_anything.trendhunter.core.tiktok_scraper import fetch_trending_sounds_web

    skin.info("Fetching trending music…")
    yt_music = fetch_trending_music_yt(region)
    tt_sounds = fetch_trending_sounds_web(region)

    data = {
        "youtube_music": yt_music,
        "tiktok_sounds": [s.to_dict() for s in tt_sounds],
    }

    if json_mode:
        click.echo(json.dumps(data, indent=2))
        return

    skin.section("Trending on YouTube Music")
    for m in yt_music[:10]:
        skin.info(f"  ▶ {m.get('title','?')}")

    skin.section("Trending TikTok Sounds")
    for s in tt_sounds[:10]:
        skin.info(f"  🎵 {s.name}")

    skin.hint("\nTip: Use trending sounds within 24-48h of appearance for max algorithmic boost")


@trends.command("analyze")
@_region_opt
@_json_flag
def trends_analyze(region, json_mode):
    """Deep cross-platform trend analysis with niche opportunity map."""
    from cli_anything.trendhunter.core.youtube_scraper import fetch_youtube_trends
    from cli_anything.trendhunter.core.tiktok_scraper import fetch_tiktok_trends
    from cli_anything.trendhunter.core.trend_analyzer import analyze_trends

    skin.info("Running deep cross-platform analysis…")
    yt = fetch_youtube_trends(region=region)
    tt = fetch_tiktok_trends(region=region)
    report = analyze_trends(yt, tt)

    if json_mode:
        click.echo(json.dumps(report.to_dict(), indent=2))
        return

    skin.section("Cross-Platform Viral Trends")
    rows = [[f"#{t.tag}", f"{t.score:.0f}", t.recommendation[:50]]
            for t in report.cross_platform[:10]]
    skin.table(["Tag", "Score", "Recommendation"], rows)

    skin.section("Niche Opportunities")
    for niche, tags in list(report.niche_opportunities.items())[:8]:
        skin.status(f"  {niche.capitalize()}", " ".join(tags[:5]))

    skin.section("Viral Hooks")
    for hook in report.viral_hooks[:5]:
        skin.info(f'  "{hook}"')


# ═══════════════════════════════════════════════════════════════════════
# account group
# ═══════════════════════════════════════════════════════════════════════

@cli.group()
def account():
    """Optimize your social media accounts for maximum growth."""
    pass


@account.command("optimize")
@click.option("--platform", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "youtube", "instagram", "youtube_shorts"]))
@click.option("--niche", default="", help="Your content niche")
@click.option("--followers", default=0, help="Current follower count")
@click.option("--stage", default="starter",
              type=click.Choice(["starter", "growing", "scale"]))
@click.option("--timezone", default="us_east", show_default=True)
@_json_flag
def account_optimize(platform, niche, followers, stage, timezone, json_mode):
    """Generate a complete account optimization report."""
    from cli_anything.trendhunter.core.account_optimizer import (
        AccountProfile, optimize_account,
    )
    profile = AccountProfile(
        platform=platform, niche=niche, followers=followers,
        stage=stage, timezone=timezone,
    )
    report = optimize_account(profile)

    if json_mode:
        click.echo(json.dumps(report.to_dict(), indent=2))
        return

    skin.section(f"Account Optimization — {platform.title()}")
    skin.status("Niche",     niche or "(not set)")
    skin.status("Stage",     stage)
    skin.status("Followers", str(followers))

    skin.section("Optimal Posting Schedule")
    rows = [[s["time"], s["best_day"], s["note"]] for s in report.posting_schedule]
    skin.table(["Time", "Best Day", "Notes"], rows)

    skin.section(f"Post {report.recommended_frequency}x/week — Content Pillars")
    for i, p in enumerate(report.content_pillars, 1):
        skin.info(f"  {i}. {p}")

    skin.section("Hashtag Strategy")
    for k, v in report.hashtag_strategy.items():
        skin.status(f"  {k.title()}", v)

    skin.section("Growth Forecast")
    for k, v in report.growth_estimate.items():
        skin.status(f"  {k.replace('_', ' ').title()}", str(v))


@account.command("schedule")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram", "youtube_shorts"]))
@click.option("--timezone", default="us_east", show_default=True)
@_json_flag
def account_schedule(platform, timezone, json_mode):
    """Show optimal posting times for a platform."""
    from cli_anything.trendhunter.core.account_optimizer import get_posting_schedule
    schedule = get_posting_schedule(platform, timezone)

    if json_mode:
        click.echo(json.dumps(schedule, indent=2))
        return

    skin.section(f"Optimal Posting Schedule — {platform.title()}")
    rows = [[s["time"], s["best_day"], s["note"]] for s in schedule]
    skin.table(["Post Time", "Best Day", "Why"], rows)
    skin.hint(f"\nTimezone: {timezone} | Adjust ±1-2h based on your audience analytics")


@account.command("tactics")
@click.option("--platform", default=None,
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@_json_flag
def account_tactics(platform, json_mode):
    """Engagement tactics playbook for faster growth."""
    from cli_anything.trendhunter.core.account_optimizer import get_engagement_tactics
    tactics = get_engagement_tactics(platform)

    if json_mode:
        click.echo(json.dumps(tactics, indent=2))
        return

    plat_str = platform or "all platforms"
    skin.section(f"Engagement Tactics — {plat_str.title()}")
    for t in tactics:
        impact_icon = {"very_high": "🔥", "high": "⚡", "medium": "✅"}.get(t["impact"], "•")
        skin.info(f"  {impact_icon} {t['tactic']}")
        skin.hint(f"     Why: {t['why']}")


@account.command("growth")
@click.option("--followers", required=True, type=int)
@click.option("--stage", default="starter",
              type=click.Choice(["starter", "growing", "scale"]))
@click.option("--posts-per-week", default=3, show_default=True, type=int)
@_json_flag
def account_growth(followers, stage, posts_per_week, json_mode):
    """Project follower growth based on stage and posting frequency."""
    from cli_anything.trendhunter.core.account_optimizer import estimate_growth
    est = estimate_growth(followers, stage, posts_per_week)

    if json_mode:
        click.echo(json.dumps(est, indent=2))
        return

    skin.section("Growth Forecast")
    for k, v in est.items():
        skin.status(f"  {k.replace('_',' ').title()}", str(v))


@account.command("bio")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@_json_flag
def account_bio(platform, json_mode):
    """Bio formula templates optimized per platform."""
    from cli_anything.trendhunter.core.account_optimizer import get_bio_formulas
    formulas = get_bio_formulas(platform)

    if json_mode:
        click.echo(json.dumps({"platform": platform, "formulas": formulas}, indent=2))
        return

    skin.section(f"Bio Formulas — {platform.title()}")
    for i, f in enumerate(formulas, 1):
        skin.info(f"  {i}. {f}")
    skin.hint("\nTip: Add a niche emoji + 1 clear CTA linking to your Linktree/Beacons page")


# ═══════════════════════════════════════════════════════════════════════
# theme group
# ═══════════════════════════════════════════════════════════════════════

@cli.group()
def theme():
    """Theme page creation, conversion optimization, and monetization playbooks."""
    pass


@theme.command("analyze-niche")
@click.argument("niche")
@_json_flag
def theme_analyze_niche(niche, json_mode):
    """Analyze a niche's monetization potential, competition, and growth speed."""
    from cli_anything.trendhunter.core.theme_page import get_niche_analysis
    data = get_niche_analysis(niche)

    if json_mode:
        click.echo(json.dumps(data, indent=2))
        return

    skin.section(f"Niche Analysis — {niche.title()}")
    skip_keys = {"niche"}
    for k, v in data.items():
        if k in skip_keys:
            continue
        label = k.replace("_", " ").title()
        value = ", ".join(v) if isinstance(v, list) else str(v)
        skin.status(f"  {label}", value)


@theme.command("playbook")
@click.argument("niche")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@_json_flag
def theme_playbook(niche, platform, json_mode):
    """Step-by-step growth playbook for building a theme page from 0."""
    from cli_anything.trendhunter.core.theme_page import get_growth_playbook
    playbook = get_growth_playbook(niche, platform)

    if json_mode:
        click.echo(json.dumps(playbook, indent=2))
        return

    skin.section(f"Growth Playbook — {niche.title()} on {platform.title()}")
    for phase in playbook:
        skin.section(phase["phase"])
        for action in phase["actions"]:
            skin.info(f"  ☐ {action}")


@theme.command("funnel")
@click.argument("niche", default="")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@_json_flag
def theme_funnel(niche, platform, json_mode):
    """Full conversion funnel blueprint — from scroll to sale."""
    from cli_anything.trendhunter.core.theme_page import get_conversion_funnel
    funnel = get_conversion_funnel(niche, platform)

    if json_mode:
        click.echo(json.dumps(funnel.to_dict(), indent=2))
        return

    skin.section("Conversion Funnel Blueprint")
    for s in funnel.stages:
        skin.section(s["stage"])
        skin.status("  Goal", s["goal"])
        skin.status("  KPI",  s["kpi"])
        for tactic in s["tactics"]:
            skin.info(f"    ▸ {tactic}")

    skin.section("Link-in-Bio Tools")
    rows = [[t["tool"], t["best_for"]] for t in funnel.link_in_bio_tools]
    skin.table(["Tool", "Best For"], rows)


@theme.command("monetize")
@click.argument("niche", default="")
@_json_flag
def theme_monetize(niche, json_mode):
    """Revenue stream breakdown with effort/reward matrix."""
    from cli_anything.trendhunter.core.theme_page import get_monetization_strategies
    strategies = get_monetization_strategies(niche)

    if json_mode:
        click.echo(json.dumps(strategies, indent=2))
        return

    skin.section(f"Monetization Strategies — {niche.title() or 'All Niches'}")
    rows = [[s["method"], s["effort"], s["income_range"], s["timeline"]]
            for s in strategies]
    skin.table(["Method", "Effort", "Income Range", "Timeline"], rows)

    skin.section("Details")
    for s in strategies:
        skin.status(f"  {s['method']}", s["how"])


@theme.command("cta")
@click.argument("niche", default="")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "youtube", "instagram"]))
@_json_flag
def theme_cta(niche, platform, json_mode):
    """CTA template library — ready-to-use calls to action."""
    from cli_anything.trendhunter.core.theme_page import get_cta_templates
    templates = get_cta_templates(niche, platform)

    if json_mode:
        click.echo(json.dumps({"niche": niche, "platform": platform,
                               "templates": templates}, indent=2))
        return

    skin.section(f"CTA Templates — {platform.title()}")
    for i, t in enumerate(templates, 1):
        skin.info(f"  {i}. {t}")
    skin.hint("\nTip: Test 2-3 different CTAs per week and track which drives most link clicks")


@theme.command("metrics")
@click.option("--followers", required=True, type=int)
@click.option("--link-clicks", default=0, type=int)
@click.option("--sales", default=0, type=int)
@_json_flag
def theme_metrics(followers, link_clicks, sales, json_mode):
    """Calculate and benchmark your conversion rates."""
    from cli_anything.trendhunter.core.theme_page import calculate_conversion_rate
    data = calculate_conversion_rate(followers, link_clicks, sales)

    if json_mode:
        click.echo(json.dumps(data, indent=2))
        return

    skin.section("Conversion Metrics")
    for k, v in data.items():
        if isinstance(v, dict):
            skin.section(f"  {k.title()}")
            for bk, bv in v.items():
                skin.status(f"    {bk.replace('_',' ').title()}", str(bv))
        else:
            skin.status(f"  {k.replace('_',' ').title()}", str(v))


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

def _fmt_views(n: int) -> str:
    if n >= 1_000_000_000:
        return f"{n/1e9:.1f}B"
    if n >= 1_000_000:
        return f"{n/1e6:.0f}M"
    if n >= 1_000:
        return f"{n/1e3:.0f}K"
    return str(n) if n > 0 else "—"


if __name__ == "__main__":
    cli()
