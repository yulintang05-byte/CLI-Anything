"""TikTok hashtag tools — curated packs, suggestions, and strategy."""

from __future__ import annotations

from cli_anything.tiktok.utils.tiktok_backend import (
    get_niche_hashtags,
    list_niches,
    NICHE_HASHTAGS,
)


def get_top_hashtags(niche: str | None = None, limit: int = 30) -> dict:
    """Return top hashtags, optionally filtered by niche."""
    if niche:
        tags = get_niche_hashtags(niche, limit=limit)
        return {
            "niche": niche,
            "hashtags": [f"#{t}" for t in tags],
            "count": len(tags),
        }

    # Return top hashtags across all niches
    all_tags: list[str] = []
    seen: set[str] = set()
    for niche_tags in NICHE_HASHTAGS.values():
        for t in niche_tags[:5]:
            if t not in seen:
                all_tags.append(t)
                seen.add(t)
    return {
        "niche": "all",
        "hashtags": [f"#{t}" for t in all_tags[:limit]],
        "count": min(len(all_tags), limit),
    }


def suggest_hashtags(niche: str, limit: int = 30) -> dict:
    """Generate a hashtag strategy for a niche with tiers."""
    tags = get_niche_hashtags(niche, limit=limit)

    # Tier system: mega (1B+), large (100M+), niche (10M+), micro (<10M)
    # We approximate tiers by position in curated list
    total = len(tags)
    tier_size = max(total // 4, 1)

    mega = tags[:tier_size]
    large = tags[tier_size : tier_size * 2]
    niche_tags = tags[tier_size * 2 : tier_size * 3]
    micro = tags[tier_size * 3 :]

    return {
        "niche": niche,
        "strategy": {
            "mega_tags": [f"#{t}" for t in mega],
            "large_tags": [f"#{t}" for t in large],
            "niche_tags": [f"#{t}" for t in niche_tags],
            "micro_tags": [f"#{t}" for t in micro],
        },
        "recommended_mix": {
            "per_post": "Use 1 mega + 1 large + 2 niche + 1 micro = 5 total",
            "rotation": "Rotate packs every 7 days to avoid shadowban",
            "placement": "Add hashtags in the caption, not comments",
        },
        "all_hashtags": [f"#{t}" for t in tags],
        "total": len(tags),
    }


def available_niches() -> list[str]:
    """List all available niche categories."""
    return list_niches()


def build_caption(niche: str, num_tags: int = 5) -> str:
    """Build a sample caption with optimal hashtag placement."""
    tags = get_niche_hashtags(niche, limit=num_tags * 3)
    selected = _pick_mixed(tags, num_tags)
    tag_str = " ".join(f"#{t}" for t in selected)
    return f"[Your caption here]\n\n{tag_str}"


def _pick_mixed(tags: list[str], n: int) -> list[str]:
    """Pick n tags spread across the full list."""
    if len(tags) <= n:
        return tags
    step = len(tags) // n
    return [tags[i * step] for i in range(n)]
