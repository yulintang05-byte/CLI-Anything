"""social-trends CLI — Agent-native social media trend intelligence tool.

Scrapes YouTube and TikTok for viral trends, hashtags, and music.
Optimizes social media accounts. Provides theme page conversion playbooks.

Usage:
    python3 -m cli_anything.social_trends [--json] <command>
    python3 -m cli_anything.social_trends  (launches REPL)
"""

import json
import sys
import shlex
import click
from typing import Any, Optional

from cli_anything.social_trends.core.session import Session
from cli_anything.social_trends.core import trends as trends_mod
from cli_anything.social_trends.core import hashtags as hashtags_mod
from cli_anything.social_trends.core import music as music_mod
from cli_anything.social_trends.core import accounts as accounts_mod
from cli_anything.social_trends.core import theme_pages as theme_mod


# ── Global state ───────────────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False


def get_session() -> Session:
    global _session
    if _session is None:
        _session = Session()
    return _session


# ── Output helpers ─────────────────────────────────────────────────────────────

def output(data: Any, message: str = "") -> None:
    if _json_output:
        click.echo(json.dumps(data, indent=2, default=str))
    else:
        if message:
            click.echo(message)
        _pretty(data)


def _pretty(data: Any, indent: int = 2) -> None:
    pad = " " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                click.echo(f"{pad}{k}:")
                _pretty(v, indent + 2)
            else:
                click.echo(f"{pad}{k}: {v}")
    elif isinstance(data, list):
        if not data:
            click.echo(f"{pad}(empty)")
            return
        for item in data:
            if isinstance(item, dict):
                parts = "  ".join(f"{k}={v}" for k, v in item.items() if not isinstance(v, (dict, list)))
                click.echo(f"{pad}- {parts}")
            else:
                click.echo(f"{pad}- {item}")
    else:
        click.echo(f"{pad}{data}")


def _err(msg: str) -> None:
    if _json_output:
        click.echo(json.dumps({"error": msg}))
    else:
        click.echo(f"[error] {msg}", err=True)


def _ok(msg: str) -> None:
    if not _json_output:
        click.echo(f"[ok] {msg}")


# ── Root group ─────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.option("--json", "use_json", is_flag=True, help="Output results as JSON")
@click.option("--platform", default=None, help="Set active platform: tiktok | youtube | all")
@click.pass_context
def cli(ctx: click.Context, use_json: bool, platform: Optional[str]) -> None:
    """social-trends: viral trend intelligence for TikTok, YouTube & Instagram.

    \b
    Commands:
      trends   fetch     Fetch viral trends
      trends   insights  Summarize trend data
      hashtags mix       Get optimized hashtag mix for a niche
      hashtags audit     Audit a list of hashtags
      hashtags caption   Build a caption with hashtag block
      music    fetch     Get trending music / sounds
      music    recommend Recommend music for a niche
      account  add       Register an account profile
      account  audit     Full account optimization audit
      account  schedule  Recommended posting schedule
      account  bio-audit Audit account bio
      theme    list      List theme page blueprints
      theme    show      Show a full blueprint
      theme    monetize  Monetization playbook
      theme    assess    Assess account for conversion
      theme    roadmap   Growth phase roadmap
      status             Show session status
      cache    clear     Clear HTTP response cache
    """
    global _json_output
    _json_output = use_json

    sess = get_session()
    if platform:
        sess.set_platform(platform)

    if ctx.invoked_subcommand is None:
        _launch_repl()


# ── trends group ───────────────────────────────────────────────────────────────

@cli.group()
def trends() -> None:
    """Fetch and analyze viral trends from YouTube and TikTok."""


@trends.command("fetch")
@click.option("--platform", "-p", default="all", show_default=True,
              type=click.Choice(["youtube", "tiktok", "all"], case_sensitive=False),
              help="Platform(s) to fetch from")
@click.option("--region", "-r", default="us", show_default=True, help="Region code (us, uk, ca, au, in, ...)")
@click.option("--category", "-c", default="all", show_default=True,
              help="Category: all, music, gaming, news, sports, entertainment, tech")
@click.option("--limit", "-n", default=20, show_default=True, help="Max results per platform")
@click.option("--apify-key", envvar="APIFY_KEY", default=None, help="Apify API key for production TikTok scraping")
def trends_fetch(platform: str, region: str, category: str, limit: int, apify_key: Optional[str]) -> None:
    """Fetch viral trending content from YouTube and/or TikTok."""
    sess = get_session()
    active_platform = platform if platform != "all" else (sess.active_platform or "all")
    try:
        items = trends_mod.fetch_trending(
            platform=active_platform,
            region=region,
            category=category,
            limit=limit,
            apify_key=apify_key,
        )
        sess.trend_cache = items
        if _json_output:
            output(items)
        else:
            click.echo(f"\nFetched {len(items)} trending items ({active_platform.upper()}, region={region.upper()})\n")
            for i, item in enumerate(items, 1):
                views = f"{item.get('views', 0):,}"
                tags = ", ".join(f"#{t}" for t in item.get("hashtags", [])[:3])
                music = item.get("music", "")
                click.echo(f"  {i:2}. [{item['platform'].upper()}] {item['title'][:60]}")
                click.echo(f"       views={views}  creator=@{item.get('creator', 'n/a')}  music={music[:40] or 'n/a'}")
                if tags:
                    click.echo(f"       tags={tags}")
                click.echo()
    except RuntimeError as e:
        _err(str(e))
        sys.exit(1)


@trends.command("insights")
def trends_insights() -> None:
    """Summarize cached trend data: top hashtags, music, creators."""
    sess = get_session()
    if not sess.trend_cache:
        _err("No trend data cached. Run `trends fetch` first.")
        sys.exit(1)
    insights = trends_mod.extract_trend_insights(sess.trend_cache)
    output(insights, "\nTrend Insights\n" + "─" * 40)


# ── hashtags group ─────────────────────────────────────────────────────────────

@cli.group()
def hashtags() -> None:
    """Hashtag strategy: mix generation, auditing, and caption building."""


@hashtags.command("mix")
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok", show_default=True,
              type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@click.option("--count", "-n", default=5, show_default=True, help="Number of hashtags")
@click.option("--no-boosters", is_flag=True, help="Exclude platform booster tags (fyp, viral)")
def hashtags_mix(niche: str, platform: str, count: int, no_boosters: bool) -> None:
    """Get an optimized hashtag mix for a content niche.

    NICHE: e.g. fitness, fashion, food, travel, beauty, finance, gaming, ...
    """
    tags = hashtags_mod.get_hashtag_mix(
        niche=niche, platform=platform, count=count,
        include_platform_boosters=not no_boosters,
    )
    if _json_output:
        output({"niche": niche, "platform": platform, "hashtags": tags})
    else:
        click.echo(f"\nOptimized {niche} hashtag mix for {platform.upper()} ({len(tags)} tags):")
        click.echo("  " + " ".join(f"#{t}" for t in tags))
        click.echo()


@hashtags.command("audit")
@click.argument("tags", nargs=-1, required=True)
def hashtags_audit(tags: tuple) -> None:
    """Audit a list of hashtags and score them.

    TAGS: space-separated list (# prefix optional): fitness viral gym fyp
    """
    clean_tags = [t.lstrip("#") for t in tags]
    result = hashtags_mod.audit_hashtags(clean_tags)
    output(result, f"\nHashtag Audit: {', '.join('#'+t for t in clean_tags)}\n" + "─" * 40)


@hashtags.command("caption")
@click.argument("text")
@click.argument("niche")
@click.option("--platform", "-p", default="tiktok", show_default=True)
def hashtags_caption(text: str, niche: str, platform: str) -> None:
    """Build an optimized caption with hashtag block.

    TEXT: Caption text (quote it if multi-word).
    NICHE: Content niche for hashtag selection.
    """
    tags = hashtags_mod.get_hashtag_mix(niche=niche, platform=platform, count=5)
    caption = hashtags_mod.build_caption(text, tags, platform)
    if _json_output:
        output({"caption": caption, "hashtags": tags})
    else:
        click.echo(f"\nCaption ({platform.upper()}):\n")
        click.echo(caption)
        click.echo()


@hashtags.command("niches")
def hashtags_niches() -> None:
    """List all available content niches with pre-built hashtag sets."""
    niches = hashtags_mod.list_niches()
    if _json_output:
        output(niches)
    else:
        click.echo("\nAvailable niches:")
        for n in niches:
            click.echo(f"  • {n}")
        click.echo()


# ── music group ────────────────────────────────────────────────────────────────

@cli.group()
def music() -> None:
    """Trending music and sound discovery."""


@music.command("fetch")
@click.option("--source", "-s", default="all", show_default=True,
              type=click.Choice(["apple", "billboard", "tiktok", "all"], case_sensitive=False),
              help="Music chart source")
@click.option("--limit", "-n", default=20, show_default=True)
def music_fetch(source: str, limit: int) -> None:
    """Fetch trending music from Apple Music, Billboard, and TikTok sounds."""
    sess = get_session()
    items = music_mod.fetch_trending_music(
        source=source, limit=limit,
        trend_items=sess.trend_cache if source in ("tiktok", "all") else None,
    )
    sess.music_cache = items
    if _json_output:
        output(items)
    else:
        click.echo(f"\nTrending Music ({source.upper()}, top {len(items)})\n" + "─" * 50)
        for i, item in enumerate(items, 1):
            uses = f"  {item.get('tiktok_uses', 0):,} uses" if item.get("tiktok_uses") else ""
            click.echo(f"  {i:2}. {item['title'][:40]:40} — {item['artist'][:25]}")
            click.echo(f"       mood={item.get('mood', 'n/a')}  bpm={item.get('bpm_range', 'varies')}  genre={item.get('genre', 'n/a')}{uses}")
        click.echo()


@music.command("recommend")
@click.argument("niche")
def music_recommend(niche: str) -> None:
    """Recommend trending music for a specific content niche.

    NICHE: e.g. fitness, fashion, food, travel, beauty, gaming, ...
    """
    sess = get_session()
    if not sess.music_cache:
        # Auto-fetch if cache is empty
        sess.music_cache = music_mod.fetch_trending_music(source="all", limit=30, trend_items=sess.trend_cache)
    recs = music_mod.recommend_music_for_niche(niche, sess.music_cache)
    if _json_output:
        output(recs)
    else:
        click.echo(f"\nRecommended music for '{niche}' content:\n")
        for i, item in enumerate(recs, 1):
            click.echo(f"  {i:2}. {item['title'][:40]:40} — {item['artist'][:25]}  [{item.get('mood', 'n/a')}]")
        click.echo()


# ── account group ──────────────────────────────────────────────────────────────

@cli.group()
def account() -> None:
    """Account management and optimization."""


@account.command("add")
@click.argument("username")
@click.argument("platform", type=click.Choice(["tiktok", "instagram", "youtube"], case_sensitive=False))
@click.option("--followers", default=0, type=int)
@click.option("--bio", default="", help="Account bio text")
@click.option("--has-link/--no-link", default=False)
@click.option("--niche", default="", help="Content niche")
@click.option("--avg-views", default=0, type=int)
@click.option("--avg-likes", default=0, type=int)
@click.option("--avg-comments", default=0, type=int)
@click.option("--posts-per-week", default=0, type=int)
@click.option("--type", "account_type", default="creator",
              type=click.Choice(["personal", "creator", "business", "theme_page"]))
@click.option("--monetization", default="", help="Current monetization: affiliate, tiktok_shop, brand_deals, ...")
def account_add(username: str, platform: str, followers: int, bio: str, has_link: bool,
                niche: str, avg_views: int, avg_likes: int, avg_comments: int,
                posts_per_week: int, account_type: str, monetization: str) -> None:
    """Register an account profile for auditing and optimization."""
    sess = get_session()
    profile = accounts_mod.create_account(
        username=username, platform=platform, followers=followers, bio=bio,
        has_link=has_link, niche=niche, avg_views=avg_views, avg_likes=avg_likes,
        avg_comments=avg_comments, post_frequency_per_week=posts_per_week,
        account_type=account_type, monetization=monetization,
    )
    sess.set_account(profile)
    if platform:
        sess.set_platform(platform)
    if niche:
        sess.set_niche(niche)
    _ok(f"Account @{username} ({platform}) registered.")
    output(profile)


@account.command("audit")
@click.argument("username", required=False)
def account_audit(username: Optional[str]) -> None:
    """Run a full optimization audit on the active account (or specify username)."""
    sess = get_session()
    profile = sess.active_account
    if profile is None:
        _err("No account registered. Run `account add` first.")
        sys.exit(1)
    result = accounts_mod.full_audit(profile)
    if _json_output:
        output(result)
    else:
        click.echo(f"\nAccount Audit: @{result['username']} ({result['platform'].upper()})")
        click.echo(f"Overall Score: {result['overall_score']}/100  Grade: {result['grade']}\n")
        click.echo("Bio:")
        click.echo(f"  Score: {result['bio_audit']['score']}/100  Issues: {len(result['bio_audit']['issues'])}")
        for issue in result['bio_audit']['issues']:
            click.echo(f"    ⚠  {issue}")
        click.echo("\nEngagement:")
        eng = result['engagement']
        click.echo(f"  Actual: {eng['actual_rate_pct']}%  Benchmark: {eng['benchmark_rate_pct']}%  Status: {eng['status']}")
        click.echo(f"  {eng['note']}")
        click.echo("\nPriority Actions:")
        for j, action in enumerate(result['priority_actions'], 1):
            click.echo(f"  {j}. {action}")
        click.echo("\nRecommended Link-in-Bio Tools:")
        for tool in result['link_in_bio']:
            click.echo(f"  • {tool['name']} ({tool['url']}) — {tool['best_for']}")
        click.echo()


@account.command("schedule")
@click.option("--platform", "-p", default=None, help="Platform override")
@click.option("--freq", default=0, type=int, help="Current posts per week")
def account_schedule(platform: Optional[str], freq: int) -> None:
    """Show recommended posting schedule with peak times."""
    sess = get_session()
    plat = platform or sess.active_platform or "tiktok"
    result = accounts_mod.recommend_schedule(plat, frequency_per_week=freq)
    if _json_output:
        output(result)
    else:
        click.echo(f"\nPosting Schedule: {plat.upper()}")
        click.echo(f"Recommended: {result['recommended_frequency']}")
        click.echo(f"Timezone: {result['timezone_note']}\n")
        for day, times in result['peak_times'].items():
            click.echo(f"  {day.upper()}: {', '.join(times)}")
        if result['issues']:
            click.echo("\nIssues:")
            for issue in result['issues']:
                click.echo(f"  ⚠  {issue}")
        click.echo()


@account.command("bio-audit")
@click.argument("bio")
@click.option("--platform", "-p", default="tiktok")
@click.option("--has-link/--no-link", default=False)
def account_bio_audit(bio: str, platform: str, has_link: bool) -> None:
    """Audit a bio string for optimization opportunities."""
    result = accounts_mod.audit_bio(bio, has_link, platform)
    output(result, f"\nBio Audit ({platform.upper()})\n" + "─" * 40)


# ── theme group ────────────────────────────────────────────────────────────────

@cli.group()
def theme() -> None:
    """Theme page creation and monetization playbooks."""


@theme.command("list")
@click.option("--difficulty", default=None,
              type=click.Choice(["easy", "medium", "hard"], case_sensitive=False),
              help="Filter by difficulty")
def theme_list(difficulty: Optional[str]) -> None:
    """List all available theme page blueprints."""
    blueprints = theme_mod.list_blueprints()
    if difficulty:
        blueprints = [b for b in blueprints if b["difficulty"] == difficulty.lower()]
    if _json_output:
        output(blueprints)
    else:
        click.echo(f"\nTheme Page Blueprints ({len(blueprints)} available):\n")
        for bp in blueprints:
            click.echo(f"  [{bp['difficulty'].upper():6}] {bp['name']:35} — {bp['niche']}")
        click.echo()


@theme.command("show")
@click.argument("name")
def theme_show(name: str) -> None:
    """Show a full theme page blueprint with content pillars and growth hacks.

    NAME: Blueprint name or niche keyword (partial match).
    """
    bp = theme_mod.get_blueprint(name)
    if bp is None:
        _err(f"Blueprint not found for '{name}'. Run `theme list` to see all options.")
        sys.exit(1)
    if _json_output:
        output(bp)
    else:
        click.echo(f"\n{'─'*60}")
        click.echo(f"THEME PAGE: {bp['name']}")
        click.echo(f"{'─'*60}")
        click.echo(f"Niche:       {bp['niche']}")
        click.echo(f"Aesthetic:   {bp['aesthetic']}")
        click.echo(f"Audience:    {bp['target_audience']}")
        click.echo(f"Difficulty:  {bp['difficulty'].upper()}")
        click.echo(f"Frequency:   {bp['posting_frequency']}")
        click.echo(f"Music vibe:  {bp['music_vibe']}")
        click.echo(f"\nContent Pillars:")
        for pillar in bp['content_pillars']:
            click.echo(f"  • {pillar}")
        click.echo(f"\nHashtag Strategy: {' '.join('#'+t for t in bp['hashtag_strategy'])}")
        click.echo(f"\nMonetization Priority:")
        for i, mon in enumerate(bp['monetization_priority'], 1):
            click.echo(f"  {i}. {mon}")
        click.echo(f"\nGrowth Hack: {bp['growth_hack']}")
        click.echo(f"Study:       {', '.join('@'+c for c in bp['competitors_to_study'])}")
        click.echo()


@theme.command("monetize")
@click.argument("strategy",
                type=click.Choice(["affiliate", "tiktok_shop", "paid_shoutouts",
                                   "digital_products", "brand_deals"], case_sensitive=False))
def theme_monetize(strategy: str) -> None:
    """Get the step-by-step monetization playbook for a strategy."""
    playbook = theme_mod.get_monetization_playbook(strategy)
    if playbook is None:
        _err(f"No playbook for '{strategy}'.")
        sys.exit(1)
    if _json_output:
        output(playbook)
    else:
        click.echo(f"\n{'─'*60}")
        click.echo(f"MONETIZATION: {playbook['name']}")
        click.echo(f"{'─'*60}")
        click.echo(f"Potential:    {playbook['monthly_potential']}/month")
        click.echo(f"Requirements: {playbook['requirements']}")
        click.echo(f"Platforms:    {', '.join(playbook['platforms'])}")
        click.echo(f"\nStep-by-Step:")
        for step in playbook['steps']:
            click.echo(f"  {step}")
        click.echo(f"\nBest Niches: {', '.join(playbook['best_niches'])}")
        click.echo(f"\nPro Tip: {playbook['pro_tip']}")
        click.echo()


@theme.command("assess")
@click.option("--followers", default=0, type=int, required=True)
@click.option("--niche", default="lifestyle", show_default=True)
@click.option("--has-link/--no-link", default=False)
def theme_assess(followers: int, niche: str, has_link: bool) -> None:
    """Assess what monetization strategies your account is ready for."""
    result = theme_mod.assess_account_for_conversion(followers, niche, has_link)
    output(result, f"\nConversion Assessment ({followers:,} followers, {niche})\n" + "─" * 40)


@theme.command("roadmap")
@click.argument("phase", type=click.Choice(["0_to_1k", "1k_to_10k", "10k_to_100k"]))
def theme_roadmap(phase: str) -> None:
    """Get the growth phase roadmap for a follower milestone.

    PHASE: 0_to_1k | 1k_to_10k | 10k_to_100k
    """
    data = theme_mod.get_growth_phase(phase)
    if _json_output:
        output(data)
    else:
        click.echo(f"\n{'─'*60}")
        click.echo(f"ROADMAP: {data['label']}")
        click.echo(f"Timeline: {data['timeline']}")
        click.echo(f"Focus:    {data['focus']}")
        click.echo(f"\nAction Plan:")
        for action in data['actions']:
            click.echo(f"  • {action}")
        click.echo(f"\nKPIs to Track:")
        for kpi in data['kpis']:
            click.echo(f"  ◦ {kpi}")
        click.echo()


# ── status & cache ─────────────────────────────────────────────────────────────

@cli.command("status")
def status() -> None:
    """Show current session state."""
    sess = get_session()
    output(sess.status(), "\nSession Status\n" + "─" * 30)


@cli.group()
def cache() -> None:
    """Manage HTTP response cache."""


@cache.command("clear")
def cache_clear() -> None:
    """Clear all cached HTTP responses."""
    from cli_anything.social_trends.utils.social_backend import clear_cache
    removed = clear_cache()
    _ok(f"Cleared {removed} cached responses.")


# ── REPL ───────────────────────────────────────────────────────────────────────

_BANNER = """\
╔══════════════════════════════════════════════════════╗
║          social-trends  v1.0.0                       ║
║  Viral trend intelligence: TikTok · YouTube · IG     ║
║  Type 'help' for commands, 'exit' to quit            ║
╚══════════════════════════════════════════════════════╝"""

_HELP_TEXT = """\
Commands:
  trends fetch [--platform] [--region] [--category] [--limit]
  trends insights
  hashtags mix <niche> [--platform] [--count]
  hashtags audit <tag1> <tag2> ...
  hashtags caption <"text"> <niche>
  hashtags niches
  music fetch [--source] [--limit]
  music recommend <niche>
  account add <username> <platform> [options]
  account audit
  account schedule [--platform]
  account bio-audit <"bio text"> [--has-link]
  theme list [--difficulty]
  theme show <name-or-niche>
  theme monetize <affiliate|tiktok_shop|paid_shoutouts|digital_products|brand_deals>
  theme assess --followers N --niche NICHE
  theme roadmap <0_to_1k|1k_to_10k|10k_to_100k>
  status
  cache clear
  exit / quit"""


def _launch_repl() -> None:
    click.echo(_BANNER)
    sess = get_session()

    while True:
        try:
            prompt = f"social-trends"
            if sess.active_niche:
                prompt += f"[{sess.active_niche}]"
            prompt += "> "
            line = click.prompt(prompt, default="", show_default=False).strip()
        except (EOFError, KeyboardInterrupt):
            click.echo("\nBye.")
            break

        if not line:
            continue
        if line.lower() in ("exit", "quit", "q"):
            click.echo("Bye.")
            break
        if line.lower() in ("help", "?", "h"):
            click.echo(_HELP_TEXT)
            continue

        sess.log(line)
        try:
            args = shlex.split(line)
            cli.main(args=args, standalone_mode=False)
        except SystemExit:
            pass
        except Exception as e:
            _err(str(e))


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    cli()


if __name__ == "__main__":
    main()
