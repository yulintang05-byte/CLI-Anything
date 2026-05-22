"""Setup for cli-anything-social-media."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-media",
    version="1.0.0",
    description="CLI harness for social media automation — scrape viral trends, optimize accounts, build theme pages",
    long_description=(Path(__file__).parent / "cli_anything" / "social_media" / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.11",
        "prompt_toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "social-media=cli_anything.social_media.social_media_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
