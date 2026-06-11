#!/usr/bin/env python3
"""setup.py for cli-anything-tiktok"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-tiktok",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for TikTok — scrape viral trends, hashtags, and sounds; "
        "optimize account growth with data-driven strategies."
    ),
    long_description=open("cli_anything/tiktok/README.md", encoding="utf-8").read()
    if __import__("pathlib").Path("cli_anything/tiktok/README.md").exists()
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
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-tiktok=cli_anything.tiktok.tiktok_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
