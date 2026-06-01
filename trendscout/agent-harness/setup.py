"""Setup for cli-anything-trendscout."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-trendscout",
    version="1.0.0",
    description="CLI harness for viral trend intelligence — scrape YouTube & TikTok trends, optimize social accounts, and build theme pages",
    long_description=(Path(__file__).parent / "cli_anything" / "trendscout" / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
    ],
    extras_require={
        "live": [
            "yt-dlp>=2024.1.0",
            "requests>=2.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "trendscout=cli_anything.trendscout.trendscout_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
