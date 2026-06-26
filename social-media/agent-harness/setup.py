"""Setup for cli-anything-social-media."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-media",
    version="1.0.0",
    description="CLI harness for social media — viral trend scraping, hashtag optimization, theme page strategy, account optimization for TikTok, YouTube, and Instagram",
    long_description=(Path(__file__).parent / "cli_anything" / "social_media" / "README.md").read_text()
    if (Path(__file__).parent / "cli_anything" / "social_media" / "README.md").exists()
    else "Social Media CLI harness for CLI-Anything",
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
    ],
    extras_require={
        "scraping": [
            "requests>=2.28",
            "beautifulsoup4>=4.11",
        ],
    },
    entry_points={
        "console_scripts": [
            "social-media=cli_anything.social_media.social_media_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Internet",
        "Topic :: Multimedia :: Video",
    ],
)
