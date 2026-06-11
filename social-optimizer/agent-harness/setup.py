#!/usr/bin/env python3
"""setup.py for cli-anything-social-optimizer"""

from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-optimizer",
    version="1.0.0",
    author="cli-anything contributors",
    author_email="",
    description=(
        "CLI harness for social media optimization — account management, "
        "content calendars, theme page playbook, and cross-platform trend synthesis."
    ),
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/HKUDS/CLI-Anything",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    extras_require={
        "full": [
            "cli-anything-tiktok>=1.0.0",
            "cli-anything-youtube>=1.0.0",
        ],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social=cli_anything.social_optimizer.social_optimizer_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
