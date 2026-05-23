"""Cross-platform trend analysis and content strategy engine."""
import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

from . import youtube_scraper as yt
from . import tiktok_scraper as tt


# Viral threshold multipliers
_VIRAL_VIEW_THRESHOLD_YT = 500_000   # 500K views = viral on YouTube
_VIRAL_VIEW_THRESHOLD_TT = 1_000_000  # 1M views = viral on TikTok


def get_cross_platform_trends(
    limit: int = 30,
    yt_api_key: Optional[str] = None,
    region: str = "US",
) -> Dict[str, Any]:
    """
    Fetch and combine YouTube + TikTok trends into a unified report.

    Returns:
        {
            "trending_topics": [...],
            "trending_hashtags": [...],
            "trending_music": [...],
            "content_opportunities": [...],
            "scraped_at": "...",
        }
    """
    # Parallel data collection
    yt_videos = yt.scrape_trending_videos(limit=limit, api_key=yt_api_key)
    tt_videos = tt.scrape_trending_videos(region=region, limit=limit)
    yt_music = yt.scrape_trending_music(api_key=yt_api_key, limit=20)
    tt_music = tt.scrape_trending_music(region=region, limit=20)
    yt_tags = yt.scrape_trending_hashtags(api_key=yt_api_key, limit=30)
    tt_tags = tt.scrape_trending_hashtags(region=region, limit=30)

    trending_topics = _merge_topics(yt_videos, tt_videos)
    trending_hashtags = _merge_hashtags(yt_tags, tt_tags)
    trending_music = _merge_music(yt_music, tt_music)
    opportunities = _identify_opportunities(
        trending_topics, trending_hashtags, trending_music
    )

    return {
        "trending_topics": trending_topics[:limit],
        "trending_hashtags": trending_hashtags[:50],
        "trending_music": trending_music[:25],
        "content_opportunities": opportunities[:10],
        "raw": {
            "youtube_videos": yt_videos,
            "tiktok_videos": tt_videos,
        },
        "scraped_at": datetime.utcnow().isoformat(),
        "platforms": ["youtube", "tiktok"],
        "region": region,
    }


def _merge_topics(yt_videos: List[Dict], tt_videos: List[Dict]) -> List[Dict]:
    """Combine YouTube and TikTok trending topics by keyword similarity."""
    # Extract keywords from titles
    yt_kw = _keywords_from_videos(yt_videos, "youtube")
    tt_kw = _keywords_from_videos(tt_videos, "tiktok")

    all_kw: Dict[str, Dict] = {}
    for kw, data in yt_kw.items():
        all_kw[kw] = data
    for kw, data in tt_kw.items():
        if kw in all_kw:
            all_kw[kw]["platforms"].append("tiktok")
            all_kw[kw]["score"] += data["score"] * 1.2  # cross-platform bonus
            all_kw[kw]["total_views"] += data["total_views"]
        else:
            all_kw[kw] = data

    sorted_topics = sorted(all_kw.values(), key=lambda x: x["score"], reverse=True)
    for i, t in enumerate(sorted_topics, 1):
        t["rank"] = i
        t["is_cross_platform"] = len(t.get("platforms", [])) > 1
    return sorted_topics


def _keywords_from_videos(videos: List[Dict], platform: str) -> Dict[str, Dict]:
    """Extract meaningful keywords from video titles."""
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into", "through",
        "and", "but", "or", "so", "yet", "nor", "not", "no", "my", "your",
        "his", "her", "our", "their", "this", "that", "these", "those", "i",
        "you", "he", "she", "we", "they", "it", "me", "him", "us", "them",
        "new", "get", "got", "make", "made", "one", "two", "first", "how",
        "what", "when", "why", "who", "all", "just", "more", "most", "never",
    }
    kw_map: Dict[str, Dict] = {}
    for video in videos:
        if "error" in video:
            continue
        title = video.get("title", "") or video.get("description", "")
        words = re.findall(r"\b[a-zA-Z]{3,}\b", title.lower())
        views = video.get("views", 0) or 0
        for word in words:
            if word in stopwords:
                continue
            if word not in kw_map:
                kw_map[word] = {
                    "keyword": word,
                    "platforms": [platform],
                    "score": 0.0,
                    "total_views": 0,
                    "example_titles": [],
                }
            kw_map[word]["score"] += 1 + (views / 1_000_000)
            kw_map[word]["total_views"] += views
            if len(kw_map[word]["example_titles"]) < 3:
                kw_map[word]["example_titles"].append(title[:80])
    return kw_map


def _merge_hashtags(yt_tags: List[Dict], tt_tags: List[Dict]) -> List[Dict]:
    """Merge and rank hashtags from both platforms."""
    combined: Dict[str, Dict] = {}

    for tag_data in yt_tags:
        ht = tag_data.get("hashtag", "").lower()
        if not ht:
            continue
        combined[ht] = {
            "hashtag": ht,
            "platforms": ["youtube"],
            "youtube_rank": tag_data.get("rank", 999),
            "tiktok_rank": 999,
            "youtube_appearances": tag_data.get("appearances", 0),
            "tiktok_appearances": 0,
            "combined_score": tag_data.get("appearances", 0),
            "seen_in": tag_data.get("seen_in", []),
        }

    for tag_data in tt_tags:
        ht = tag_data.get("hashtag", "").lower()
        if not ht:
            continue
        if ht in combined:
            combined[ht]["platforms"].append("tiktok")
            combined[ht]["tiktok_rank"] = tag_data.get("rank", 999)
            combined[ht]["tiktok_appearances"] = tag_data.get("appearances", 0)
            combined[ht]["combined_score"] = (
                combined[ht]["youtube_appearances"]
                + tag_data.get("appearances", 0) * 1.5  # TikTok weight
            )
        else:
            combined[ht] = {
                "hashtag": ht,
                "platforms": ["tiktok"],
                "youtube_rank": 999,
                "tiktok_rank": tag_data.get("rank", 999),
                "youtube_appearances": 0,
                "tiktok_appearances": tag_data.get("appearances", 0),
                "combined_score": tag_data.get("appearances", 0),
                "seen_in": tag_data.get("seen_in", []),
            }

    sorted_tags = sorted(combined.values(), key=lambda x: x["combined_score"], reverse=True)
    for i, t in enumerate(sorted_tags, 1):
        t["rank"] = i
        t["is_cross_platform"] = len(t["platforms"]) > 1
    return sorted_tags


def _merge_music(yt_music: List[Dict], tt_music: List[Dict]) -> List[Dict]:
    """Merge trending music from both platforms."""
    music_map: Dict[str, Dict] = {}

    for item in yt_music:
        key = _music_key(item.get("song_title", ""), item.get("artist", ""))
        music_map[key] = {
            "song_title": item.get("song_title", ""),
            "artist": item.get("artist", ""),
            "platforms": ["youtube"],
            "youtube_views": item.get("views", 0),
            "tiktok_videos": 0,
            "youtube_url": item.get("url", ""),
            "tiktok_url": "",
            "hashtags": item.get("hashtags", []),
            "trend_score": item.get("views", 0) / 1_000_000,
            "is_viral": item.get("views", 0) >= _VIRAL_VIEW_THRESHOLD_YT,
        }

    for item in tt_music:
        key = _music_key(item.get("song_title", ""), item.get("artist", ""))
        # Try fuzzy match
        matched_key = _fuzzy_music_match(key, music_map)
        if matched_key:
            music_map[matched_key]["platforms"].append("tiktok")
            music_map[matched_key]["tiktok_videos"] = item.get("videos_using", 0)
            music_map[matched_key]["tiktok_url"] = item.get("tiktok_url", "")
            music_map[matched_key]["trend_score"] += item.get("videos_using", 0) * 0.1
        else:
            music_map[key] = {
                "song_title": item.get("song_title", ""),
                "artist": item.get("artist", ""),
                "platforms": ["tiktok"],
                "youtube_views": 0,
                "tiktok_videos": item.get("videos_using", 0),
                "youtube_url": "",
                "tiktok_url": item.get("tiktok_url", ""),
                "hashtags": [],
                "trend_score": item.get("videos_using", 0) * 0.1,
                "is_viral": item.get("total_views", 0) >= _VIRAL_VIEW_THRESHOLD_TT,
            }

    sorted_music = sorted(music_map.values(), key=lambda x: x["trend_score"], reverse=True)
    for i, m in enumerate(sorted_music, 1):
        m["rank"] = i
        m["is_cross_platform"] = len(m["platforms"]) > 1
    return sorted_music


def _music_key(title: str, artist: str) -> str:
    def clean(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())
    return f"{clean(title)}||{clean(artist)}"


def _fuzzy_music_match(key: str, music_map: Dict) -> Optional[str]:
    title_part = key.split("||")[0]
    for existing_key in music_map:
        existing_title = existing_key.split("||")[0]
        if len(title_part) > 5 and title_part in existing_title:
            return existing_key
        if len(existing_title) > 5 and existing_title in title_part:
            return existing_key
    return None


def _identify_opportunities(
    topics: List[Dict],
    hashtags: List[Dict],
    music: List[Dict],
) -> List[Dict]:
    """Identify content creation opportunities from trend data."""
    opportunities = []

    # Cross-platform topics = highest opportunity
    for topic in topics:
        if topic.get("is_cross_platform") and topic.get("total_views", 0) > 1_000_000:
            opportunities.append({
                "type": "cross_platform_topic",
                "opportunity": f"Create content about '{topic['keyword']}' — trending on both YouTube & TikTok",
                "keyword": topic["keyword"],
                "estimated_reach": topic.get("total_views", 0),
                "platforms": topic.get("platforms", []),
                "priority": "HIGH",
                "action": f"Post a video/reel about '{topic['keyword']}' using trending hashtags",
            })

    # Viral music for TikTok
    for track in music[:5]:
        if track.get("tiktok_videos", 0) > 3 or track.get("is_viral"):
            opportunities.append({
                "type": "trending_audio",
                "opportunity": f"Use '{track['song_title']}' by {track['artist']} — viral on TikTok",
                "song": track["song_title"],
                "artist": track["artist"],
                "tiktok_url": track.get("tiktok_url", ""),
                "priority": "HIGH",
                "action": "Create a TikTok video using this trending sound",
            })

    # High-volume cross-platform hashtags
    for ht in hashtags:
        if ht.get("is_cross_platform") and ht.get("combined_score", 0) > 5:
            opportunities.append({
                "type": "cross_platform_hashtag",
                "opportunity": f"Use {ht['hashtag']} — trending on {', '.join(ht['platforms'])}",
                "hashtag": ht["hashtag"],
                "combined_score": ht.get("combined_score", 0),
                "priority": "MEDIUM",
                "action": f"Include {ht['hashtag']} in your next post on all platforms",
            })

    # Sort by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(opportunities, key=lambda x: priority_order.get(x.get("priority", "LOW"), 2))


def generate_hashtag_set(
    niche: str,
    platform: str = "both",
    size: str = "medium",
    yt_api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate an optimized hashtag set for a given niche.

    Args:
        niche: e.g., "fitness", "cooking", "crypto"
        platform: "youtube"|"tiktok"|"both"
        size: "small"(5-10)|"medium"(15-20)|"large"(25-30)
        yt_api_key: optional YouTube Data API key
    """
    size_map = {"small": (5, 10), "medium": (12, 20), "large": (22, 30)}
    min_ht, max_ht = size_map.get(size, (12, 20))

    yt_niche_tags = []
    tt_tags = []

    if platform in ("youtube", "both"):
        yt_niche_tags = yt.get_niche_hashtags(niche, api_key=yt_api_key, limit=20)

    if platform in ("tiktok", "both"):
        # Get top TT trending hashtags related to niche
        tt_all = tt.scrape_trending_hashtags(limit=50)
        niche_words = set(niche.lower().split())
        tt_tags = [
            t for t in tt_all
            if any(w in t.get("hashtag", "").lower() for w in niche_words)
        ]

    # Always include niche-specific tags
    niche_specific = [
        f"#{niche.replace(' ', '')}",
        f"#{niche.replace(' ', '')}content",
        f"#{niche.replace(' ', '')}creator",
        f"#{niche.replace(' ', '')}tips",
        f"#{niche.replace(' ', '')}community",
    ]

    # Broad reach tags
    broad_tags = [
        "#viral", "#trending", "#fyp", "#foryou", "#foryoupage",
        "#explore", "#content", "#creator", "#2024", "#reels",
    ]

    # Mid-range tags for discoverability
    mid_tags = [
        f"#{niche.replace(' ', '')}life",
        f"#{niche.replace(' ', '')}daily",
        f"#{niche.replace(' ', '')}journey",
        f"#best{niche.replace(' ', '')}",
        f"#{niche.replace(' ', '')}goals",
    ]

    # Combine and deduplicate
    all_tags: List[str] = []
    for t in yt_niche_tags + tt_tags:
        ht = t.get("hashtag", "")
        if ht and ht not in all_tags:
            all_tags.append(ht)

    combined = niche_specific + all_tags + mid_tags + broad_tags
    seen = set()
    unique_tags = []
    for t in combined:
        t_clean = t.lower().strip()
        if t_clean not in seen:
            seen.add(t_clean)
            unique_tags.append(t)

    final_set = unique_tags[:max_ht]

    return {
        "niche": niche,
        "platform": platform,
        "hashtag_count": len(final_set),
        "hashtags": final_set,
        "hashtag_string": " ".join(final_set),
        "strategy": {
            "niche_specific": niche_specific[:5],
            "trending_scraped": all_tags[:8],
            "broad_reach": broad_tags[:5],
        },
        "tips": [
            f"Use {min_ht}-{max_ht} hashtags per post for optimal reach",
            "Mix niche-specific and broad hashtags",
            "Refresh your hashtag set weekly as trends change",
            "Never use banned/shadowbanned hashtags",
            f"For TikTok: always include #fyp #foryoupage",
            f"For YouTube Shorts: title hashtags beat description hashtags",
        ],
    }
