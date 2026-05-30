#!/usr/bin/env python3
"""setup.py for cli-anything-social-trends"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for Social Media Trends — scrape YouTube & TikTok for viral trends, "
        "hashtags, and music; optimize accounts; build theme pages. "
        "Requires: yt-dlp (pip install yt-dlp), httpx, beautifulsoup4"
    ),
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Video",
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
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "prompt-toolkit>=3.0.0",
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
