#!/usr/bin/env python3
"""setup.py for cli-anything-social-trends

Install with: pip install -e .
"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    author="cli-anything contributors",
    description=(
        "CLI harness for Social Media Trend Intelligence — "
        "scrapes YouTube & TikTok for viral trends, hashtags, and music; "
        "optimizes accounts; guides theme page creation and monetization. "
        "Requires: yt-dlp (pip install yt-dlp), requests (pip install requests)"
    ),
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "yt-dlp>=2024.1.0",
        "requests>=2.31.0",
    ],
    extras_require={
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
