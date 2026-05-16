#!/usr/bin/env python3
"""setup.py for cli-anything-social-media."""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-media",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for social media: viral trend scraping (YouTube/TikTok), "
        "account optimization, hashtag strategy, and theme page intelligence."
    ),
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "yt-dlp>=2024.1.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "social-cli=cli_anything.social_media.social_cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
