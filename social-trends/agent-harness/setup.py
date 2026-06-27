"""Setup for cli-anything-social-trends."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description=(
        "CLI harness for viral trend intelligence — "
        "scrape YouTube & TikTok trends, hashtags, music; "
        "optimize accounts; convert theme pages"
    ),
    long_description=(
        Path(__file__).parent / "cli_anything" / "social_trends" / "README.md"
    ).read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
    ],
    extras_require={
        "apify": ["httpx>=0.24"],
    },
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
