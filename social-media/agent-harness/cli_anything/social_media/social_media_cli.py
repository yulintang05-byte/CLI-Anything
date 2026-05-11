"""cli-anything Social Media — main CLI entry point.

Commands:
  trends   Scrape YouTube / TikTok for viral trends, hashtags, and music
  report   Generate a cross-platform viral intelligence report
  account  Manage and optimize social media accounts
  theme    Theme page creation, niche analysis, and conversion strategies
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from cli_anything.social_media.utils.repl_skin import ReplSkin
from cli_anything.social_media.core.account_optimizer import (
    AccountProfile, register_account, get_account, list_accounts,
    remove_account, optimize_account, optimize_all_accounts,
)
from cli_anything.social_media.core.theme_pages import (
    get_niche_analysis, list_niches, get_playbook, get_conversion_strategies,
    compare_niches,
)
from cli_anything.social_media.core.trends_aggregator import generate_cross_platform_report

_VERSION = "1.0.0"
_skin = ReplSkin("social_media", version=_VERSION)


# ── Shared options ────────────────────────────────────────────────────

_json_option = click.option(
    "--json", "output_json", is_flag=True, default=False,
    help="Output results as JSON (agent-friendly mode)."
)


def _out(data: dict | list, as_json: bool) -> None:
    """Print structured output — JSON for agents, pretty-printed for humans."""
    if as_json:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        click.echo(json.dumps(data, indent=2, default=str))


# ── Root group ────────────────────────────────────────────────────────

@click.group()
@click.version_option(version=_VERSION, prog_name="cli-anything-social-media")
@click.pass_context
def main(ctx: click.Context) -> None:
    """cli-anything Social Media — viral trend intelligence & account optimization.

    Scrape YouTube and TikTok for trending content, hashtags, and music.
    Optimize your social media accounts with data-driven recommendations.
    Build theme pages that convert followers into revenue.

    Quick start:
      cli-anything-social-media trends youtube --max 20
      cli-anything-social-media trends tiktok --niche fitness
      cli-anything-social-media report --niche travel
      cli-anything-social-media account add --platform tiktok --username myaccount
      cli-anything-social-media account optimize-all
      cli-anything-social-media theme playbook --niche motivation --platform tiktok
    """
    ctx.ensure_object(dict)


# ═══════════════════════════════════════════════════════════════════════
# TRENDS GROUP
# ═══════════════════════════════════════════════════════════════════════

@main.group()
def trends() -> None:
    """Scrape viral trends, hashtags, and music from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--category", default="trending",
              type=click.Choice(["trending", "music", "gaming", "movies"]),
              show_default=True, help="Trending category to scrape.")
@click.option("--region", default="US", show_default=True,
              help="ISO 3166-1 alpha-2 region code (e.g., US, GB, IN).")
@click.option("--max", "max_results", default=20, show_default=True, type=int,
              help="Maximum number of videos to analyze.")
@_json_option
def trends_youtube(category: str, region: str, max_results: int, output_json: bool) -> None:
    """Scrape YouTube trending videos, hashtags, and music.

    Requires yt-dlp: pip install yt-dlp

    Examples:
      cli-anything-social-media trends youtube
      cli-anything-social-media trends youtube --category music --max 30
      cli-anything-social-media trends youtube --region GB --json
    """
    from cli_anything.social_media.core.youtube_scraper import scrape_youtube_trending

    _skin.info(f"Scraping YouTube {category} trends (region: {region}, max: {max_results})...")
    try:
        result = scrape_youtube_trending(
            category=category, region=region, max_results=max_results
        )
    except RuntimeError as e:
        _skin.error(str(e))
        sys.exit(1)

    if output_json:
        _out(result.to_dict(), True)
        return

    # Human-readable output
    _skin.success(f"Scraped {len(result.trends)} trending videos from YouTube")
    print()

    _skin.section("Top Trending Videos")
    rows = []
    for t in result.trends[:10]:
        rows.append([
            t.title[:50] + ("..." if len(t.title) > 50 else ""),
            f"{t.view_count:,}",
            f"{t.engagement_rate:.2f}%",
            t.channel[:20],
        ])
    _skin.table(["Title", "Views", "Engagement", "Channel"], rows)

    print()
    _skin.section("Top Hashtags")
    tag_rows = [[f"#{h['tag']}", str(h['count']), f"{h['avg_views']:,}", str(h['trend_score'])]
                for h in result.top_hashtags[:15]]
    _skin.table(["Hashtag", "Count", "Avg Views", "Score"], tag_rows)

    if result.trending_music:
        print()
        _skin.section("Trending Music")
        for m in result.trending_music[:5]:
            _skin.status(m.title, f"by {m.artist} (score: {m.trend_score})")

    if result.viral_patterns:
        print()
        _skin.section("Viral Patterns Detected")
        for p in result.viral_patterns:
            _skin.info(p)


@trends.command("tiktok")
@click.option("--niche", default="general",
              type=click.Choice([
                  "fitness", "finance", "food", "beauty", "travel",
                  "fashion", "comedy", "education", "general"
              ]),
              show_default=True, help="Content niche to scrape.")
@click.option("--region", default="US", show_default=True,
              help="Target region code.")
@click.option("--max", "max_results", default=30, show_default=True, type=int,
              help="Maximum number of videos to analyze.")
@_json_option
def trends_tiktok(niche: str, region: str, max_results: int, output_json: bool) -> None:
    """Scrape TikTok viral trends for a specific niche.

    Requires yt-dlp: pip install yt-dlp

    Examples:
      cli-anything-social-media trends tiktok
      cli-anything-social-media trends tiktok --niche fitness
      cli-anything-social-media trends tiktok --niche finance --max 50 --json
    """
    from cli_anything.social_media.core.tiktok_scraper import scrape_tiktok_trending

    _skin.info(f"Scraping TikTok {niche} trends (region: {region}, max: {max_results})...")
    try:
        result = scrape_tiktok_trending(niche=niche, region=region, max_results=max_results)
    except RuntimeError as e:
        _skin.error(str(e))
        sys.exit(1)

    if output_json:
        _out(result.to_dict(), True)
        return

    _skin.success(f"Scraped {len(result.trends)} trending TikTok videos")
    print()

    _skin.section("Top Viral TikToks")
    rows = []
    for t in result.trends[:10]:
        rows.append([
            t.title[:45] + ("..." if len(t.title) > 45 else ""),
            f"{t.play_count:,}",
            f"{t.engagement_rate:.2f}%",
            f"{t.virality_score:.3f}",
            t.author[:15],
        ])
    _skin.table(["Title", "Plays", "Engagement", "Virality", "Author"], rows)

    print()
    _skin.section("Top Hashtags")
    tag_rows = [[f"#{h['tag']}", str(h['count']), f"{h['avg_plays']:,}", str(h['trend_score'])]
                for h in result.top_hashtags[:15]]
    _skin.table(["Hashtag", "Count", "Avg Plays", "Score"], tag_rows)

    if result.trending_music:
        print()
        _skin.section("Trending Sounds")
        for m in result.trending_music[:5]:
            is_orig = " [Original]" if m.is_original else ""
            _skin.status(m.title + is_orig, f"by {m.artist} — {m.video_count} videos")

    if result.content_strategy:
        print()
        _skin.section("Content Strategy (Actionable Now)")
        for s in result.content_strategy:
            _skin.info(s)


@trends.command("user")
@click.argument("username")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok"]),
              show_default=True, help="Platform to scrape.")
@click.option("--max", "max_videos", default=30, show_default=True, type=int,
              help="Max videos to analyze.")
@_json_option
def trends_user(username: str, platform: str, max_videos: int, output_json: bool) -> None:
    """Analyze a specific user's content for trend patterns.

    Examples:
      cli-anything-social-media trends user @charlidamelio
      cli-anything-social-media trends user khaby.lame --max 50
    """
    from cli_anything.social_media.core.tiktok_scraper import scrape_tiktok_user

    _skin.info(f"Analyzing {platform} user: {username} ({max_videos} videos)...")
    try:
        result = scrape_tiktok_user(username, max_videos=max_videos)
    except RuntimeError as e:
        _skin.error(str(e))
        sys.exit(1)

    if output_json:
        _out(result.to_dict(), True)
        return

    _skin.success(f"Analyzed {len(result.trends)} videos from @{username}")
    if result.viral_patterns:
        print()
        _skin.section("Viral Patterns for This Account")
        for p in result.viral_patterns:
            _skin.info(p)
    if result.content_strategy:
        print()
        _skin.section("Strategy Recommendations")
        for s in result.content_strategy:
            _skin.info(s)


@trends.command("hashtag")
@click.argument("hashtag")
@click.option("--platform", default="youtube",
              type=click.Choice(["youtube"]),
              show_default=True)
@click.option("--max", "max_results", default=20, show_default=True, type=int)
@_json_option
def trends_hashtag(hashtag: str, platform: str, max_results: int, output_json: bool) -> None:
    """Research a specific hashtag's performance.

    Examples:
      cli-anything-social-media trends hashtag fitness
      cli-anything-social-media trends hashtag "#mentalhealth" --max 30
    """
    from cli_anything.social_media.core.youtube_scraper import search_youtube_hashtag

    tag = hashtag.lstrip("#")
    _skin.info(f"Researching #{tag} on {platform}...")
    try:
        videos = search_youtube_hashtag(tag, max_results=max_results)
    except RuntimeError as e:
        _skin.error(str(e))
        sys.exit(1)

    if output_json:
        _out([v.to_dict() for v in videos], True)
        return

    _skin.success(f"Found {len(videos)} videos for #{tag}")
    rows = [[
        v.title[:50] + ("..." if len(v.title) > 50 else ""),
        f"{v.view_count:,}",
        f"{v.engagement_rate:.2f}%",
        v.channel[:20],
    ] for v in videos[:15]]
    _skin.table(["Title", "Views", "Engagement", "Channel"], rows)


# ═══════════════════════════════════════════════════════════════════════
# REPORT GROUP
# ═══════════════════════════════════════════════════════════════════════

@main.command("report")
@click.option("--niche", default="general",
              type=click.Choice([
                  "fitness", "finance", "food", "beauty", "travel",
                  "fashion", "comedy", "education", "general"
              ]),
              show_default=True, help="TikTok niche for trend context.")
@click.option("--region", default="US", show_default=True)
@click.option("--max", "max_results", default=20, show_default=True, type=int,
              help="Videos per platform to analyze.")
@click.option("--yt-category", default="trending",
              type=click.Choice(["trending", "music", "gaming", "movies"]),
              show_default=True)
@click.option("--no-youtube", is_flag=True, default=False,
              help="Skip YouTube scraping.")
@click.option("--no-tiktok", is_flag=True, default=False,
              help="Skip TikTok scraping.")
@click.option("--save", "save_path", default=None, type=click.Path(),
              help="Save report to a JSON file.")
@_json_option
def report(
    niche: str, region: str, max_results: int, yt_category: str,
    no_youtube: bool, no_tiktok: bool, save_path: str | None, output_json: bool,
) -> None:
    """Generate a full cross-platform viral intelligence report.

    Combines YouTube + TikTok data into a single prioritized action plan.

    Examples:
      cli-anything-social-media report
      cli-anything-social-media report --niche fitness --region GB
      cli-anything-social-media report --save report.json --json
    """
    _skin.info("Generating cross-platform viral intelligence report...")
    _skin.info(f"Niche: {niche} | Region: {region} | Platforms: "
               f"{'YouTube ' if not no_youtube else ''}{'TikTok' if not no_tiktok else ''}")

    try:
        result = generate_cross_platform_report(
            niche=niche,
            region=region,
            max_results=max_results,
            include_youtube=not no_youtube,
            include_tiktok=not no_tiktok,
            yt_category=yt_category,
        )
    except RuntimeError as e:
        _skin.error(str(e))
        sys.exit(1)

    data = result.to_dict()

    if save_path:
        Path(save_path).write_text(json.dumps(data, indent=2, default=str))
        _skin.success(f"Report saved to: {save_path}")

    if output_json:
        _out(data, True)
        return

    _skin.success("Report generated successfully")
    print()

    _skin.section("Proactive Action Plan")
    for i, action in enumerate(result.proactive_actions, 1):
        _skin.info(f"{i}. {action}")

    print()
    _skin.section("Master Hashtags (Copy-Paste Ready)")
    click.echo("  " + " ".join(result.master_hashtags[:15]))

    if result.master_sounds:
        print()
        _skin.section("Trending Sounds to Use Right Now")
        for s in result.master_sounds[:5]:
            _skin.status("  Sound", s)

    if result.unified_trends:
        print()
        _skin.section("Top Cross-Platform Keywords")
        rows = [[
            t.keyword,
            ", ".join(t.platforms),
            str(t.combined_score),
            f"{t.youtube_avg_views:,}",
            f"{t.tiktok_avg_plays:,}",
        ] for t in result.unified_trends[:10]]
        _skin.table(
            ["Keyword", "Platforms", "Score", "YT Avg Views", "TT Avg Plays"],
            rows
        )


# ═══════════════════════════════════════════════════════════════════════
# ACCOUNT GROUP
# ═══════════════════════════════════════════════════════════════════════

@main.group()
def account() -> None:
    """Manage and optimize social media accounts."""


@account.command("add")
@click.option("--platform", required=True,
              type=click.Choice(["youtube", "tiktok", "instagram"]),
              help="Social media platform.")
@click.option("--username", required=True, help="Account username (without @).")
@click.option("--display-name", default="", help="Display/channel name.")
@click.option("--bio", default="", help="Current account bio.")
@click.option("--followers", default=0, type=int, help="Current follower count.")
@click.option("--following", default=0, type=int, help="Current following count.")
@click.option("--posts", default=0, type=int, help="Total post count.")
@click.option("--avg-views", default=0, type=int, help="Average views per post.")
@click.option("--avg-likes", default=0, type=int, help="Average likes per post.")
@click.option("--avg-comments", default=0, type=int, help="Average comments per post.")
@click.option("--niche", default="", help="Content niche (e.g., fitness, finance).")
@click.option("--posting-freq", default="unknown", help="Posting frequency (e.g., 'daily', '3x/week').")
@click.option("--content-types", default="", help="Comma-separated content types.")
@click.option("--hashtags", default="", help="Comma-separated current hashtags.")
@click.option("--profile-url", default="", help="Profile link URL.")
@click.option("--notes", default="", help="Additional notes.")
def account_add(
    platform, username, display_name, bio, followers, following, posts,
    avg_views, avg_likes, avg_comments, niche, posting_freq,
    content_types, hashtags, profile_url, notes,
) -> None:
    """Register a social media account for optimization tracking.

    Examples:
      cli-anything-social-media account add --platform tiktok --username myaccount \\
        --followers 5000 --niche fitness --avg-views 10000 --posting-freq daily
    """
    profile = AccountProfile(
        platform=platform,
        username=username,
        display_name=display_name or username,
        bio=bio,
        follower_count=followers,
        following_count=following,
        post_count=posts,
        avg_views=avg_views,
        avg_likes=avg_likes,
        avg_comments=avg_comments,
        niche=niche,
        posting_frequency=posting_freq,
        content_types=[c.strip() for c in content_types.split(",") if c.strip()],
        current_hashtags=[h.strip().lstrip("#") for h in hashtags.split(",") if h.strip()],
        profile_url=profile_url,
        notes=notes,
    )
    register_account(profile)
    _skin.success(f"Registered @{username} on {platform}")
    _skin.info(f"Run: cli-anything-social-media account optimize --platform {platform} --username {username}")


@account.command("list")
@_json_option
def account_list(output_json: bool) -> None:
    """List all registered accounts.

    Example:
      cli-anything-social-media account list
    """
    accounts = list_accounts()
    if not accounts:
        _skin.warning("No accounts registered. Use 'account add' to add one.")
        return

    if output_json:
        _out([a.to_dict() for a in accounts], True)
        return

    rows = [[
        a.platform,
        f"@{a.username}",
        a.niche or "—",
        f"{a.follower_count:,}",
        f"{a.engagement_rate():.2f}%",
        a.posting_frequency,
    ] for a in accounts]
    _skin.table(
        ["Platform", "Username", "Niche", "Followers", "Engagement", "Freq"],
        rows
    )


@account.command("remove")
@click.option("--platform", required=True,
              type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.option("--username", required=True)
def account_remove(platform: str, username: str) -> None:
    """Remove an account from the registry.

    Example:
      cli-anything-social-media account remove --platform tiktok --username myaccount
    """
    if remove_account(platform, username):
        _skin.success(f"Removed @{username} ({platform})")
    else:
        _skin.error(f"Account @{username} ({platform}) not found")
        sys.exit(1)


@account.command("optimize")
@click.option("--platform", required=True,
              type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.option("--username", required=True)
@click.option("--with-trends", is_flag=True, default=False,
              help="Fetch live trending hashtags to incorporate into recommendations.")
@click.option("--save", "save_path", default=None, type=click.Path(),
              help="Save optimization report to JSON file.")
@_json_option
def account_optimize(
    platform: str, username: str, with_trends: bool,
    save_path: str | None, output_json: bool,
) -> None:
    """Generate an optimization report for a specific account.

    Examples:
      cli-anything-social-media account optimize --platform tiktok --username myaccount
      cli-anything-social-media account optimize --platform youtube --username mychannel \\
        --with-trends --save report.json
    """
    profile = get_account(platform, username)
    if not profile:
        _skin.error(f"Account @{username} ({platform}) not registered. Use 'account add' first.")
        sys.exit(1)

    trending_tags = None
    if with_trends:
        _skin.info("Fetching live trending hashtags...")
        try:
            from cli_anything.social_media.core.trends_aggregator import generate_cross_platform_report
            trend_report = generate_cross_platform_report(
                niche=profile.niche or "general",
                max_results=15,
                include_youtube=(platform == "youtube"),
                include_tiktok=(platform == "tiktok"),
            )
            trending_tags = [t.lstrip("#") for t in trend_report.master_hashtags[:20]]
            _skin.success(f"Loaded {len(trending_tags)} live trending hashtags")
        except Exception as e:
            _skin.warning(f"Could not fetch live trends: {e}")

    report = optimize_account(profile, trending_tags)

    if save_path:
        Path(save_path).write_text(json.dumps(report.to_dict(), indent=2, default=str))
        _skin.success(f"Saved to: {save_path}")

    if output_json:
        _out(report.to_dict(), True)
        return

    _skin.success(f"Optimization report for @{username} ({platform})")
    print()

    # Score
    s = report.score
    bar_len = s.overall // 5
    bar = "█" * bar_len + "░" * (20 - bar_len)
    click.echo(f"  Overall Score:  {bar}  {s.overall}/100")
    print()

    _skin.table(
        ["Dimension", "Score"],
        [
            ["Profile Completeness", f"{s.profile_completeness}/100"],
            ["Content Strategy", f"{s.content_strategy}/100"],
            ["Hashtag Quality", f"{s.hashtag_quality}/100"],
            ["Posting Consistency", f"{s.posting_consistency}/100"],
            ["Engagement Health", f"{s.engagement_health}/100"],
            ["Growth Trajectory", f"{s.growth_trajectory}/100"],
        ]
    )

    if report.critical_fixes:
        print()
        _skin.section("Critical Fixes (Do These First)")
        for fix in report.critical_fixes:
            _skin.warning(fix)

    if report.quick_wins:
        print()
        _skin.section("Quick Wins")
        for win in report.quick_wins:
            _skin.info(win)

    if report.strategic_recommendations:
        print()
        _skin.section("Strategic Recommendations")
        for rec in report.strategic_recommendations:
            _skin.info(rec)

    print()
    _skin.section("Suggested Bio")
    click.echo(f"  {report.bio_rewrite}")

    print()
    _skin.section("Hashtag Overhaul")
    plan = report.hashtag_overhaul
    _skin.status("Niche tags", " ".join(plan.get("add_niche", [])))
    _skin.status("Trending tags", " ".join(plan.get("add_trending", [])))
    _skin.status("Broad tags", " ".join(plan.get("add_broad", [])))
    _skin.info(plan.get("instructions", ""))

    print()
    _skin.section("Monetization Opportunities")
    for opp in report.monetization_opportunities:
        _skin.info(opp)


@account.command("optimize-all")
@click.option("--with-trends", is_flag=True, default=False,
              help="Incorporate live trending hashtags.")
@click.option("--save-dir", default=None, type=click.Path(),
              help="Directory to save individual JSON reports.")
@_json_option
def account_optimize_all(
    with_trends: bool, save_dir: str | None, output_json: bool,
) -> None:
    """Optimize ALL registered accounts at once.

    Generates an optimization report for every registered account
    and outputs a prioritized action plan.

    Examples:
      cli-anything-social-media account optimize-all
      cli-anything-social-media account optimize-all --with-trends --save-dir ./reports
    """
    accounts = list_accounts()
    if not accounts:
        _skin.warning("No accounts registered. Use 'account add' to add one.")
        return

    trending_tags = None
    if with_trends:
        _skin.info("Fetching live trending hashtags for all accounts...")
        try:
            from cli_anything.social_media.core.trends_aggregator import generate_cross_platform_report
            trend_report = generate_cross_platform_report(niche="general", max_results=15)
            trending_tags = [t.lstrip("#") for t in trend_report.master_hashtags[:20]]
            _skin.success(f"Loaded {len(trending_tags)} trending hashtags")
        except Exception as e:
            _skin.warning(f"Could not fetch live trends: {e}")

    reports = optimize_all_accounts(trending_tags)

    if save_dir:
        dir_path = Path(save_dir)
        dir_path.mkdir(parents=True, exist_ok=True)
        for r in reports:
            fname = f"{r.account.platform}_{r.account.username}_report.json"
            (dir_path / fname).write_text(json.dumps(r.to_dict(), indent=2, default=str))
        _skin.success(f"Saved {len(reports)} reports to: {save_dir}")

    if output_json:
        _out([r.to_dict() for r in reports], True)
        return

    for r in reports:
        print()
        click.echo("=" * 60)
        _skin.section(f"@{r.account.username} ({r.account.platform.upper()})  —  Score: {r.score.overall}/100")

        if r.critical_fixes:
            _skin.warning(f"[CRITICAL] {r.critical_fixes[0]}")

        _skin.info(f"Quick win: {r.quick_wins[0] if r.quick_wins else 'See full report'}")
        _skin.info(f"Bio suggestion: {r.bio_rewrite}")

        if r.score.hashtag_quality < 60 and r.hashtag_overhaul.get("add_niche"):
            tags = " ".join(r.hashtag_overhaul["add_niche"][:4])
            _skin.info(f"Replace hashtags with: {tags}")


# ═══════════════════════════════════════════════════════════════════════
# THEME GROUP
# ═══════════════════════════════════════════════════════════════════════

@main.group()
def theme() -> None:
    """Theme page creation, niche analysis, and monetization strategies."""


@theme.command("niches")
@_json_option
def theme_niches(output_json: bool) -> None:
    """List all available niches with monetization and growth analysis.

    Example:
      cli-anything-social-media theme niches
    """
    niches = list_niches()

    if output_json:
        _out([n.to_dict() for n in niches], True)
        return

    _skin.section("Available Niches")
    rows = [[
        n.niche.replace("_", " ").title(),
        n.competition_level,
        n.monetization_potential,
        n.growth_speed,
        f"${n.avg_cpm:.0f}",
    ] for n in niches]
    _skin.table(
        ["Niche", "Competition", "Monetization", "Growth Speed", "Avg CPM"],
        rows
    )
    print()
    _skin.hint("Run: cli-anything-social-media theme niche --name <niche> for full details")


@theme.command("niche")
@click.option("--name", required=True, help="Niche name (e.g., fitness, personal_finance).")
@_json_option
def theme_niche(name: str, output_json: bool) -> None:
    """Get detailed analysis for a specific niche.

    Examples:
      cli-anything-social-media theme niche --name fitness
      cli-anything-social-media theme niche --name personal_finance --json
    """
    analysis = get_niche_analysis(name)
    if not analysis:
        _skin.error(f"Niche '{name}' not found. Run 'theme niches' to see available niches.")
        sys.exit(1)

    if output_json:
        _out(analysis.to_dict(), True)
        return

    _skin.section(f"Niche: {analysis.niche.replace('_', ' ').title()}")
    _skin.status("Competition", analysis.competition_level)
    _skin.status("Monetization potential", analysis.monetization_potential)
    _skin.status("Growth speed", analysis.growth_speed)
    _skin.status("Avg CPM", f"${analysis.avg_cpm:.2f}")
    _skin.status("Top platforms", ", ".join(analysis.top_platforms))
    _skin.status("Content difficulty", analysis.content_difficulty)
    _skin.status("Demographics", analysis.audience_demographics)

    print()
    _skin.section("Top Hashtags")
    click.echo("  " + " ".join(f"#{t}" for t in analysis.top_hashtags))

    print()
    _skin.section("Monetization Paths")
    for path in analysis.monetization_paths:
        _skin.info(path)

    if analysis.notes:
        print()
        _skin.section("Pro Notes")
        _skin.hint(f"  {analysis.notes}")


@theme.command("playbook")
@click.option("--niche", required=True,
              help="Content niche (e.g., fitness, motivation, travel).")
@click.option("--platform", default="tiktok",
              type=click.Choice(["tiktok", "instagram", "youtube"]),
              show_default=True, help="Target platform.")
@click.option("--save", "save_path", default=None, type=click.Path(),
              help="Save playbook to a JSON file.")
@_json_option
def theme_playbook(niche: str, platform: str, save_path: str | None, output_json: bool) -> None:
    """Generate a step-by-step theme page launch playbook.

    Includes 4-phase launch plan, content sources, monetization timeline,
    hashtag sets, bio templates, and common mistakes to avoid.

    Examples:
      cli-anything-social-media theme playbook --niche motivation
      cli-anything-social-media theme playbook --niche fitness --platform instagram
      cli-anything-social-media theme playbook --niche travel --save playbook.json
    """
    playbook = get_playbook(niche, platform)

    if save_path:
        Path(save_path).write_text(json.dumps(playbook.to_dict(), indent=2, default=str))
        _skin.success(f"Playbook saved to: {save_path}")

    if output_json:
        _out(playbook.to_dict(), True)
        return

    _skin.section(f"Theme Page Playbook: {niche.title()} on {platform.title()}")
    print()

    _skin.section("Phase 1: Launch (Days 1-7)")
    for step in playbook.phase_1_launch:
        _skin.info(step)

    print()
    _skin.section("Phase 2: Grow (Days 8-30)")
    for step in playbook.phase_2_growth:
        _skin.info(step)

    print()
    _skin.section("Phase 3: Scale (Days 31-90)")
    for step in playbook.phase_3_scale:
        _skin.info(step)

    print()
    _skin.section("Phase 4: Monetize (Day 90+)")
    for step in playbook.phase_4_monetize:
        _skin.info(step)

    print()
    _skin.section("Content Sources")
    for src in playbook.content_sources:
        _skin.hint(f"  • {src}")

    print()
    _skin.section("Monetization Timeline")
    rows = [[
        m["milestone"],
        m["action"][:60] + ("..." if len(m["action"]) > 60 else ""),
        m["expected_income"],
    ] for m in playbook.monetization_timeline]
    _skin.table(["Milestone", "Action", "Expected Income"], rows)

    print()
    _skin.section("Bio Templates (Copy One)")
    for i, bio in enumerate(playbook.bio_templates, 1):
        click.echo(f"  [{i}] {bio}")

    print()
    _skin.section("Hashtag Sets (Rotate Every 3-5 Posts)")
    for i, hset in enumerate(playbook.hashtag_sets, 1):
        click.echo(f"  Set {i}: {' '.join('#' + t for t in hset)}")

    print()
    _skin.section("Tools Needed")
    tool_rows = [[t["tool"], t["purpose"], t["cost"]] for t in playbook.tools_needed]
    _skin.table(["Tool", "Purpose", "Cost"], tool_rows)

    print()
    _skin.section("Common Mistakes to Avoid")
    for mistake in playbook.common_mistakes:
        _skin.warning(mistake)


@theme.command("convert")
@click.option("--difficulty", default=None,
              type=click.Choice(["beginner", "intermediate", "advanced"]),
              help="Filter by difficulty level.")
@_json_option
def theme_convert(difficulty: str | None, output_json: bool) -> None:
    """Show follower-to-revenue conversion strategies.

    Covers: bio link funnels, shoutout business, affiliate stacking,
    digital product ladders, and paid communities.

    Examples:
      cli-anything-social-media theme convert
      cli-anything-social-media theme convert --difficulty beginner
    """
    strategies = get_conversion_strategies(difficulty)

    if output_json:
        _out([s.to_dict() for s in strategies], True)
        return

    for strategy in strategies:
        print()
        _skin.section(f"{strategy.strategy_name}  [{strategy.difficulty.upper()}]")
        _skin.status("Income potential", strategy.income_potential)
        _skin.status("Setup time", strategy.setup_time)
        _skin.info(strategy.description)
        print()
        _skin.hint("  Steps:")
        for i, step in enumerate(strategy.steps, 1):
            _skin.hint(f"  {i}. {step}")
        _skin.hint(f"\n  Tools: {', '.join(strategy.tools)}")
        if strategy.examples:
            _skin.hint("\n  Examples:")
            for ex in strategy.examples:
                _skin.hint(f"  • {ex}")


@theme.command("compare")
@click.argument("niches", nargs=-1, required=True)
@_json_option
def theme_compare(niches: tuple[str, ...], output_json: bool) -> None:
    """Compare multiple niches side by side.

    Examples:
      cli-anything-social-media theme compare fitness finance travel
      cli-anything-social-media theme compare motivation pets tech --json
    """
    results = compare_niches(list(niches))
    if not results:
        _skin.error("No matching niches found. Run 'theme niches' to see available options.")
        sys.exit(1)

    if output_json:
        _out([n.to_dict() for n in results], True)
        return

    rows = [[
        n.niche.replace("_", " ").title(),
        n.competition_level,
        n.monetization_potential,
        n.growth_speed,
        f"${n.avg_cpm:.0f}",
        n.content_difficulty,
    ] for n in results]
    _skin.table(
        ["Niche", "Competition", "Monetization", "Growth", "CPM", "Difficulty"],
        rows
    )


# ── REPL entry point ──────────────────────────────────────────────────

def _run_repl() -> None:
    """Launch the interactive REPL for social media CLI."""
    _skin.print_banner()
    pt_session = _skin.create_prompt_session()

    help_text = {
        "trends youtube": "Scrape YouTube trending videos & hashtags",
        "trends tiktok": "Scrape TikTok viral content by niche",
        "trends user @NAME": "Analyze a specific user's content",
        "trends hashtag TAG": "Research a specific hashtag",
        "report": "Full cross-platform viral intelligence report",
        "account add": "Register a social media account",
        "account list": "List all registered accounts",
        "account optimize": "Optimize a specific account",
        "account optimize-all": "Optimize ALL registered accounts",
        "theme niches": "Browse all available niches",
        "theme niche": "Deep dive into a specific niche",
        "theme playbook": "Full theme page launch playbook",
        "theme convert": "Follower-to-revenue conversion strategies",
        "theme compare": "Compare niches side by side",
        "help": "Show this help",
        "quit": "Exit",
    }

    _skin.info("Welcome to cli-anything Social Media. Type 'help' to get started.")
    print()

    while True:
        try:
            line = _skin.get_input(pt_session)
        except (EOFError, KeyboardInterrupt):
            break

        if not line:
            continue
        if line.lower() in ("quit", "exit", "q"):
            break
        if line.lower() in ("help", "h", "?"):
            _skin.help(help_text)
            continue

        # Delegate to Click CLI
        try:
            from click.testing import CliRunner
            runner = CliRunner(mix_stderr=False)
            result = runner.invoke(main, line.split(), catch_exceptions=False)
            if result.output:
                click.echo(result.output, nl=False)
            if result.exit_code != 0 and result.stderr_bytes:
                click.echo(result.stderr_bytes.decode(), err=True, nl=False)
        except SystemExit:
            pass
        except Exception as e:
            _skin.error(str(e))

    _skin.print_goodbye()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        _run_repl()
    else:
        main()
