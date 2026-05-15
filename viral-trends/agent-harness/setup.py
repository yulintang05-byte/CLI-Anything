from setuptools import setup, find_packages

setup(
    name="cli-anything-viral-trends",
    version="0.1.0",
    description="Agent-native viral trend scraper, account optimizer, and theme page guide",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "yt-dlp>=2024.1.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "viral-trends=cli_anything.viral_trends.viral_trends_cli:main",
        ],
    },
)
