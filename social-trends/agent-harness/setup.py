from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trends",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.12",
        "lxml>=4.9",
        "pytrends>=4.9",
    ],
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.cli:main",
        ],
    },
    python_requires=">=3.10",
)
