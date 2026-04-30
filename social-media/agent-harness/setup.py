#!/usr/bin/env python3
"""
setup.py for cli-anything-social-media

Install with: pip install -e .
"""

from setuptools import setup, find_namespace_packages

with open("cli_anything/social_media/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cli-anything-social-media",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for social media: viral trend scraping (YouTube + TikTok), "
        "hashtag optimization, account growth, and theme page conversion. "
        "Requires: yt-dlp (optional, for live YouTube data): pip install yt-dlp"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
        "prompt-toolkit>=3.0.0",
    ],
    extras_require={
        "live": [
            "yt-dlp>=2024.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social-media=cli_anything.social_media.social_media_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
