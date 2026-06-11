from setuptools import setup, find_packages

setup(
    name="social-trends",
    version="1.0.0",
    description="Viral trend scraping, hashtag optimization, and theme page strategy CLI",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
    ],
    extras_require={
        "youtube_api": ["google-api-python-client>=2.0"],
        "trends": ["pytrends>=4.9"],
        "dev": ["pytest>=7.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "social-trends=social_trends.agent_harness.cli:cli",
        ],
    },
)
