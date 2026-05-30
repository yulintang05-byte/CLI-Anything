from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="Agent-native social media trend scraper — YouTube & TikTok viral trends, hashtags, music, and account optimization",
    packages=find_namespace_packages(include=["cli_anything*"]),
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
        "lxml>=4.9",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-social-trends=cli_anything.social_trends.social_trends_cli:main",
        ]
    },
    python_requires=">=3.10",
)
