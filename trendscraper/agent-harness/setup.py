"""Setup for cli-anything-trendscraper."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-trendscraper",
    version="1.0.0",
    description="CLI harness for scraping viral trends, hashtags, and music from YouTube and TikTok — optimize social accounts and build converting theme pages",
    long_description=(Path(__file__).parent / "cli_anything" / "trendscraper" / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "google-api-python-client>=2.100.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0", "pytest-httpx>=0.30.0"],
    },
    entry_points={
        "console_scripts": [
            "trendscraper=cli_anything.trendscraper.trendscraper_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
