"""Setup for cli-anything-social-trends."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI harness for scraping viral trends from YouTube & TikTok, optimizing accounts, and building theme pages",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.31",
        "feedparser>=6.0",
    ],
    extras_require={
        "youtube-api": ["google-api-python-client>=2.0"],
    },
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
