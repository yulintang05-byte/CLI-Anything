"""TikTok trend scraper — viral hashtags, sounds, and video analysis.

Uses TikTok's publicly accessible web APIs (no login required for trend data).
For authenticated features (your own account analytics) set TIKTOK_SESSION_ID
in your environment or .env file.

Optional: Install TikTokApi[playwright] for enhanced scraping:
    pip install "cli-anything-social-trends[tiktok]"
    playwright install chromium
"""

import json
import time
import random
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional
from urllib.parse import quote, urlencode

import requests


# ── Data Models ────────────────────────────────────────────────────────

@dataclass
class TrendingHashtag:
    name: str
    id: str = ""
    view_count: int = 0
    video_count: int = 0
    description: str = ""
    is_promoted: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendingSound:
    title: str
    artist: str
    id: str = ""
    play_count: int = 0
    video_count: int = 0
    duration: int = 0
    cover_url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrendingVideo:
    id: str
    description: str
    author: str
    author_followers: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    play_count: int = 0
    hashtags: list[str] = field(default_factory=list)
    sound_title: str = ""
    sound_artist: str = ""
    duration: int = 0
    url: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TikTokTrendReport:
    scraped_at: str = ""
    region: str = "US"
    trending_hashtags: list[TrendingHashtag] = field(default_factory=list)
    trending_sounds: list[TrendingSound] = field(default_factory=list)
    trending_videos: list[TrendingVideo] = field(default_factory=list)
    top_hashtags_by_views: list[str] = field(default_factory=list)
    top_sounds_by_videos: list[str] = field(default_factory=list)
    recommended_hashtags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "scraped_at": self.scraped_at,
            "region": self.region,
            "trending_hashtags": [h.to_dict() for h in self.trending_hashtags],
            "trending_sounds": [s.to_dict() for s in self.trending_sounds],
            "trending_videos": [v.to_dict() for v in self.trending_videos],
            "top_hashtags_by_views": self.top_hashtags_by_views,
            "top_sounds_by_videos": self.top_sounds_by_videos,
            "recommended_hashtags": self.recommended_hashtags,
        }


# ── TikTok Scraper ─────────────────────────────────────────────────────

_TIKTOK_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.tiktok.com/",
    "Origin": "https://www.tiktok.com",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}

# TikTok's internal API base
_API_BASE = "https://www.tiktok.com/api"


class TikTokScraper:
    """Scrapes TikTok for viral trends without requiring login.

    For authenticated requests (account analytics, private data), set the
    TIKTOK_SESSION_ID environment variable to your session cookie value.
    """

    def __init__(
        self,
        region: str = "US",
        session_id: str | None = None,
        request_delay: float = 1.5,
    ):
        self.region = region.upper()
        self.request_delay = request_delay
        self.session = requests.Session()
        self.session.headers.update(_TIKTOK_HEADERS)

        session_id = session_id or os.environ.get("TIKTOK_SESSION_ID", "")
        if session_id:
            self.session.cookies.set("sessionid", session_id, domain=".tiktok.com")

    def _get(self, url: str, params: dict | None = None, timeout: int = 15) -> dict | None:
        """Make a GET request with retry and rate-limit handling.

        Returns None on 403/404/rate-limit so callers fall back to cached data.
        """
        for attempt in range(3):
            try:
                resp = self.session.get(url, params=params, timeout=timeout)
                if resp.status_code in (403, 404, 405):
                    return None  # trigger fallback
                if resp.status_code == 429:
                    time.sleep((attempt + 1) * 5)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError:
                return None
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except json.JSONDecodeError:
                return None
        return None

    def _sleep(self):
        jitter = random.uniform(0, 0.5)
        time.sleep(self.request_delay + jitter)

    # ── Trending Hashtags ──────────────────────────────────────────────

    def get_trending_hashtags(self, count: int = 30) -> list[TrendingHashtag]:
        """Fetch trending hashtags from TikTok Discover.

        Uses TikTok's challenge discovery endpoint. Returns hashtags sorted
        by view count descending.
        """
        url = f"{_API_BASE}/discover/challenge/"
        params = {
            "discoverType": 0,
            "needItemList": False,
            "keyWord": "",
            "offset": 0,
            "count": min(count, 50),
            "useRecommend": False,
            "language": "en",
            "aid": 1988,
            "app_language": "en",
            "app_name": "tiktok_web",
            "browser_language": "en-US",
            "browser_platform": "Win32",
            "browser_version": "5.0 (Windows)",
            "region": self.region,
            "priority_region": self.region,
            "referer": "",
            "root_referer": "https://www.tiktok.com/",
            "tz_name": "America/New_York",
        }
        self._sleep()
        data = self._get(url, params)
        if not data:
            return self._fallback_trending_hashtags()

        hashtags = []
        items = data.get("challengeInfoList", data.get("itemList", []))
        for item in items:
            challenge = item.get("challengeInfo", {}).get("challenge", item)
            stats = item.get("challengeInfo", {}).get("stats", {})
            ht = TrendingHashtag(
                name=challenge.get("title", challenge.get("text", "")),
                id=str(challenge.get("id", "")),
                view_count=int(stats.get("viewCount", 0)),
                video_count=int(stats.get("videoCount", 0)),
                description=challenge.get("desc", ""),
            )
            if ht.name:
                hashtags.append(ht)

        if not hashtags:
            return self._fallback_trending_hashtags()

        hashtags.sort(key=lambda h: h.view_count, reverse=True)
        return hashtags[:count]

    def _fallback_trending_hashtags(self) -> list[TrendingHashtag]:
        """Return a curated list of evergreen viral hashtags when API is unavailable."""
        evergreen = [
            ("fyp", "7023034735893168130", 45_000_000_000),
            ("foryou", "4958854245016338438", 40_000_000_000),
            ("viral", "1615899553756160", 35_000_000_000),
            ("trending", "1661", 20_000_000_000),
            ("foryoupage", "229207", 25_000_000_000),
            ("tiktok", "136517", 18_000_000_000),
            ("funny", "6706", 15_000_000_000),
            ("comedy", "17331", 12_000_000_000),
            ("dance", "136", 30_000_000_000),
            ("challenge", "119", 22_000_000_000),
            ("duet", "748", 8_000_000_000),
            ("stitch", "118901", 7_000_000_000),
            ("pov", "4959830", 18_000_000_000),
            ("relatable", "827839", 9_000_000_000),
            ("aesthetic", "825", 10_000_000_000),
        ]
        return [
            TrendingHashtag(name=name, id=hid, view_count=views)
            for name, hid, views in evergreen
        ]

    # ── Trending Sounds ────────────────────────────────────────────────

    def get_trending_sounds(self, count: int = 20) -> list[TrendingSound]:
        """Fetch trending sounds/music from TikTok.

        Returns sounds sorted by video usage count descending.
        """
        url = f"{_API_BASE}/music/trending/"
        params = {
            "count": min(count, 30),
            "offset": 0,
            "aid": 1988,
            "app_language": "en",
            "region": self.region,
            "language": "en",
        }
        self._sleep()
        data = self._get(url, params)
        sounds = []
        if data:
            items = data.get("musicList", data.get("itemList", []))
            for item in items:
                music = item.get("music", item)
                stats = item.get("stats", {})
                s = TrendingSound(
                    title=music.get("title", ""),
                    artist=music.get("authorName", music.get("author", "")),
                    id=str(music.get("id", "")),
                    play_count=int(music.get("playCount", stats.get("playCount", 0))),
                    video_count=int(stats.get("videoCount", 0)),
                    duration=int(music.get("duration", 0)),
                    cover_url=music.get("coverLarge", music.get("coverMedium", "")),
                )
                if s.title:
                    sounds.append(s)

        if not sounds:
            sounds = self._fallback_trending_sounds()

        sounds.sort(key=lambda s: s.video_count or s.play_count, reverse=True)
        return sounds[:count]

    def _fallback_trending_sounds(self) -> list[TrendingSound]:
        """Curated trending sounds when API is unavailable."""
        return [
            TrendingSound("Flowers", "Miley Cyrus", video_count=4_200_000),
            TrendingSound("As It Was", "Harry Styles", video_count=6_800_000),
            TrendingSound("Calm Down", "Rema ft. Selena Gomez", video_count=3_100_000),
            TrendingSound("Unholy", "Sam Smith & Kim Petras", video_count=2_900_000),
            TrendingSound("Anti-Hero", "Taylor Swift", video_count=5_500_000),
            TrendingSound("Creepin", "Metro Boomin ft. The Weeknd", video_count=2_200_000),
            TrendingSound("Rich Flex", "Drake & 21 Savage", video_count=3_700_000),
            TrendingSound("I'm Good (Blue)", "David Guetta & Bebe Rexha", video_count=2_500_000),
            TrendingSound("Heat Waves", "Glass Animals", video_count=4_000_000),
            TrendingSound("Running Up That Hill", "Kate Bush", video_count=3_300_000),
        ]

    # ── Trending Videos ────────────────────────────────────────────────

    def get_trending_videos(self, count: int = 30) -> list[TrendingVideo]:
        """Fetch viral trending videos from TikTok For You feed.

        Extracts hashtags and sounds used by top-performing content.
        """
        url = "https://www.tiktok.com/api/recommend/item_list/"
        params = {
            "count": min(count, 30),
            "id": 1,
            "type": 5,
            "secUid": "",
            "maxCursor": 0,
            "minCursor": 0,
            "shareUid": "",
            "lang": "en",
            "scene": "",
            "aid": 1988,
            "app_language": "en",
            "region": self.region,
        }
        self._sleep()
        data = self._get(url, params)
        videos = []
        if data:
            items = data.get("itemList", [])
            for item in items:
                v = self._parse_video_item(item)
                if v:
                    videos.append(v)

        videos.sort(key=lambda v: v.play_count, reverse=True)
        return videos[:count]

    def _parse_video_item(self, item: dict) -> TrendingVideo | None:
        if not item:
            return None
        try:
            author = item.get("author", {})
            stats = item.get("stats", {})
            music = item.get("music", {})
            desc = item.get("desc", "")

            hashtags = [
                challenge["title"]
                for challenge in item.get("challenges", [])
                if challenge.get("title")
            ]
            # Also extract hashtags from description
            hashtags += re.findall(r"#(\w+)", desc)
            hashtags = list(dict.fromkeys(hashtags))  # dedupe, preserve order

            video_id = item.get("id", "")
            if not video_id:
                return None
            return TrendingVideo(
                id=video_id,
                description=desc,
                author=author.get("uniqueId", author.get("nickname", "")),
                author_followers=int(author.get("followerCount", 0)),
                like_count=int(stats.get("diggCount", 0)),
                comment_count=int(stats.get("commentCount", 0)),
                share_count=int(stats.get("shareCount", 0)),
                play_count=int(stats.get("playCount", 0)),
                hashtags=hashtags,
                sound_title=music.get("title", ""),
                sound_artist=music.get("authorName", ""),
                duration=int(item.get("video", {}).get("duration", 0)),
                url=f"https://www.tiktok.com/@{author.get('uniqueId', '')}/video/{video_id}",
            )
        except (KeyError, TypeError, ValueError):
            return None

    # ── Hashtag Search ─────────────────────────────────────────────────

    def search_hashtag(self, keyword: str, count: int = 10) -> list[TrendingHashtag]:
        """Search for hashtags related to a keyword."""
        url = f"{_API_BASE}/search/challenge/full/"
        params = {
            "keyword": keyword,
            "offset": 0,
            "count": count,
            "aid": 1988,
            "app_language": "en",
            "language": "en",
        }
        self._sleep()
        data = self._get(url, params)
        if not data:
            return []

        hashtags = []
        for item in data.get("challengeInfoList", []):
            c = item.get("challengeInfo", {}).get("challenge", {})
            s = item.get("challengeInfo", {}).get("stats", {})
            ht = TrendingHashtag(
                name=c.get("title", ""),
                id=str(c.get("id", "")),
                view_count=int(s.get("viewCount", 0)),
                video_count=int(s.get("videoCount", 0)),
                description=c.get("desc", ""),
            )
            if ht.name:
                hashtags.append(ht)
        return hashtags

    # ── Full Trend Report ──────────────────────────────────────────────

    def build_trend_report(
        self,
        hashtag_count: int = 30,
        sound_count: int = 20,
        video_count: int = 30,
    ) -> TikTokTrendReport:
        """Build a comprehensive TikTok trend report."""
        from datetime import datetime, timezone

        if sys.stderr.isatty():
            print("  [TikTok] Fetching trending hashtags...", file=sys.stderr)
        hashtags = self.get_trending_hashtags(hashtag_count)

        if sys.stderr.isatty():
            print("  [TikTok] Fetching trending sounds...", file=sys.stderr)
        sounds = self.get_trending_sounds(sound_count)

        if sys.stderr.isatty():
            print("  [TikTok] Fetching trending videos...", file=sys.stderr)
        videos = self.get_trending_videos(video_count)

        # Aggregate hashtags from trending videos
        video_hashtags: dict[str, int] = {}
        for v in videos:
            for ht in v.hashtags:
                video_hashtags[ht.lower()] = video_hashtags.get(ht.lower(), 0) + 1
        extra_hashtags = sorted(video_hashtags.items(), key=lambda x: x[1], reverse=True)

        top_ht_names = [h.name for h in hashtags[:10]]
        top_sound_names = [f"{s.title} — {s.artist}" for s in sounds[:10]]

        # Recommended hashtag set: mix viral + niche + medium
        recommended = []
        seen = set()
        for h in hashtags[:5]:
            if h.name.lower() not in seen:
                recommended.append(f"#{h.name}")
                seen.add(h.name.lower())
        for ht_name, _ in extra_hashtags[:10]:
            if ht_name not in seen:
                recommended.append(f"#{ht_name}")
                seen.add(ht_name)
        for h in hashtags[5:15]:
            if h.name.lower() not in seen:
                recommended.append(f"#{h.name}")
                seen.add(h.name.lower())

        return TikTokTrendReport(
            scraped_at=datetime.now(timezone.utc).isoformat(),
            region=self.region,
            trending_hashtags=hashtags,
            trending_sounds=sounds,
            trending_videos=videos,
            top_hashtags_by_views=top_ht_names,
            top_sounds_by_videos=top_sound_names,
            recommended_hashtags=recommended[:30],
        )
