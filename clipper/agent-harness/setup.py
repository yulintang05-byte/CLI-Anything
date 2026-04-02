"""Setup for cli-anything-clipper."""
from pathlib import Path
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-clipper",
    version="1.0.0",
    description="CLI harness for video clipping — create highlight clips for Whop, TikTok, Twitch, YouTube",
    long_description=(Path(__file__).parent / "cli_anything" / "clipper" / "README.md").read_text(),
    long_description_content_type="text/markdown",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "clipper=cli_anything.clipper.clipper_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
