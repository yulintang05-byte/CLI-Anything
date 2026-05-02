from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="Agent-native social media trends tracker, hashtag engine, and account optimizer",
    author="CLI-Anything Contributors",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "prompt_toolkit>=3.0",
    ],
    extras_require={
        "scrape": ["yt-dlp>=2024.1"],
    },
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
        ]
    },
)
