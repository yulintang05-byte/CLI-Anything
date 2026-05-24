"""Setup for viral-trends CLI-Anything agent harness."""

from setuptools import setup, find_packages

setup(
    name="cli-anything-viral-trends",
    version="0.1.0",
    description="CLI-Anything: YouTube & TikTok viral trend scraper + social media account optimizer",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "viral-trends=cli_anything.viral_trends.viral_trends_cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
