"""Setup for cli-anything-social-intel."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-intel",
    version="1.0.0",
    description="CLI harness for social media intelligence — viral trends, hashtags, music, account optimization, and theme page strategy for YouTube and TikTok",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "prompt_toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "social-intel=cli_anything.social_intel.social_intel_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
