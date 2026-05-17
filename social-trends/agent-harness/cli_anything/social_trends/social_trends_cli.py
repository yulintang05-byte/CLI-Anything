"""CLI-Anything Social Trends — Main CLI entry point.

Commands:
  setup         Configure API keys, region, and default niche
  accounts      Manage your YouTube/TikTok accounts
  scrape        Scrape trending videos, hashtags, and music
  hashtags      Analyze and generate hashtag strategies
  music         Track trending sounds and music
  optimize      Audit accounts and generate optimization reports
  theme-page    Theme page creation and conversion playbook
  report        View and export saved reports
  status        Show current configuration status
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click

from cli_anything.social_trends.utils.social_backend import SocialBackend
from cli_anything.social_trends.utils.repl_skin import ReplSkin

_skin = ReplSkin("social_trends", version="1.0.0")
_skin._ACCENT_COLORS = {**getattr(_skin, "_ACCENT_COLORS", {}), "social_trends": "\033[38;5;197m"}


# ── CLI Root ───────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.version_option("1.0.0", prog_name="cli-anything-social-trends")
@click.option("--json", "as_json", is_flag=True, help="Output results as JSON")
@click.pass_context
def main(ctx: click.Context, as_json: bool) -> None:
    """CLI-Anything Social Trends — Viral trend scraping & account optimization."""
    ctx.ensure_object(dict)
    ctx.obj["backend"] = SocialBackend()
    ctx.obj["json"] = as_json
    if ctx.invoked_subcommand is None:
        _launch_repl(ctx.obj["backend"])


# ── Setup ──────────────────────────────────────────────────────────────────

@main.group()
def setup() -> None:
    """Configure API keys, region, and default niche."""


@setup.command("youtube-key")
@click.argument("api_key")
@click.pass_context
def setup_youtube_key(ctx: click.Context, api_key: str) -> None:
    """Set your YouTube Data API v3 key.

    Get one at: https://console.cloud.google.com/  (free tier: 10,000 units/day)
    """
    be: SocialBackend = ctx.obj["backend"]
    be.set_youtube_api_key(api_key)
    _skin.success("YouTube API key saved.")
    _skin.info("Test it with: cli-anything-social-trends scrape youtube --trending")


@setup.command("tiktok-token")
@click.argument("ms_token")
@click.pass_context
def setup_tiktok_token(ctx: click.Context, ms_token: str) -> None:
    """Set your TikTok ms_token for enhanced data access.

    To get your ms_token:
      1. Open TikTok in Chrome, log in
      2. DevTools → Application → Cookies → tiktok.com → ms_token
      3. Copy the value and paste it here
    """
    be: SocialBackend = ctx.obj["backend"]
    be.set_tiktok_ms_token(ms_token)
    _skin.success("TikTok ms_token saved.")


@setup.command("region")
@click.argument("region_code")
@click.pass_context
def setup_region(ctx: click.Context, region_code: str) -> None:
    """Set default region code for trend scraping (e.g. US, GB, AU, CA)."""
    be: SocialBackend = ctx.obj["backend"]
    be.set_region(region_code.upper())
    _skin.success(f"Region set to {region_code.upper()}")


@setup.command("niche")
@click.argument("niche")
@click.pass_context
def setup_niche(ctx: click.Context, niche: str) -> None:
    """Set default niche (fitness, food, travel, tech, beauty, gaming, motivation, finance, fashion, comedy)."""
    be: SocialBackend = ctx.obj["backend"]
    be.set_niche(niche)
    _skin.success(f"Default niche set to: {niche}")


# ── Accounts ───────────────────────────────────────────────────────────────

@main.group()
def accounts() -> None:
    """Manage your YouTube and TikTok accounts."""


@accounts.command("add")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"]))
@click.argument("username")
@click.option("--channel-id", help="YouTube channel ID (for API lookups)")
@click.option("--niche", help="Override default niche for this account")
@click.pass_context
def accounts_add(
    ctx: click.Context, platform: str, username: str,
    channel_id: Optional[str], niche: Optional[str]
) -> None:
    """Register an account for tracking and optimization."""
    be: SocialBackend = ctx.obj["backend"]
    entry = be.add_account(platform, username, channel_id, niche)
    _skin.success(f"Added {platform} account: @{username}")
    if platform == "youtube" and not channel_id:
        _skin.hint("Tip: Add --channel-id to enable full YouTube API analysis")


@accounts.command("remove")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"]))
@click.argument("username")
@click.pass_context
def accounts_remove(ctx: click.Context, platform: str, username: str) -> None:
    """Remove a registered account."""
    be: SocialBackend = ctx.obj["backend"]
    if be.remove_account(platform, username):
        _skin.success(f"Removed {platform} account: @{username}")
    else:
        _skin.error(f"Account not found: {platform}/@{username}")


@accounts.command("list")
@click.pass_context
def accounts_list(ctx: click.Context) -> None:
    """List all registered accounts."""
    be: SocialBackend = ctx.obj["backend"]
    entries = be.list_accounts()
    if not entries:
        _skin.warning("No accounts registered. Add one with: accounts add <platform> <username>")
        return
    headers = ["Platform", "Username", "Niche", "Channel ID", "Added"]
    rows = [
        [e.platform, f"@{e.username}", e.niche or "-", e.channel_id or "-", e.added_at[:10]]
        for e in entries
    ]
    _skin.table(headers, rows)


# ── Scrape ─────────────────────────────────────────────────────────────────

@main.group()
def scrape() -> None:
    """Scrape trending content from YouTube and TikTok."""


@scrape.command("youtube")
@click.option("--trending", is_flag=True, help="Fetch most-popular videos")
@click.option("--niche", help="Search trending videos for a specific niche")
@click.option("--category", default="0", help="YouTube category ID (0=all, 10=music, 17=sports, 20=gaming)")
@click.option("--region", help="Region code override (e.g. GB, AU)")
@click.option("--limit", default=25, show_default=True, help="Max videos to fetch")
@click.option("--save", is_flag=True, help="Save results to report file")
@click.pass_context
def scrape_youtube(
    ctx: click.Context, trending: bool, niche: Optional[str],
    category: str, region: Optional[str], limit: int, save: bool
) -> None:
    """Scrape trending YouTube videos, hashtags, and music."""
    be: SocialBackend = ctx.obj["backend"]
    if not be.config.youtube_api_key:
        _skin.error("No YouTube API key configured.")
        _skin.hint("Run: setup youtube-key YOUR_KEY")
        sys.exit(1)

    from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
    from cli_anything.social_trends.core.music_tracker import MusicTracker

    yt = YouTubeScraper(
        api_key=be.config.youtube_api_key,
        region_code=region or be.config.default_region,
        max_results=limit,
    )
    effective_niche = niche or be.config.default_niche

    def _do_scrape():
        nonlocal videos, hashtags, tracks
        videos = yt.get_trending_videos(category_id=category) if (trending or not niche) else yt.get_trending_by_niche(effective_niche, limit)
        hashtags = yt.extract_hashtags(videos)
        tracks = yt.get_trending_music(videos)

    videos: list = []
    hashtags: list = []
    tracks: list = []
    if ctx.obj["json"]:
        _do_scrape()
    else:
        with click.progressbar(length=3, label="Scraping YouTube") as bar:
            videos = yt.get_trending_videos(category_id=category) if (trending or not niche) else yt.get_trending_by_niche(effective_niche, limit)
            bar.update(1)
            hashtags = yt.extract_hashtags(videos)
            bar.update(1)
            tracks = yt.get_trending_music(videos)
            bar.update(1)

    if ctx.obj["json"]:
        click.echo(json.dumps({"videos": videos, "hashtags": hashtags, "music": tracks}, indent=2, default=str))
        return

    _skin.success(f"Fetched {len(videos)} videos, {len(hashtags)} hashtags, {len(tracks)} music tracks")

    # Top videos table
    _skin.info(f"\nTop {min(10, len(videos))} Trending YouTube Videos ({effective_niche.upper()}):")
    v_headers = ["#", "Title", "Channel", "Views", "ER%", "Tags"]
    v_rows = [
        [
            i + 1,
            v["title"][:50],
            v["channel"][:20],
            f"{v.get('view_count', 0):,}",
            f"{round((v.get('like_count',0)+v.get('comment_count',0))/max(v.get('view_count',1),1)*100,2)}%",
            len(v.get("tags", [])),
        ]
        for i, v in enumerate(videos[:10])
    ]
    _skin.table(v_headers, v_rows)

    # Top hashtags
    _skin.info(f"\nTop 20 Trending Hashtags:")
    h_headers = ["Rank", "Hashtag", "Mentions"]
    h_rows = [[i + 1, f"#{t}", c] for i, (t, c) in enumerate(hashtags[:20])]
    _skin.table(h_headers, h_rows)

    # Top music
    if tracks:
        _skin.info(f"\nTop Trending Music:")
        m_headers = ["Rank", "Title", "Artist", "Views"]
        m_rows = [[i + 1, t["title"][:40], t["artist"][:25], f"{t.get('view_count', 0):,}"] for i, t in enumerate(tracks[:10])]
        _skin.table(m_headers, m_rows)

    if save:
        report = {"platform": "youtube", "niche": effective_niche, "videos": videos, "hashtags": hashtags, "music": tracks}
        path = be.save_report("youtube_trends", report)
        _skin.success(f"Report saved: {path}")


@scrape.command("tiktok")
@click.option("--trending", is_flag=True, help="Fetch FYP trending videos")
@click.option("--hashtag", help="Fetch top videos for a specific hashtag")
@click.option("--niche", help="Fetch videos for niche hashtag set")
@click.option("--limit", default=30, show_default=True)
@click.option("--no-playwright", is_flag=True, help="Force HTTP-only mode (no browser)")
@click.option("--save", is_flag=True)
@click.pass_context
def scrape_tiktok(
    ctx: click.Context, trending: bool, hashtag: Optional[str],
    niche: Optional[str], limit: int, no_playwright: bool, save: bool
) -> None:
    """Scrape trending TikTok videos, hashtags, and sounds."""
    be: SocialBackend = ctx.obj["backend"]
    from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper

    tt = TikTokScraper(
        use_playwright=not no_playwright,
        ms_token=be.config.tiktok_ms_token,
    )
    effective_niche = niche or be.config.default_niche

    videos: list[dict] = []
    with click.progressbar(length=3, label="Scraping TikTok") as bar:
        if hashtag:
            videos = tt.get_hashtag_videos(hashtag, limit)
        elif niche:
            seed_tags = tt.get_niche_hashtags(effective_niche)
            for tag in seed_tags[:2]:
                videos.extend(tt.get_hashtag_videos(tag, limit // 2))
        else:
            videos = tt.get_trending_videos(limit)
        bar.update(1)
        hashtags = tt.extract_hashtags(videos)
        bar.update(1)
        sounds = tt.get_trending_sounds(videos)
        bar.update(1)

    _skin.success(f"Fetched {len(videos)} videos, {len(hashtags)} hashtags, {len(sounds)} sounds")

    if ctx.obj["json"]:
        click.echo(json.dumps({"videos": videos, "hashtags": hashtags, "sounds": sounds}, indent=2, default=str))
        return

    _skin.info(f"\nTop {min(10, len(videos))} Trending TikTok Videos ({effective_niche.upper()}):")
    v_headers = ["#", "Description", "Author", "Plays", "Likes", "ER%"]
    v_rows = [
        [i + 1, v.get("description", "")[:45], f"@{v.get('author','')[:18]}",
         f"{v.get('play_count',0):,}", f"{v.get('like_count',0):,}",
         f"{v.get('engagement_rate',0)}%"]
        for i, v in enumerate(videos[:10])
    ]
    _skin.table(v_headers, v_rows)

    _skin.info("\nTop 20 Trending TikTok Hashtags:")
    h_rows = [[i + 1, f"#{t}", c] for i, (t, c) in enumerate(hashtags[:20])]
    _skin.table(["Rank", "Hashtag", "Mentions"], h_rows)

    if sounds:
        _skin.info("\nTop Trending TikTok Sounds:")
        s_rows = [[i + 1, s.get("title","")[:35], s.get("artist","")[:20], s.get("video_count",0)] for i, s in enumerate(sounds[:10])]
        _skin.table(["Rank", "Sound", "Artist", "Videos Using It"], s_rows)

    if save:
        report = {"platform": "tiktok", "niche": effective_niche, "videos": videos, "hashtags": hashtags, "sounds": sounds}
        path = be.save_report("tiktok_trends", report)
        _skin.success(f"Report saved: {path}")


@scrape.command("all")
@click.option("--niche", help="Niche to scrape (overrides default)")
@click.option("--save", is_flag=True, default=True, show_default=True)
@click.pass_context
def scrape_all(ctx: click.Context, niche: Optional[str], save: bool) -> None:
    """Run full scrape of both YouTube and TikTok and generate combined report."""
    _skin.info("Running full cross-platform scrape...")
    ctx.invoke(scrape_youtube, trending=True, niche=niche, category="0",
               region=None, limit=30, save=False)
    ctx.invoke(scrape_tiktok, trending=True, hashtag=None, niche=niche,
               limit=30, no_playwright=False, save=False)
    _skin.success("Full scrape complete. Run 'hashtags strategy' to build posting strategy.")


# ── Hashtags ───────────────────────────────────────────────────────────────

@main.group()
def hashtags() -> None:
    """Analyze trends and generate hashtag strategies."""


@hashtags.command("strategy")
@click.option("--niche", help="Niche to build strategy for")
@click.option("--platform", type=click.Choice(["youtube", "tiktok", "both"]), default="both")
@click.option("--from-report", help="Path to a saved trends report JSON")
@click.option("--max-tags", default=30, show_default=True)
@click.pass_context
def hashtags_strategy(
    ctx: click.Context, niche: Optional[str], platform: str,
    from_report: Optional[str], max_tags: int
) -> None:
    """Build a complete hashtag posting strategy from scraped data."""
    be: SocialBackend = ctx.obj["backend"]
    effective_niche = niche or be.config.default_niche

    from cli_anything.social_trends.core.hashtag_analyzer import HashtagAnalyzer
    analyzer = HashtagAnalyzer()

    if from_report:
        path = Path(from_report)
        if not path.exists():
            _skin.error(f"Report not found: {from_report}")
            sys.exit(1)
        data = json.loads(path.read_text())
        if "hashtags" in data:
            ht = data["hashtags"]
            if isinstance(ht, list) and ht and isinstance(ht[0], (list, tuple)):
                if data.get("platform") == "youtube":
                    analyzer.feed_youtube(ht)
                else:
                    analyzer.feed_tiktok(ht)
    else:
        # Try to load most recent reports
        yt_reports = be.list_reports("youtube_trends")
        tt_reports = be.list_reports("tiktok_trends")
        if yt_reports:
            d = be.load_report(yt_reports[0])
            analyzer.feed_youtube(d.get("hashtags", []))
        if tt_reports:
            d = be.load_report(tt_reports[0])
            analyzer.feed_tiktok(d.get("hashtags", []))
        if not yt_reports and not tt_reports:
            _skin.warning("No saved reports found. Run 'scrape all --save' first.")
            _skin.hint("Or use --from-report to specify a report file")
            return

    strategy = analyzer.build_post_strategy(effective_niche, platform, max_tags)

    if ctx.obj["json"]:
        click.echo(json.dumps(strategy, indent=2))
        return

    _skin.success(f"\nHashtag Strategy for #{effective_niche} on {platform.upper()}")

    _skin.info("\nPILLAR TAGS (use every post — broad reach):")
    if strategy["pillar_tags"]:
        _skin.table(
            ["Tag", "Competition", "Score"],
            [[f"#{s['tag']}", s["competition"], s["trend_score"]] for s in strategy["pillar_tags"]]
        )

    _skin.info("\nNICHE TAGS (core strategy — best ROI):")
    if strategy["niche_tags"]:
        _skin.table(
            ["Tag", "Competition", "Recommended Use"],
            [[f"#{s['tag']}", s["competition"], s["recommended_use"]] for s in strategy["niche_tags"][:10]]
        )

    _skin.info("\nMICRO TAGS (community building):")
    if strategy["micro_tags"]:
        click.echo("  " + "  ".join(f"#{s['tag']}" for s in strategy["micro_tags"]))

    click.echo()
    _skin.success("READY-TO-PASTE hashtag block:")
    click.echo(f"\n{strategy['ready_to_paste']}\n")

    path = be.save_report("hashtag_strategy", strategy)
    _skin.info(f"Strategy saved: {path}")


@hashtags.command("compare")
@click.argument("tags", nargs=-1)
@click.pass_context
def hashtags_compare(ctx: click.Context, tags: tuple) -> None:
    """Compare specific hashtags against scraped trend data."""
    be: SocialBackend = ctx.obj["backend"]
    from cli_anything.social_trends.core.hashtag_analyzer import HashtagAnalyzer
    analyzer = HashtagAnalyzer()

    yt_reports = be.list_reports("youtube_trends")
    tt_reports = be.list_reports("tiktok_trends")
    if yt_reports:
        analyzer.feed_youtube(be.load_report(yt_reports[0]).get("hashtags", []))
    if tt_reports:
        analyzer.feed_tiktok(be.load_report(tt_reports[0]).get("hashtags", []))

    results = analyzer.compare_tags(list(tags))
    headers = ["Tag", "Platform", "Mentions", "Competition", "Score", "Recommendation"]
    rows = [
        [f"#{r.tag}", r.platform, r.mention_count, r.competition, r.trend_score, r.recommended_use]
        for r in results
    ]
    _skin.table(headers, rows)


# ── Music ──────────────────────────────────────────────────────────────────

@main.group()
def music() -> None:
    """Track trending music and sounds."""


@music.command("trending")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "both"]), default="both")
@click.option("--limit", default=15, show_default=True)
@click.pass_context
def music_trending(ctx: click.Context, platform: str, limit: int) -> None:
    """Show trending music from saved scrape reports."""
    be: SocialBackend = ctx.obj["backend"]
    from cli_anything.social_trends.core.music_tracker import MusicTracker

    tracker = MusicTracker()
    yt_reports = be.list_reports("youtube_trends")
    tt_reports = be.list_reports("tiktok_trends")

    if yt_reports and platform in ("youtube", "both"):
        d = be.load_report(yt_reports[0])
        tracker.feed_youtube_tracks(d.get("music", []))

    if tt_reports and platform in ("tiktok", "both"):
        d = be.load_report(tt_reports[0])
        tracker.feed_tiktok_videos(d.get("videos", []))

    if not yt_reports and not tt_reports:
        _skin.warning("No saved reports. Run 'scrape all --save' first.")
        return

    if platform in ("tiktok", "both"):
        sounds = tracker.get_top_tiktok_sounds(limit)
        _skin.info(f"\nTop TikTok Sounds:")
        _skin.table(
            ["Rank", "Sound", "Artist", "Videos", "Velocity/day", "Niche", "Action"],
            [[i+1, t.title[:30], t.artist[:20], t.use_count,
              t.velocity, ", ".join(t.niche_affinity[:2]) or "general",
              t.recommendation[:35]] for i, t in enumerate(sounds)]
        )

    if platform in ("youtube", "both"):
        tracks = tracker.get_top_youtube_tracks(limit)
        _skin.info(f"\nTop YouTube Tracks:")
        _skin.table(
            ["Rank", "Title", "Artist", "Views", "Action"],
            [[i+1, t.title[:35], t.artist[:20], f"{t.est_reach:,}", t.recommendation[:30]]
             for i, t in enumerate(tracks)]
        )

    cross = tracker.get_cross_platform_tracks(5)
    if cross:
        _skin.success(f"\nCROSS-PLATFORM HITS (use immediately):")
        for t in cross:
            _skin.info(f"  {t.title} — {t.artist} | Reach: {t.est_reach:,}")


# ── Optimize ───────────────────────────────────────────────────────────────

@main.group()
def optimize() -> None:
    """Audit your accounts and generate optimization action plans."""


@optimize.command("account")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"]))
@click.argument("username")
@click.option("--channel-id", help="YouTube channel ID for API lookup")
@click.option("--niche", help="Override niche for this audit")
@click.pass_context
def optimize_account(
    ctx: click.Context, platform: str, username: str,
    channel_id: Optional[str], niche: Optional[str]
) -> None:
    """Run full optimization audit on a single account."""
    be: SocialBackend = ctx.obj["backend"]
    effective_niche = niche or be.config.default_niche

    from cli_anything.social_trends.core.account_optimizer import AccountOptimizer

    optimizer = AccountOptimizer()
    optimizer.set_niche(effective_niche)

    # Feed trending data from latest reports
    yt_reports = be.list_reports("youtube_trends")
    tt_reports = be.list_reports("tiktok_trends")
    all_tags: list[str] = []
    all_topics: list[str] = []
    if yt_reports:
        d = be.load_report(yt_reports[0])
        yt_tags = [t for t, _ in d.get("hashtags", [])[:30]]
        all_tags.extend(yt_tags)
        all_topics.extend([v["title"] for v in d.get("videos", [])[:10]])
    if tt_reports:
        d = be.load_report(tt_reports[0])
        tt_tags = [t for t, _ in d.get("hashtags", [])[:30]]
        all_tags.extend(tt_tags)
    optimizer.feed_trending_hashtags(list(dict.fromkeys(all_tags))[:50])
    optimizer.feed_trending_topics(all_topics[:15])

    if platform == "youtube":
        if not be.config.youtube_api_key:
            _skin.warning("No YouTube API key — using demo stats. Run 'setup youtube-key' for live data.")
            ch_stats = {
                "name": username, "description": f"A YouTube channel about {effective_niche}",
                "subscriber_count": 0, "view_count": 0, "video_count": 0,
                "custom_url": "", "country": be.config.default_region,
            }
            recent_videos: list[dict] = []
        else:
            from cli_anything.social_trends.core.youtube_scraper import YouTubeScraper
            yt = YouTubeScraper(be.config.youtube_api_key, be.config.default_region)
            cid = channel_id or (be.get_account("youtube", username) or object()).channel_id or ""
            if cid:
                with click.progressbar(length=2, label="Fetching channel data") as bar:
                    ch_stats = yt.get_channel_stats(cid)
                    bar.update(1)
                    recent_videos = yt.get_channel_videos(cid, 20)
                    bar.update(1)
            else:
                _skin.warning("No channel ID — provide --channel-id for live stats.")
                ch_stats = {"name": username, "description": "", "subscriber_count": 0,
                            "view_count": 0, "video_count": 0, "custom_url": ""}
                recent_videos = []
        audit = optimizer.audit_youtube_account(ch_stats, recent_videos, effective_niche)

    else:  # tiktok
        from cli_anything.social_trends.core.tiktok_scraper import TikTokScraper
        tt = TikTokScraper(use_playwright=be.config.use_playwright, ms_token=be.config.tiktok_ms_token)
        with click.progressbar(length=1, label="Fetching TikTok profile") as bar:
            tt_stats = tt.get_account_stats(username)
            bar.update(1)
        audit = optimizer.audit_tiktok_account(tt_stats, [], effective_niche)

    _print_audit(audit)
    report = {"audit": audit.__dict__}
    path = be.save_report(f"account_audit_{platform}_{username}", report)
    _skin.info(f"\nFull audit saved: {path}")


@optimize.command("all-accounts")
@click.option("--niche", help="Override niche for all audits")
@click.pass_context
def optimize_all(ctx: click.Context, niche: Optional[str]) -> None:
    """Run optimization audit on ALL registered accounts."""
    be: SocialBackend = ctx.obj["backend"]
    entries = be.list_accounts()
    if not entries:
        _skin.warning("No accounts registered. Add accounts with: accounts add <platform> <username>")
        return
    _skin.info(f"Auditing {len(entries)} accounts...")
    for entry in entries:
        _skin.info(f"\n{'─'*60}")
        _skin.info(f"Auditing {entry.platform.upper()} @{entry.username}...")
        ctx.invoke(
            optimize_account,
            platform=entry.platform,
            username=entry.username,
            channel_id=entry.channel_id,
            niche=niche or entry.niche,
        )


# ── Theme Page ─────────────────────────────────────────────────────────────

@main.group(name="theme-page")
def theme_page() -> None:
    """Theme page creation, conversion, and monetization playbook."""


@theme_page.command("plan")
@click.argument("niche")
@click.option("--platform", type=click.Choice(["tiktok", "youtube"]), default="tiktok")
@click.option("--followers", default=0, show_default=True, help="Current follower count")
@click.option("--page-name", default="YourPage", help="Your page/brand name")
@click.pass_context
def theme_page_plan(
    ctx: click.Context, niche: str, platform: str, followers: int, page_name: str
) -> None:
    """Generate a complete theme page creation and growth plan."""
    be: SocialBackend = ctx.obj["backend"]
    from cli_anything.social_trends.core.theme_page import ThemePageConverter

    converter = ThemePageConverter()

    # Feed latest trend data
    tt_reports = be.list_reports("tiktok_trends")
    if tt_reports:
        d = be.load_report(tt_reports[0])
        converter.set_trending_data(
            hashtags=[t for t, _ in d.get("hashtags", [])[:20]],
            sounds=d.get("sounds", [])[:10],
        )

    plan = converter.create_plan(niche, platform, followers, page_name)

    if ctx.obj["json"]:
        click.echo(json.dumps(plan.__dict__, indent=2, default=str))
        return

    _skin.success(f"\nTheme Page Plan: {niche.upper()} on {platform.upper()}")
    _skin.info(f"Current tier: {plan.current_milestone}")
    _skin.info(f"Next goal:    {plan.next_milestone}")

    _skin.info("\nCONTENT PILLARS:")
    for i, p in enumerate(plan.content_pillars, 1):
        click.echo(f"  {i}. {p}")

    _skin.info("\nWEEKLY CONTENT CALENDAR:")
    _skin.table(
        ["Day", "Content Type", "Sound", "Hashtags"],
        [[c["day"], c["content_type"], c["sound"][:25], " ".join(c["hashtags"][:3])]
         for c in plan.weekly_content_calendar]
    )

    _skin.info("\nMONETIZATION POTENTIAL:")
    rev = plan.monetization_potential_monthly
    click.echo(f"  YouTube AdSense: {rev.get('youtube_adsense_monthly','N/A')}/month")
    click.echo(f"  TikTok Fund:     {rev.get('tiktok_creator_fund_monthly','N/A')}/month")
    click.echo(f"  Affiliates:      {rev.get('affiliate_commissions_monthly','N/A')}/month")
    click.echo(f"  Brand Deals:     {rev.get('brand_deals_monthly','N/A')}/month")
    click.echo(f"  TOTAL ESTIMATE:  {rev.get('total_estimated_monthly','N/A')}/month")
    click.echo(f"  [{rev.get('note','')}]")

    _skin.info("\nMILESTONE ACTIONS:")
    for action in plan.milestone_actions:
        if action.strip():
            click.echo(f"  • {action}")

    _skin.info("\nEARLY GROWTH — Engagement Pod Strategy:")
    for tip in plan.engagement_pod_strategy[:4]:
        click.echo(f"  → {tip}")

    path = be.save_report(f"theme_page_plan_{niche}_{platform}", plan.__dict__)
    _skin.success(f"\nFull plan saved: {path}")


@theme_page.command("conversion-guide")
@click.argument("niche")
@click.pass_context
def theme_page_guide(ctx: click.Context, niche: str) -> None:
    """Full step-by-step guide to convert any account into a theme page."""
    from cli_anything.social_trends.core.theme_page import ThemePageConverter

    converter = ThemePageConverter()
    guide = converter.get_conversion_guide(niche)

    if ctx.obj["json"]:
        click.echo(json.dumps(guide, indent=2))
        return

    _skin.success(f"\nTheme Page Conversion Guide — {niche.upper()}\n")
    sections = [
        ("phase_1_account_reset", "PHASE 1 — Account Reset"),
        ("phase_2_content_strategy", "PHASE 2 — Content Strategy"),
        ("phase_3_growth_tactics", "PHASE 3 — Growth Tactics"),
        ("phase_4_monetization", "PHASE 4 — Monetization"),
        ("content_sourcing", "CONTENT SOURCING"),
        ("common_mistakes_to_avoid", "MISTAKES TO AVOID"),
    ]
    for key, label in sections:
        _skin.info(f"\n{label}:")
        for item in guide.get(key, []):
            click.echo(f"  • {item}")

    _skin.info("\nTIMELINE:")
    for period, milestone in guide.get("realistic_timeline", {}).items():
        click.echo(f"  {period}: {milestone}")

    _skin.info("\nTOOLS NEEDED:")
    for category, tools in guide.get("tools_needed", {}).items():
        click.echo(f"  {category.title()}: {', '.join(tools)}")


@theme_page.command("branding")
@click.argument("niche")
@click.argument("page_name")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), default="tiktok")
@click.pass_context
def theme_page_branding(ctx: click.Context, niche: str, page_name: str, platform: str) -> None:
    """Generate a branding checklist for your theme page."""
    from cli_anything.social_trends.core.theme_page import _branding_checklist

    checklist = _branding_checklist(platform, niche, page_name)
    _skin.success(f"\nBranding Checklist for @{page_name} ({niche.upper()} / {platform.upper()})\n")
    for i, item in enumerate(checklist, 1):
        click.echo(f"  [{' ' if i > 0 else 'x'}] {item}")


# ── Report ─────────────────────────────────────────────────────────────────

@main.group()
def report() -> None:
    """View and manage saved reports."""


@report.command("list")
@click.option("--type", "report_type", help="Filter by type: youtube_trends, tiktok_trends, hashtag_strategy, account_audit")
@click.pass_context
def report_list(ctx: click.Context, report_type: Optional[str]) -> None:
    """List saved reports."""
    be: SocialBackend = ctx.obj["backend"]
    reports = be.list_reports(report_type)
    if not reports:
        _skin.warning("No reports found. Run 'scrape all --save' to generate one.")
        return
    _skin.table(
        ["#", "Filename", "Size"],
        [[i + 1, p.name, f"{p.stat().st_size // 1024}KB"] for i, p in enumerate(reports[:20])]
    )


@report.command("show")
@click.argument("index_or_path")
@click.pass_context
def report_show(ctx: click.Context, index_or_path: str) -> None:
    """Show a specific report (by index from 'report list' or file path)."""
    be: SocialBackend = ctx.obj["backend"]
    try:
        idx = int(index_or_path) - 1
        reports = be.list_reports()
        path = reports[idx]
    except (ValueError, IndexError):
        path = Path(index_or_path)
    if not path.exists():
        _skin.error(f"Report not found: {path}")
        return
    data = be.load_report(path)
    click.echo(json.dumps(data, indent=2, default=str))


# ── Status ─────────────────────────────────────────────────────────────────

@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current configuration and account status."""
    be: SocialBackend = ctx.obj["backend"]
    info = be.status()

    if ctx.obj["json"]:
        click.echo(json.dumps(info, indent=2))
        return

    _skin.print_banner()
    _skin.table(
        ["Setting", "Value"],
        [
            ["Config dir", info["config_dir"]],
            ["YouTube API", "✓ Configured" if info["youtube_api_configured"] else "✗ Not set (run: setup youtube-key)"],
            ["TikTok token", "✓ Configured" if info["tiktok_token_configured"] else "✗ Not set (run: setup tiktok-token)"],
            ["Region", info["default_region"]],
            ["Default niche", info["default_niche"]],
            ["Registered accounts", info["accounts"]],
            ["Saved reports", info["saved_reports"]],
        ]
    )
    accounts = be.list_accounts()
    if accounts:
        _skin.info("\nRegistered accounts:")
        for a in accounts:
            click.echo(f"  • {a.platform}: @{a.username} (niche: {a.niche or 'default'})")


# ── REPL ───────────────────────────────────────────────────────────────────

def _launch_repl(be: SocialBackend) -> None:
    _skin.print_banner()
    _skin.info("Interactive mode. Type 'help' to list commands or 'exit' to quit.\n")
    try:
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        session = PromptSession(history=FileHistory(str(be.history_path)))
        while True:
            try:
                line = session.prompt(_skin.prompt("social-trends")).strip()
            except (KeyboardInterrupt, EOFError):
                break
            if not line:
                continue
            if line.lower() in ("exit", "quit", "q"):
                break
            if line.lower() == "help":
                _print_help()
                continue
            args = line.split()
            try:
                main.main(args, standalone_mode=False, obj={"backend": be, "json": False})
            except SystemExit:
                pass
            except Exception as exc:
                _skin.error(str(exc))
    except ImportError:
        _skin.warning("prompt-toolkit not installed — run commands directly (cli-anything-social-trends <cmd>)")
    _skin.print_goodbye()


def _print_help() -> None:
    click.echo("""
Available commands:
  setup youtube-key <KEY>          Set YouTube Data API v3 key
  setup tiktok-token <TOKEN>       Set TikTok session token
  setup region <CODE>              Set region (US, GB, AU, CA...)
  setup niche <NICHE>              Set default niche

  accounts add <platform> <user>   Register an account
  accounts list                    List all accounts

  scrape youtube --trending        Scrape YouTube trending videos
  scrape tiktok --trending         Scrape TikTok trending videos
  scrape all                       Scrape both platforms (saves report)

  hashtags strategy                Build hashtag posting strategy
  hashtags compare #tag1 #tag2     Compare specific hashtags

  music trending                   Show trending sounds & tracks

  optimize account <platform> <user>  Audit a single account
  optimize all-accounts            Audit all registered accounts

  theme-page plan <niche>          Generate theme page growth plan
  theme-page conversion-guide <niche>  Full theme page setup guide
  theme-page branding <niche> <name>   Branding checklist

  report list                      List saved reports
  report show <index>              View a saved report

  status                           Show configuration status
""")


def _print_audit(audit) -> None:
    _skin.info(f"\n{'═'*60}")
    _skin.info(f"ACCOUNT AUDIT: {audit.platform.upper()} @{audit.username}")
    _skin.info(f"{'═'*60}")
    _skin.table(["Metric", "Value"], [
        ["Niche", audit.niche],
        ["Followers/Subs", f"{audit.follower_count:,}"],
        ["Tier", audit.tier],
        ["Your ER", f"{audit.current_er}%"],
        ["Benchmark ER", f"{audit.benchmark_er}%"],
        ["ER vs Benchmark", audit.er_vs_benchmark],
        ["Bio Score", f"{audit.bio_score}/100"],
        ["Overall Score", f"{audit.score}/100"],
    ])
    if audit.bio_suggestions:
        _skin.info("\nBIO IMPROVEMENTS:")
        for tip in audit.bio_suggestions:
            click.echo(f"  • {tip}")
    _skin.info("\nOPTIMAL POSTING SCHEDULE:")
    sched = audit.posting_schedule
    click.echo(f"  Days:  {', '.join(sched.get('days', []))}")
    click.echo(f"  Times: {', '.join(str(h) + ':00 UTC' for h in sched.get('hours_utc', []))}")
    if audit.content_gaps:
        _skin.warning(f"\nCONTENT GAPS ({len(audit.content_gaps)} missing trends):")
        for gap in audit.content_gaps[:8]:
            click.echo(f"  ⚠ {gap}")
    _skin.success("\nQUICK WINS (do this week):")
    for i, win in enumerate(audit.quick_wins, 1):
        click.echo(f"  {i}. {win}")
    _skin.info("\nCROSS-PLATFORM TIPS:")
    for tip in audit.cross_platform_tips[:3]:
        click.echo(f"  → {tip}")
