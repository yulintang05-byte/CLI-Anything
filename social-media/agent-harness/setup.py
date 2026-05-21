"""Setup for cli-anything-social."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social",
    version="1.0.0",
    description="CLI harness for social media intelligence — trending content, hashtags, music, account optimization, and theme page strategy for TikTok, Instagram, and YouTube",
    long_description=(Path(__file__).parent.parent / "SOCIAL.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
    ],
    extras_require={
        "yt-dlp": ["yt-dlp>=2024.1.0"],
    },
    entry_points={
        "console_scripts": [
            "social=cli_anything.social.social_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
