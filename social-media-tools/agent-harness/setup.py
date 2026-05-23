from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social",
    version="1.0.0",
    description="Social media trend scraper, account optimizer, and theme page toolkit",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "yt-dlp>=2024.1.0",
        "aiohttp>=3.8.0",
        "beautifulsoup4>=4.12.0",
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "social=cli_anything.social.social_cli:cli",
            "cli-anything-social=cli_anything.social.social_cli:cli",
        ],
    },
)
