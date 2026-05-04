from setuptools import find_packages, setup

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI agent harness for social media trend scraping and account optimisation",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.28.0",
        "google-api-python-client>=2.0.0",
        "google-auth-oauthlib>=0.4.0",
    ],
    extras_require={
        "tiktok-live": [
            "TikTokApi>=6.0.0",
            "playwright>=1.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.cli:cli",
        ],
    },
)
