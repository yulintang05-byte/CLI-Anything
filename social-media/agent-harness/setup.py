#!/usr/bin/env python3
"""setup.py for cli-anything-social-media"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-media",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for social media growth — viral trend discovery (YouTube/TikTok), "
        "hashtag optimizer, account auditor, theme page playbook, and content calendar."
    ),
    long_description=open("SOCIAL_MEDIA.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
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
        "prompt-toolkit>=3.0.0",
    ],
    extras_require={
        "trends": [
            "pytrends>=4.9.0",      # Google Trends integration
            "yt-dlp>=2024.1.1",     # YouTube trending (most reliable)
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "social-media=cli_anything.social_media.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
