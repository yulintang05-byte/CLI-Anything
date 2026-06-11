#!/usr/bin/env python3
"""setup.py for cli-anything-youtube"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-youtube",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for YouTube — scrape viral trends, extract hashtags, "
        "research SEO keywords, and optimize your channel for growth."
    ),
    long_description=open("cli_anything/youtube/README.md", encoding="utf-8").read()
    if __import__("pathlib").Path("cli_anything/youtube/README.md").exists()
    else "",
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
        "requests>=2.28.0",
        "prompt-toolkit>=3.0.0",
        "yt-dlp>=2024.1.0",
    ],
    extras_require={
        "api": ["google-api-python-client>=2.0.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-youtube=cli_anything.youtube.youtube_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
