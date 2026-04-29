"""CLI-Anything Social Trends — main Click CLI definition."""

import json as _json
import sys
import click
from tabulate import tabulate

from .core import youtube, tiktok, account_optimizer, theme_pages
from .utils.social_backend import SocialSession, load_session, save_session


# ── Root group ────────────────────────────────────────────────────────────────

@click.group()
@click.option("--json", "output_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def cli(ctx: click.Context, output_json: bool):
    """CLI-Anything Social Trends: scrape viral trends, optimize accounts, build theme pages."""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json


# ── trends group ──────────────────────────────────────────────────────────────

@cli.group()
def trends():
    """Scrape trending content, hashtags, and music from YouTube and TikTok."""


@trends.command("youtube")
@click.option("--region", default="US", show_default=True, help="ISO 3166-1 country code")
@click.option("--max", "max_results", default=25, show_default=True, type=int)
@click.option("--category", default=None, help="YouTube category ID (10=Music, 24=Entertainment, etc.)")
@click.pass_context
def trends_youtube(ctx: click.Context, region: str, max_results: int, category: str):
    """Get trending YouTube videos with hashtags and engagement data."""
    try:
        videos = youtube.get_trending_videos(region, max_results, category)
        if ctx.obj["json"]:
            click.echo(_json.dumps(videos, indent=2))
        else:
            rows = [
                [
                    v["title"][:55],
                    v["channel"][:25],
                    f"{v['views']:,}",
                    f"{v['likes']:,}",
                    ", ".join(f"#{t}" for t in v["hashtags"][:3]) or "—",
                    v["url"],
                ]
                for v in videos
            ]
            click.echo(tabulate(rows, headers=["Title", "Channel", "Views", "Likes", "Top Hashtags", "URL"]))
    except RuntimeError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@trends.command("tiktok")
@click.option("--max", "max_results", default=20, show_default=True, type=int)
@click.option("--hashtag", default=None, help="Filter by specific hashtag")
@click.pass_context
def trends_tiktok(ctx: click.Context, max_results: int, hashtag: str):
    """Get trending TikTok videos with hashtag and sound data."""
    videos = tiktok.get_trending_videos(hashtag, max_results)
    if ctx.obj["json"]:
        click.echo(_json.dumps(videos, indent=2))
    else:
        rows = [
            [
                v.get("description", "")[:55],
                v.get("author", "")[:20],
                f"{v.get('views', 0):,}",
                f"{v.get('likes', 0):,}",
                v.get("music_title", "—")[:30],
                ", ".join(f"#{t}" for t in v.get("hashtags", [])[:3]) or "—",
            ]
            for v in videos
        ]
        click.echo(tabulate(rows, headers=["Description", "Author", "Views", "Likes", "Sound", "Hashtags"]))


@trends.command("combined")
@click.option("--niche", default=None, help="Niche/keyword to focus on")
@click.option("--region", default="US", show_default=True)
@click.pass_context
def trends_combined(ctx: click.Context, niche: str, region: str):
    """Cross-platform trend report: top hashtags and sounds from both platforms."""
    result: dict = {}

    yt_hashtags: list = []
    try:
        yt_hashtags = youtube.get_trending_hashtags(region_code=region, max_results=50)
        result["youtube_hashtags"] = yt_hashtags[:15]
    except Exception as e:
        result["youtube_hashtags"] = []
        result["youtube_error"] = str(e)

    tt_hashtags = tiktok.get_trending_hashtags(max_results=20)
    tt_sounds = tiktok.get_trending_sounds(max_results=10)
    result["tiktok_hashtags"] = tt_hashtags
    result["tiktok_trending_sounds"] = tt_sounds

    if niche:
        result["niche_trends"] = tiktok.get_niche_trends(niche)

    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo("\n=== TRENDING HASHTAGS — YOUTUBE ===")
        if yt_hashtags:
            rows = [[h["hashtag"], f"{h['video_count']}", f"{h['avg_views']:,}"] for h in yt_hashtags[:10]]
            click.echo(tabulate(rows, headers=["Hashtag", "Videos", "Avg Views"]))
        click.echo("\n=== TRENDING HASHTAGS — TIKTOK ===")
        if tt_hashtags:
            rows = [[h["hashtag"], f"{h.get('video_count', 0)}", f"{h.get('avg_views', 0):,}"] for h in tt_hashtags[:10]]
            click.echo(tabulate(rows, headers=["Hashtag", "Videos", "Avg Views"]))
        click.echo("\n=== TRENDING SOUNDS — TIKTOK ===")
        if tt_sounds:
            rows = [[s.get("title", s.get("music_id", "?")), s.get("author", ""), f"{s.get('video_count', 0)}", s.get("tiktok_url", "")] for s in tt_sounds[:10]]
            click.echo(tabulate(rows, headers=["Sound", "Artist", "Videos", "URL"]))


# ── hashtags group ────────────────────────────────────────────────────────────

@cli.group()
def hashtags():
    """Research, analyze, and track hashtag performance."""


@hashtags.command("trending")
@click.option("--platform", type=click.Choice(["youtube", "tiktok", "both"]), default="both")
@click.option("--region", default="US", show_default=True)
@click.option("--max", "max_results", default=20, show_default=True, type=int)
@click.pass_context
def hashtags_trending(ctx: click.Context, platform: str, region: str, max_results: int):
    """Get currently trending hashtags by platform."""
    result: dict = {}
    if platform in ("youtube", "both"):
        try:
            result["youtube"] = youtube.get_trending_hashtags(region, max_results)
        except Exception as e:
            result["youtube_error"] = str(e)
    if platform in ("tiktok", "both"):
        result["tiktok"] = tiktok.get_trending_hashtags(max_results)

    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        for p, items in result.items():
            if isinstance(items, list):
                click.echo(f"\n=== {p.upper()} TRENDING HASHTAGS ===")
                rows = [[h["hashtag"], h.get("video_count", "—"), f"{h.get('avg_views', 0):,}"] for h in items]
                click.echo(tabulate(rows, headers=["Hashtag", "Videos", "Avg Views"]))


@hashtags.command("analyze")
@click.argument("hashtag")
@click.option("--platform", type=click.Choice(["youtube", "tiktok"]), default="youtube")
@click.option("--max", "max_results", default=20, show_default=True, type=int)
@click.pass_context
def hashtags_analyze(ctx: click.Context, hashtag: str, platform: str, max_results: int):
    """Analyze performance data for a specific hashtag."""
    if platform == "youtube":
        try:
            result = youtube.analyze_hashtag(hashtag, max_results)
        except RuntimeError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
    else:
        videos = tiktok.search_by_keyword(hashtag, max_results)
        total_views = sum(v.get("views", 0) for v in videos)
        result = {
            "hashtag": hashtag,
            "platform": platform,
            "video_count": len(videos),
            "total_views": total_views,
            "avg_views": total_views // max(len(videos), 1),
            "top_videos": videos[:5],
        }

    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo(f"\nHashtag: {result['hashtag']}")
        click.echo(f"Videos analyzed: {result['video_count']}")
        click.echo(f"Total views: {result.get('total_views', 0):,}")
        click.echo(f"Avg views: {result.get('avg_views', 0):,}")
        if result.get("top_videos"):
            click.echo("\nTop Videos:")
            rows = [[v.get("title", v.get("description", ""))[:60], f"{v.get('views', 0):,}"] for v in result["top_videos"]]
            click.echo(tabulate(rows, headers=["Title/Description", "Views"]))


@hashtags.command("research")
@click.argument("niche")
@click.option("--platform", type=click.Choice(["tiktok", "youtube"]), default="tiktok")
@click.pass_context
def hashtags_research(ctx: click.Context, niche: str, platform: str):
    """Research optimal hashtags for a niche."""
    starter = theme_pages._starter_hashtags(niche)
    if platform == "youtube":
        try:
            niche_videos = youtube.search_trending_by_niche(niche, max_results=20)
            found_hashtags: list[str] = []
            for v in niche_videos:
                found_hashtags.extend(v.get("hashtags", []))
            unique = list(dict.fromkeys(found_hashtags))[:15]
            result = {"niche": niche, "platform": platform, "discovered_hashtags": [f"#{t}" for t in unique], "starter_pack": starter}
        except Exception as e:
            result = {"niche": niche, "error": str(e), "starter_pack": starter}
    else:
        niche_data = tiktok.get_niche_trends(niche)
        result = {
            "niche": niche,
            "platform": platform,
            "top_hashtags": niche_data.get("top_hashtags", []),
            "starter_pack": starter,
        }

    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo(f"\n=== HASHTAG RESEARCH: {niche.upper()} ({platform.upper()}) ===")
        top = result.get("top_hashtags", result.get("discovered_hashtags", []))
        if top and isinstance(top[0], dict):
            rows = [[h["hashtag"], h.get("video_count", "—"), f"{h.get('avg_views', 0):,}"] for h in top[:15]]
            click.echo(tabulate(rows, headers=["Hashtag", "Videos", "Avg Views"]))
        elif top:
            click.echo("Discovered: " + ", ".join(top[:15]))
        click.echo("\nStarter Pack:")
        click.echo("  Niche: " + ", ".join(starter["niche_specific"]))
        click.echo("  Broad: " + ", ".join(starter["broad"]))
        click.echo("  Community: " + ", ".join(starter["community"]))


# ── music group ───────────────────────────────────────────────────────────────

@cli.group()
def music():
    """Discover trending music and sounds for content creation."""


@music.command("trending")
@click.option("--platform", type=click.Choice(["youtube", "tiktok", "both"]), default="both")
@click.option("--region", default="US", show_default=True)
@click.option("--max", "max_results", default=20, show_default=True, type=int)
@click.pass_context
def music_trending(ctx: click.Context, platform: str, region: str, max_results: int):
    """Get trending music and sounds across platforms."""
    result: dict = {}
    if platform in ("youtube", "both"):
        try:
            result["youtube_music"] = youtube.get_trending_music(region, max_results)
        except Exception as e:
            result["youtube_music_error"] = str(e)
    if platform in ("tiktok", "both"):
        result["tiktok_sounds"] = tiktok.get_trending_sounds(max_results)

    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        if "youtube_music" in result:
            click.echo("\n=== TRENDING MUSIC — YOUTUBE ===")
            rows = [[v.get("artist", "?")[:25], v.get("track", v["title"])[:40], f"{v['views']:,}", v["url"]] for v in result["youtube_music"][:10]]
            click.echo(tabulate(rows, headers=["Artist", "Track", "Views", "URL"]))
        if "tiktok_sounds" in result:
            click.echo("\n=== TRENDING SOUNDS — TIKTOK ===")
            rows = [[s.get("title", "?")[:35], s.get("author", "")[:25], f"{s.get('video_count', 0)}", s.get("tiktok_url", "")] for s in result["tiktok_sounds"][:10]]
            click.echo(tabulate(rows, headers=["Sound", "Artist", "Videos", "URL"]))


@music.command("recommend")
@click.argument("content_type")
@click.option("--platform", type=click.Choice(["tiktok", "youtube"]), default="tiktok")
@click.pass_context
def music_recommend(ctx: click.Context, content_type: str, platform: str):
    """Get music recommendations for a content type (e.g. 'motivation', 'cooking', 'gaming')."""
    recs = _recommend_music(content_type, platform)
    if ctx.obj["json"]:
        click.echo(_json.dumps(recs, indent=2))
    else:
        click.echo(f"\nMusic Recommendations for '{content_type}' on {platform.title()}")
        for r in recs:
            click.echo(f"\n  Mood: {r['mood']}")
            click.echo(f"  Examples: {', '.join(r['examples'])}")
            click.echo(f"  Why: {r['why']}")


# ── accounts group ────────────────────────────────────────────────────────────

@cli.group()
def accounts():
    """Audit and optimize social media accounts."""


@accounts.command("audit")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"]))
@click.argument("username")
@click.pass_context
def accounts_audit(ctx: click.Context, platform: str, username: str):
    """Audit a public account and display key metrics."""
    data = account_optimizer.audit_account(platform, username)
    if ctx.obj["json"]:
        click.echo(_json.dumps(data, indent=2))
    else:
        click.echo(f"\n=== ACCOUNT AUDIT: @{username} ({platform.upper()}) ===")
        for k, v in data.items():
            if k not in ("note",):
                click.echo(f"  {k.replace('_', ' ').title():30s}: {v}")
        if data.get("note"):
            click.echo(f"\n  Note: {data['note']}")


@accounts.command("optimize")
@click.argument("platform", type=click.Choice(["youtube", "tiktok"]))
@click.argument("username")
@click.option("--niche", default=None, help="Your content niche")
@click.pass_context
def accounts_optimize(ctx: click.Context, platform: str, username: str, niche: str):
    """Generate a full optimization report for an account."""
    report = account_optimizer.generate_optimization_report(platform, username, niche)
    if ctx.obj["json"]:
        click.echo(_json.dumps(report, indent=2))
    else:
        click.echo(f"\n=== OPTIMIZATION REPORT: @{username} ({platform.upper()}) ===")
        acct = report["account"]
        click.echo(f"\nFollowers: {acct.get('followers', 0):,}")
        click.echo(f"Videos: {acct.get('video_count', 0):,}")

        click.echo("\n--- GROWTH PHASE ---")
        phase = report["growth_phase"]
        click.echo(f"  Phase: {phase['phase']}")
        click.echo(f"  Strategy: {phase['strategy']}")
        click.echo(f"  Key metric: {phase['key_metric']}")
        click.echo(f"  Content tip: {phase['content_tip']}")

        click.echo("\n--- POSTING SCHEDULE ---")
        sched = report["posting_schedule"]
        click.echo(f"  Best days: {', '.join(sched['best_days'])}")
        click.echo(f"  Best times (UTC): {', '.join(sched['best_times_utc'])}")
        click.echo(f"  Frequency: {sched['frequency']}")

        click.echo("\n--- QUICK WINS ---")
        for i, win in enumerate(report["quick_wins"], 1):
            click.echo(f"  {i}. {win}")

        click.echo("\n--- ISSUES FOUND ---")
        for issue in report["issues_found"]:
            click.echo(f"  • {issue}")

        click.echo("\n--- HASHTAG STRATEGY ---")
        hs = report["hashtag_strategy"]
        click.echo(f"  Recommended count: {hs['recommended_count']}")
        click.echo(f"  Tip: {hs['tip']}")


@accounts.command("schedule")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.option("--niche", default=None)
@click.pass_context
def accounts_schedule(ctx: click.Context, platform: str, niche: str):
    """Get the optimal posting schedule for a platform and niche."""
    sched = account_optimizer.get_posting_schedule(platform, niche)
    if ctx.obj["json"]:
        click.echo(_json.dumps(sched, indent=2))
    else:
        click.echo(f"\n=== POSTING SCHEDULE: {platform.upper()} ===")
        click.echo(f"  Best days: {', '.join(sched['best_days'])}")
        click.echo(f"  Best times (UTC): {', '.join(sched['best_times_utc'])}")
        click.echo(f"  Frequency: {sched['frequency']}")
        click.echo(f"  Notes: {sched['notes']}")
        if sched.get("niche_tip"):
            click.echo(f"\n  Niche tip: {sched['niche_tip']}")


@accounts.command("bio")
@click.argument("platform", type=click.Choice(["youtube", "tiktok", "instagram"]))
@click.argument("niche")
@click.option("--cta", default="Follow for daily tips", show_default=True)
@click.pass_context
def accounts_bio(ctx: click.Context, platform: str, niche: str, cta: str):
    """Generate a high-converting bio template."""
    result = account_optimizer.get_bio_template(platform, niche, cta)
    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo(f"\n=== BIO TEMPLATE: {platform.upper()} / {niche.upper()} ===\n")
        click.echo(result["bio"])
        click.echo(f"\nCharacter limit: {result['character_limits'].get(platform.lower(), 'N/A')}")
        click.echo("\nTips:")
        for tip in result["tips"]:
            click.echo(f"  • {tip}")


# ── theme-pages group ─────────────────────────────────────────────────────────

@cli.group("theme-pages")
def theme_pages_group():
    """Create, convert, and monetize viral theme pages."""


@theme_pages_group.command("niches")
@click.option("--sort", type=click.Choice(["growth_speed", "difficulty", "saturation"]), default="growth_speed")
@click.option("--difficulty", default=None, type=click.Choice(["Easy", "Medium", "Hard"]))
@click.option("--platform", default=None, help="Filter by platform (e.g. TikTok)")
@click.option("--max", "max_results", default=10, show_default=True, type=int)
@click.pass_context
def niches(ctx: click.Context, sort: str, difficulty: str, platform: str, max_results: int):
    """List the most profitable theme page niches."""
    result = theme_pages.get_profitable_niches(sort, max_results, difficulty, platform)
    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo("\n=== PROFITABLE THEME PAGE NICHES ===")
        rows = [
            [
                n["niche"],
                n["difficulty"],
                n["saturation"],
                n["growth_speed"],
                n["avg_cpm"],
                ", ".join(n["platforms"][:3]),
            ]
            for n in result
        ]
        click.echo(tabulate(rows, headers=["Niche", "Difficulty", "Saturation", "Growth", "CPM", "Platforms"]))


@theme_pages_group.command("strategy")
@click.argument("niche")
@click.option("--platform", type=click.Choice(["tiktok", "youtube", "instagram"]), default="tiktok")
@click.pass_context
def strategy(ctx: click.Context, niche: str, platform: str):
    """Generate a detailed theme page strategy for a niche."""
    result = theme_pages.generate_strategy(niche, platform)
    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo(f"\n=== THEME PAGE STRATEGY: {niche.upper()} on {platform.upper()} ===")
        click.echo(f"\n{result['summary']}")
        click.echo("\n--- USERNAME IDEAS ---")
        for u in result["recommended_username_formats"]:
            click.echo(f"  {u}")
        click.echo("\n--- CONTENT PILLARS ---")
        rows = [[p["pillar"], f"{p['share']}%", p["example"]] for p in result["content_pillars"]]
        click.echo(tabulate(rows, headers=["Pillar", "Share", "Example"]))
        click.echo("\n--- MONETIZATION PATH ---")
        for m in result["monetization_path"]:
            click.echo(f"  • {m}")
        click.echo("\n--- 30-DAY PLAN ---")
        for week in result["first_30_days_plan"]:
            click.echo(f"\n  Week {week['week']}: {week['goal']}")
            for action in week["actions"]:
                click.echo(f"    - {action}")
        click.echo("\n--- STARTER HASHTAGS ---")
        sp = result["hashtag_starter_pack"]
        click.echo(f"  Niche: {', '.join(sp['niche_specific'])}")
        click.echo(f"  Broad: {', '.join(sp['broad'])}")
        click.echo(f"  {sp['strategy']}")


@theme_pages_group.command("guide")
@click.option("--section", default=None, help="Specific phase name (e.g. 'Monetization')")
@click.pass_context
def guide(ctx: click.Context, section: str):
    """Show the complete theme page creation guide."""
    result = theme_pages.get_conversion_guide(section)
    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        if isinstance(result, dict) and "phases" in result:
            click.echo(f"\n{result['title']}")
            click.echo(f"\n{result['overview']}\n")
            for phase in result["phases"]:
                click.echo(f"\n{'='*60}")
                click.echo(f"PHASE {phase['phase']}: {phase['name']} ({phase.get('duration', '')})")
                click.echo(f"{'='*60}")
                for action in phase.get("actions", []):
                    click.echo(f"  ✓ {action}")
                if phase.get("income_timeline"):
                    click.echo("\n  Income Timeline:")
                    for stage, income in phase["income_timeline"].items():
                        click.echo(f"    {stage}: {income}")
            click.echo("\n--- COMMON MISTAKES TO AVOID ---")
            for m in result["common_mistakes"]:
                click.echo(f"  ✗ {m}")
        else:
            click.echo(_json.dumps(result, indent=2))


@theme_pages_group.command("compare")
@click.argument("niche_a")
@click.argument("niche_b")
@click.pass_context
def compare(ctx: click.Context, niche_a: str, niche_b: str):
    """Compare two niches side-by-side."""
    result = theme_pages.compare_niches(niche_a, niche_b)
    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo(f"\n=== NICHE COMPARISON: {niche_a.upper()} vs {niche_b.upper()} ===")
        rows = [[c["metric"], c[niche_a], c[niche_b]] for c in result["comparison"]]
        click.echo(tabulate(rows, headers=["Metric", niche_a.title(), niche_b.title()]))
        click.echo(f"\nRecommendation: {result['recommendation']}")


@theme_pages_group.command("monetization")
@click.argument("niche")
@click.pass_context
def monetization(ctx: click.Context, niche: str):
    """Show expected income timeline and monetization methods for a niche."""
    result = theme_pages.get_monetization_timeline(niche)
    if ctx.obj["json"]:
        click.echo(_json.dumps(result, indent=2))
    else:
        click.echo(f"\n=== MONETIZATION TIMELINE: {niche.upper()} ===")
        click.echo(f"CPM Range: {result['cpm_range']}")
        click.echo("\nIncome by Stage:")
        for stage, income in result["income_by_stage"].items():
            click.echo(f"  {stage}: {income}")
        click.echo("\nMonetization Methods:")
        for m in result["monetization_methods"]:
            click.echo(f"  • {m}")
        click.echo(f"\nFastest Start: {result['fastest_monetization']}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _recommend_music(content_type: str, platform: str) -> list[dict]:
    ct_lower = content_type.lower()
    library = [
        {
            "mood": "Energetic/Hype",
            "matches": ["gym", "fitness", "workout", "gaming", "sports", "motivation"],
            "examples": ["Trendy EDM drops", "Hip-hop beats", "Phonk music"],
            "why": "Fast tempo keeps watch time high and matches high-energy visuals",
        },
        {
            "mood": "Chill/Aesthetic",
            "matches": ["food", "travel", "fashion", "lifestyle", "beauty", "cooking"],
            "examples": ["Lo-fi beats", "Indie pop", "Soft R&B"],
            "why": "Creates aspirational mood that drives saves and shares",
        },
        {
            "mood": "Emotional/Inspiring",
            "matches": ["motivation", "mindset", "story", "transformation", "success"],
            "examples": ["Cinematic orchestral", "Soft piano", "Gospel-inspired"],
            "why": "Triggers emotional response that drives comments and shares",
        },
        {
            "mood": "Trending Viral Sound",
            "matches": ["any", "trending", "viral", "fyp"],
            "examples": ["Check TikTok trending sounds page", "Remix of chart hits", "Meme sounds"],
            "why": "Algorithm boosts videos using trending sounds by 2-4× on TikTok",
        },
        {
            "mood": "Corporate/Professional",
            "matches": ["tech", "finance", "real estate", "business", "investing"],
            "examples": ["Upbeat corporate pop", "Minimal electronic", "Podcast-style background"],
            "why": "Professional tone builds trust in high-value niches (higher CPM)",
        },
    ]
    matching = [r for r in library if any(m in ct_lower for m in r["matches"])]
    if not matching:
        matching = library
    viral_sound = next((r for r in library if r["mood"] == "Trending Viral Sound"), None)
    if viral_sound and viral_sound not in matching:
        matching.append(viral_sound)
    return matching[:3]
