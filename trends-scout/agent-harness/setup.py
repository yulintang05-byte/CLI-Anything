#!/usr/bin/env python3
"""setup.py for cli-anything-trends-scout"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-trends-scout",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for viral trend intelligence — scrapes YouTube & TikTok for "
        "trending videos, hashtags, and music. Optimizes account strategy and "
        "provides a theme page conversion playbook."
    ),
    long_description=open("cli_anything/trends_scout/README.md", encoding="utf-8").read()
    if __import__("os").path.exists("cli_anything/trends_scout/README.md")
    else "CLI harness for social media trend intelligence.",
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
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
        "requests>=2.28.0",
        "prompt-toolkit>=3.0.0",
    ],
    extras_require={
        "full": [
            "pytrends>=4.9.0",   # Google Trends data
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "responses>=0.23.0",  # HTTP mocking
        ],
    },
    entry_points={
        "console_scripts": [
            "trends-scout=cli_anything.trends_scout.trends_scout_cli:main",
            "cli-anything-trends-scout=cli_anything.trends_scout.trends_scout_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
