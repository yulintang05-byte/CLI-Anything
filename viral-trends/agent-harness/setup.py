"""Setup for cli-anything-viraltrends."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-viraltrends",
    version="1.0.0",
    description="CLI harness for YouTube + TikTok viral trend intelligence — hashtags, music, account optimization, theme pages",
    long_description=(Path(__file__).parent / "cli_anything" / "viraltrends" / "README.md").read_text()
    if (Path(__file__).parent / "cli_anything" / "viraltrends" / "README.md").exists()
    else "",
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
    ],
    extras_require={
        "scraper": [
            "yt-dlp>=2024.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "viraltrends=cli_anything.viraltrends.viraltrends_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
