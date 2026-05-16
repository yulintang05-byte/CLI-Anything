"""TikTok trends fetcher.

Uses the official TikTok Research API (https://developers.tiktok.com/products/research-api/)
for hashtag/video data, and the TikTok Display API for sound/music trends.

Requires:
  - TIKTOK_CLIENT_KEY   (from TikTok for Developers app)
  - TIKTOK_CLIENT_SECRET
"""

import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from typing import Optional

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2"
TIKTOK_OAUTH_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# Trending hashtag categories for query building
TREND_SEED_QUERIES = {
    "music":     ["music", "newsong", "viral", "dance", "trending"],
    "comedy":    ["funny", "comedy", "humor", "meme", "lol"],
    "fashion":   ["fashion", "ootd", "style", "outfit", "fit"],
    "gaming":    ["gaming", "gamer", "twitch", "esports", "streamer"],
    "food":      ["food", "recipe", "cooking", "foodie", "mukbang"],
    "fitness":   ["fitness", "gym", "workout", "health", "bodybuilding"],
    "business":  ["entrepreneur", "business", "money", "investing", "sidehustle"],
    "lifestyle": ["lifestyle", "vlog", "dailyvlog", "grwm", "dayinmylife"],
    "all":       ["viral", "trending", "fyp", "foryou", "foryoupage"],
}


def _get_access_token(client_key: str, client_secret: str) -> str:
    """Obtain OAuth2 client-credentials token from TikTok."""
    payload = urllib.parse.urlencode({
        "client_key": client_key,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    }).encode()
    req = urllib.request.Request(
        TIKTOK_OAUTH_URL,
        data=payload,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode())
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"TikTok OAuth failed: {data.get('message', data)}")
    return token


def _post(url: str, token: str, body: dict) -> dict:
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_trending_hashtags(
    client_key: str,
    client_secret: str,
    category: str = "all",
    region: str = "US",
    max_results: int = 30,
) -> list[dict]:
    """Return trending TikTok hashtags by searching top videos for seed queries."""
    token = _get_access_token(client_key, client_secret)
    seeds = TREND_SEED_QUERIES.get(category.lower(), TREND_SEED_QUERIES["all"])
    tag_counts: dict[str, int] = {}
    tag_views: dict[str, int] = {}

    for seed in seeds[:3]:
        body = {
            "query": {
                "and": [
                    {"field_name": "keyword", "operation": "IN", "field_values": [seed]},
                    {"field_name": "region_code", "operation": "IN", "field_values": [region.upper()]},
                ],
            },
            "start_date": _days_ago(7),
            "end_date": _today(),
            "max_count": 20,
            "fields": "id,hashtag_names,view_count,like_count,share_count",
        }
        try:
            resp = _post(f"{TIKTOK_API_BASE}/research/video/query/", token, body)
            for video in resp.get("data", {}).get("videos", []):
                views = video.get("view_count", 0)
                for tag in video.get("hashtag_names", []):
                    t = tag.lower().lstrip("#")
                    tag_counts[t] = tag_counts.get(t, 0) + 1
                    tag_views[t] = tag_views.get(t, 0) + views
        except Exception:
            continue

    ranked = sorted(tag_counts.keys(), key=lambda t: tag_views.get(t, 0), reverse=True)[:max_results]
    return [
        {
            "hashtag": f"#{tag}",
            "video_appearances": tag_counts[tag],
            "total_views": tag_views[tag],
        }
        for tag in ranked
    ]


def fetch_trending_sounds(
    client_key: str,
    client_secret: str,
    region: str = "US",
    max_results: int = 20,
) -> list[dict]:
    """Return trending TikTok sounds/music from top viral videos."""
    token = _get_access_token(client_key, client_secret)
    body = {
        "query": {
            "and": [
                {"field_name": "keyword", "operation": "IN", "field_values": ["fyp", "viral"]},
                {"field_name": "region_code", "operation": "IN", "field_values": [region.upper()]},
            ],
        },
        "start_date": _days_ago(3),
        "end_date": _today(),
        "max_count": 50,
        "fields": "id,music_id,view_count,like_count,share_count,hashtag_names",
    }
    resp = _post(f"{TIKTOK_API_BASE}/research/video/query/", token, body)
    sound_views: dict[str, int] = {}
    sound_likes: dict[str, int] = {}
    for video in resp.get("data", {}).get("videos", []):
        music_id = str(video.get("music_id", ""))
        if not music_id or music_id == "0":
            continue
        sound_views[music_id] = sound_views.get(music_id, 0) + video.get("view_count", 0)
        sound_likes[music_id] = sound_likes.get(music_id, 0) + video.get("like_count", 0)

    ranked = sorted(sound_views.keys(), key=lambda s: sound_views[s], reverse=True)[:max_results]
    return [
        {
            "sound_id": sid,
            "total_views": sound_views[sid],
            "total_likes": sound_likes[sid],
            "tiktok_url": f"https://www.tiktok.com/music/-{sid}",
        }
        for sid in ranked
    ]


def fetch_trending_videos(
    client_key: str,
    client_secret: str,
    category: str = "all",
    region: str = "US",
    max_results: int = 20,
) -> list[dict]:
    """Return top trending TikTok videos for a category/region."""
    token = _get_access_token(client_key, client_secret)
    seeds = TREND_SEED_QUERIES.get(category.lower(), TREND_SEED_QUERIES["all"])
    body = {
        "query": {
            "and": [
                {"field_name": "keyword", "operation": "IN", "field_values": seeds[:5]},
                {"field_name": "region_code", "operation": "IN", "field_values": [region.upper()]},
            ],
        },
        "start_date": _days_ago(7),
        "end_date": _today(),
        "max_count": min(max_results, 50),
        "fields": "id,author_name,video_description,hashtag_names,view_count,like_count,comment_count,share_count,music_id,create_time",
        "sort_type": "relevant",
    }
    resp = _post(f"{TIKTOK_API_BASE}/research/video/query/", token, body)
    results = []
    for v in resp.get("data", {}).get("videos", []):
        views = v.get("view_count", 1) or 1
        likes = v.get("like_count", 0)
        comments = v.get("comment_count", 0)
        shares = v.get("share_count", 0)
        results.append({
            "id": v.get("id"),
            "author": v.get("author_name", ""),
            "description": v.get("video_description", "")[:120],
            "hashtags": v.get("hashtag_names", [])[:10],
            "views": views,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "engagement_rate": round((likes + comments + shares) / views * 100, 2),
            "music_id": str(v.get("music_id", "")),
            "created_at": v.get("create_time", ""),
            "url": f"https://www.tiktok.com/@{v.get('author_name', '_')}/video/{v.get('id')}",
        })
    results.sort(key=lambda x: x["views"], reverse=True)
    return results


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _days_ago(n: int) -> str:
    ts = time.time() - n * 86400
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y%m%d")
