"""Setup for cli-anything-trendscout."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-trendscout",
    version="1.0.0",
    description="CLI harness for viral trend intelligence — scrape YouTube & TikTok for trends, hashtags, and music",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
        "requests>=2.28",
    ],
    extras_require={
        "ytdlp": ["yt-dlp>=2024.1.1"],
    },
    entry_points={
        "console_scripts": [
            "trendscout=cli_anything.trendscout.trendscout_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
