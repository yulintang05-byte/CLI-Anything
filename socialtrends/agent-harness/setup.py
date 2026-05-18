from setuptools import setup, find_packages

setup(
    name="cli-anything-socialtrends",
    version="1.0.0",
    description="Social media trend scraping, hashtag analysis, and account optimization",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.11",
        "google-api-python-client>=2.0",
        "pytrends>=4.9",
        "python-dateutil>=2.8",
    ],
    extras_require={
        "dev": ["pytest>=7.0"],
    },
    entry_points={
        "console_scripts": [
            "socialtrends=cli_anything.socialtrends.socialtrends_cli:main",
        ],
    },
)
