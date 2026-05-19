from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trend-scout",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "google-api-python-client>=2.0.0",
        "TikTokApi>=6.0.0",
        "playwright>=1.40.0",
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
        "pytz>=2023.3",
        "rich>=13.0.0",
        "tabulate>=0.9.0",
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-social-trend-scout=cli_anything.social_trend_scout.social_trend_scout_cli:cli",
        ],
    },
)
