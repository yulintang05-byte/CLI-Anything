"""Setup for cli-anything-viral-trends."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-viral-trends",
    version="1.0.0",
    description="CLI harness for viral trend intelligence — scrape YouTube & TikTok for trending hashtags, music, and content",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.31",
        "yt-dlp>=2024.1.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-mock>=3.0"],
    },
    entry_points={
        "console_scripts": [
            "viral-trends=cli_anything.viral_trends.trends_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
