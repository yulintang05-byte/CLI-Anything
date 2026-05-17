from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI-Anything harness for social media trend scraping, account optimization, and theme page management",
    author="CLI-Anything",
    license="MIT",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "requests>=2.31.0",
        "google-api-python-client>=2.100.0",
        "google-auth>=2.23.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "TikTokApi>=6.3.0",
        "playwright>=1.40.0",
        "pandas>=2.0.0",
        "python-dateutil>=2.8.0",
        "tabulate>=0.9.0",
        "rich>=13.0.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "responses>=0.24.0"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social-trends=cli_anything.social_trends.social_trends_cli:main"
        ]
    },
)
