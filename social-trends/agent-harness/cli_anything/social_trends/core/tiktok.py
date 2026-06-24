"""TikTok trend intelligence — Research API + public web scraping fallback.

Two operational modes:
  1. Research API (requires TikTok developer credentials): full video/hashtag/music data.
  2. Public scrape (no key needed): best-effort trending data from TikTok's public endpoints.

All output is normalized to the same schema for easy cross-platform merging.
"""

import re
from typing import Optional
from cli_anything.social_trends.utils.trends_backend import (
    tt_post,
    tt_scrape_trending_hashtags,
    tt_scrape_trending_music,
    cached,
    check_tiktok_configured,
)


SUPPORTED_REGIONS = [
    "US", "GB", "CA", "AU", "IN", "BR", "JP", "KR",
    "FR", "DE", "MX", "ID", "TH", "PH", "VN", "SG",
]


def _normalize_research_video(item: dict) -> dict:
    """Normalize a TikTok Research API video item."""
    music = item.get("music_info", {})
    author = item.get("author_info", {})
    return {
        "id": str(item.get("id", "")),
        "platform": "tiktok",
        "description": item.get("video_description", "")[:300],
        "created_at": item.get("create_time", 0),
        "author": author.get("display_name", ""),
        "author_id": str(author.get("sec_uid", "")),
        "views": item.get("view_count", 0),
        "likes": item.get("like_count", 0),
        "comments": item.get("comment_count", 0),
        "shares": item.get("share_count", 0),
        "hashtags": [h.get("name", "") for h in item.get("hashtag_info_list", [])],
        "music_id": str(music.get("id", "")),
        "music_title": music.get("title", ""),
        "music_author": music.get("author", ""),
        "duration": item.get("duration", 0),
        "url": f"https://tiktok.com/@{author.get('display_name', '')}/video/{item.get('id', '')}",
    }


def _normalize_scraped_video(item: dict) -> dict:
    """Normalize a scraped TikTok video item (public web)."""
    desc = item.get("desc", "")
    author = item.get("author", {})
    stats = item.get("stats", {})
    music = item.get("music", {})

    hashtags = re.findall(r"#(\w+)", desc)
    return {
        "id": item.get("id", ""),
        "platform": "tiktok",
        "description": desc[:300],
        "created_at": item.get("createTime", 0),
        "author": author.get("nickname", ""),
        "author_id": author.get("id", ""),
        "views": stats.get("playCount", 0),
        "likes": stats.get("diggCount", 0),
        "comments": stats.get("commentCount", 0),
        "shares": stats.get("shareCount", 0),
        "hashtags": hashtags,
        "music_id": music.get("id", ""),
        "music_title": music.get("title", ""),
        "music_author": music.get("authorName", ""),
        "duration": item.get("video", {}).get("duration", 0),
        "url": f"https://tiktok.com/@{author.get('uniqueId', '')}/video/{item.get('id', '')}",
    }


def get_trending_videos(
    region: str = "US",
    max_results: int = 25,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Fetch trending TikTok videos.

    Uses TikTok Research API if credentials are configured, otherwise
    falls back to public web scraping.

    Args:
        region: ISO 3166-1 alpha-2 code (e.g. 'US').
        max_results: Number of videos to return.
        start_date: YYYYMMDD for Research API date range.
        end_date: YYYYMMDD for Research API date range.
    """
    cache_key = f"tt_trending_{region}_{max_results}_{start_date}_{end_date}"

    def fetch():
        if check_tiktok_configured():
            return _fetch_via_research_api(region, max_results, start_date, end_date)
        return _fetch_via_scrape(region, max_results)

    return cached(cache_key, fetch)


def _fetch_via_research_api(
    region: str,
    max_results: int,
    start_date: Optional[str],
    end_date: Optional[str],
) -> dict:
    import time
    if not start_date:
        import datetime
        end_dt = datetime.date.today()
        start_dt = end_dt - datetime.timedelta(days=7)
        start_date = start_dt.strftime("%Y%m%d")
        end_date = end_dt.strftime("%Y%m%d")

    payload = {
        "query": {
            "and": [
                {"operation": "EQ", "field_name": "region_code", "field_values": [region]},
            ]
        },
        "start_date": start_date,
        "end_date": end_date,
        "max_count": min(max_results, 100),
        "fields": (
            "id,video_description,create_time,author_info,"
            "music_info,hashtag_info_list,view_count,like_count,"
            "comment_count,share_count,duration"
        ),
    }
    data = tt_post("/research/video/query/", data=payload)
    videos = [_normalize_research_video(v) for v in data.get("videos", [])]
    return {
        "platform": "tiktok",
        "source": "research_api",
        "region": region,
        "total": len(videos),
        "videos": videos,
    }


def _fetch_via_scrape(region: str, max_results: int) -> dict:
    raw = tt_scrape_trending_hashtags(region=region)
    videos = [_normalize_scraped_video(item) for item in raw[:max_results]]
    return {
        "platform": "tiktok",
        "source": "public_scrape",
        "region": region,
        "total": len(videos),
        "videos": videos,
        "note": "Configure TikTok Research API credentials for richer data.",
    }


def get_trending_hashtags(
    region: str = "US",
    max_results: int = 30,
) -> dict:
    """Extract trending hashtags from TikTok videos.

    Aggregates #hashtags from fetched trending videos, ranked by frequency.
    """
    cache_key = f"tt_hashtags_{region}_{max_results}"

    def fetch():
        result = get_trending_videos(region=region, max_results=50)
        tag_counts: dict[str, int] = {}
        for video in result.get("videos", []):
            for tag in video.get("hashtags", []):
                tag_lower = tag.lower()
                tag_counts[tag_lower] = tag_counts.get(tag_lower, 0) + 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        hashtags = [
            {"tag": f"#{tag}", "count": count, "platform": "tiktok"}
            for tag, count in sorted_tags[:max_results]
        ]
        return {
            "platform": "tiktok",
            "region": region,
            "total": len(hashtags),
            "hashtags": hashtags,
        }

    return cached(cache_key, fetch)


def get_trending_music(region: str = "US", max_results: int = 25) -> dict:
    """Fetch trending music from TikTok.

    Uses Research API when available, falls back to public scrape.
    """
    cache_key = f"tt_music_{region}_{max_results}"

    def fetch():
        if check_tiktok_configured():
            # Extract music from trending videos via Research API
            result = get_trending_videos(region=region, max_results=100)
            music_counts: dict[str, dict] = {}
            for video in result.get("videos", []):
                mid = str(video.get("music_id", ""))
                if mid and mid != "0":
                    if mid not in music_counts:
                        music_counts[mid] = {
                            "id": mid,
                            "platform": "tiktok",
                            "title": video.get("music_title", ""),
                            "author": video.get("music_author", ""),
                            "video_count": 0,
                        }
                    music_counts[mid]["video_count"] += 1

            sorted_music = sorted(
                music_counts.values(), key=lambda x: x["video_count"], reverse=True
            )
            return {
                "platform": "tiktok",
                "source": "research_api",
                "region": region,
                "total": len(sorted_music[:max_results]),
                "music": sorted_music[:max_results],
            }
        else:
            raw = tt_scrape_trending_music(region=region)
            music = []
            for item in raw[:max_results]:
                music.append({
                    "id": str(item.get("id", "")),
                    "platform": "tiktok",
                    "title": item.get("title", ""),
                    "author": item.get("authorName", ""),
                    "cover": item.get("coverLarge", ""),
                    "play_url": item.get("playUrl", ""),
                    "duration": item.get("duration", 0),
                    "video_count": item.get("userCount", 0),
                })
            return {
                "platform": "tiktok",
                "source": "public_scrape",
                "region": region,
                "total": len(music),
                "music": music,
            }

    return cached(cache_key, fetch)


def search_hashtag_videos(
    hashtag: str,
    region: str = "US",
    max_results: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Search TikTok for videos using a specific hashtag.

    Requires TikTok Research API credentials.
    """
    if not check_tiktok_configured():
        raise RuntimeError(
            "TikTok Research API required for hashtag search. "
            "Run: social-trends auth tiktok --client-key <K> --client-secret <S>"
        )

    import datetime
    if not start_date:
        end_dt = datetime.date.today()
        start_dt = end_dt - datetime.timedelta(days=30)
        start_date = start_dt.strftime("%Y%m%d")
        end_date = end_dt.strftime("%Y%m%d")

    tag_clean = hashtag.lstrip("#")
    payload = {
        "query": {
            "and": [
                {"operation": "EQ", "field_name": "hashtag_name", "field_values": [tag_clean]},
                {"operation": "EQ", "field_name": "region_code", "field_values": [region]},
            ]
        },
        "start_date": start_date,
        "end_date": end_date,
        "max_count": min(max_results, 100),
        "fields": (
            "id,video_description,create_time,author_info,"
            "music_info,hashtag_info_list,view_count,like_count,"
            "comment_count,share_count,duration"
        ),
    }
    data = tt_post("/research/video/query/", data=payload)
    videos = [_normalize_research_video(v) for v in data.get("videos", [])]
    return {
        "platform": "tiktok",
        "hashtag": f"#{tag_clean}",
        "region": region,
        "total": len(videos),
        "videos": videos,
    }
