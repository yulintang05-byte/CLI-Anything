"""Social Trends — agent-native viral trend scraper & account optimizer."""
from .trends import fetch_youtube_trending, fetch_tiktok_trending
from .hashtags import extract_hashtags, rank_hashtags
from .music import fetch_trending_music
from .optimizer import generate_account_audit, optimize_profile
from .theme_pages import get_theme_page_guide

__all__ = [
    "fetch_youtube_trending",
    "fetch_tiktok_trending",
    "extract_hashtags",
    "rank_hashtags",
    "fetch_trending_music",
    "generate_account_audit",
    "optimize_profile",
    "get_theme_page_guide",
]
