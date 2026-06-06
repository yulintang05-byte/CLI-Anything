"""Setup for cli-anything-trend-scout."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-trend-scout",
    version="1.0.0",
    description="CLI harness for scraping YouTube/TikTok viral trends, hashtags, and music — optimize theme pages and social accounts",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
        "requests>=2.31",
        "yt-dlp>=2024.1",
    ],
    extras_require={
        "full": [
            "playwright>=1.40",
            "beautifulsoup4>=4.12",
        ]
    },
    entry_points={
        "console_scripts": [
            "trend-scout=cli_anything.trend_scout.trend_scout_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
