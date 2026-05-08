"""Setup for cli-anything-trend-scout."""

from setuptools import setup, find_packages

setup(
    name="cli-anything-trend-scout",
    version="1.0.0",
    description="YouTube & TikTok viral trend scraper, account optimizer, and theme page strategist",
    author="CLI-Anything",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "prompt-toolkit>=3.0",
    ],
    extras_require={
        "youtube-api": ["google-api-python-client>=2.0"],
        "tiktok-api": ["TikTokApi>=6.0"],
        "ytdlp": ["yt-dlp>=2024.0"],
        "all": [
            "google-api-python-client>=2.0",
            "TikTokApi>=6.0",
            "yt-dlp>=2024.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trend-scout=cli_anything.trend_scout.trend_scout_cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
