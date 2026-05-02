#!/usr/bin/env python3
"""
setup.py for cli-anything-social

Install with: pip install -e .
Or publish: python -m build && twine upload dist/*
"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for Social Media — YouTube/TikTok trend scraping, "
        "account optimisation, and theme page conversion playbooks."
    ),
    long_description=(
        open("cli_anything/social/README.md", "r", encoding="utf-8").read()
        if __import__("os").path.exists("cli_anything/social/README.md")
        else "CLI harness for social media management."
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cli-anything-social",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
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
            "responses>=0.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social=cli_anything.social.social_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
