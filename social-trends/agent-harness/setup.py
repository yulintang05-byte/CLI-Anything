#!/usr/bin/env python3
"""
setup.py for cli-anything-social-trends

Install with: pip install -e .
Or publish to PyPI: python -m build && twine upload dist/*
"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for viral trend scraping — YouTube Data API v3 + TikTok Research API. "
        "Surfaces trending videos, music, and hashtags; optimizes social media accounts; "
        "and provides complete theme page creation + monetization playbooks."
    ),
    long_description=open("cli_anything/social_trends/README.md", "r", encoding="utf-8").read()
    if __import__("os").path.exists("cli_anything/social_trends/README.md")
    else "CLI harness for social media trend intelligence and account optimization.",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cli-anything-social-trends",
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
        "requests>=2.28.0",
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
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
