#!/usr/bin/env python3
"""
setup.py for cli-anything-social-trends

Install with: pip install -e .
"""

from setuptools import setup, find_namespace_packages

with open("cli_anything/social_trends/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for viral social media trend scraping and account optimization. "
        "Scrapes YouTube & TikTok trending videos, hashtags, and music. "
        "Optional dependency: yt-dlp (pip install yt-dlp) for enhanced YouTube data."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
    ],
    extras_require={
        "enhanced": [
            "yt-dlp>=2024.1.0",   # Better YouTube data extraction
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
