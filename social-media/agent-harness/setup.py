#!/usr/bin/env python3
"""
setup.py for cli-anything-social-media

Install with: pip install -e .
"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-media",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for social media automation — scrape YouTube & TikTok "
        "for viral trends, hashtags, and music; optimize accounts; schedule "
        "content; and build converting theme pages."
    ),
    long_description=open("cli_anything/social_media/README.md", "r", encoding="utf-8").read()
    if __import__("os").path.exists("cli_anything/social_media/README.md")
    else "CLI harness for social media intelligence and automation.",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cli-anything-social-media",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "prompt-toolkit>=3.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "youtube-api": [
            "google-api-python-client>=2.0.0",
            "google-auth-oauthlib>=1.0.0",
        ],
        "youtube-search": [
            "youtubesearchpython>=1.6.0",
        ],
        "tiktok": [
            "TikTokApi>=6.0.0",
        ],
        "tiktok-browser": [
            "playwright>=1.40.0",
        ],
        "instagram": [
            "instagrapi>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social=cli_anything.social_media.social_media_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
