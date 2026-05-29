"""Setup for cli-anything-viral-trends."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-viral-trends",
    version="1.0.0",
    description="CLI harness for YouTube/TikTok viral trend analysis, account optimization, and content scheduling",
    long_description=(Path(__file__).parent / "cli_anything" / "viral_trends" / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
    ],
    entry_points={
        "console_scripts": [
            "viral-trends=cli_anything.viral_trends.viral_trends_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
