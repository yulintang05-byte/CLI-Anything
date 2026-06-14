from setuptools import setup, find_packages

setup(
    name="cli-anything-social-manager",
    version="1.0.0",
    description="CLI-Anything harness for social media trend scraping, account optimization, and theme page management",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.31",
        "rich>=13.0",
        "prompt-toolkit>=3.0",
        "beautifulsoup4>=4.12",
        "pytrends>=4.9",
        "python-dateutil>=2.8",
        "tabulate>=0.9",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-social=cli_anything.social_manager.social_manager_cli:cli",
        ]
    },
)
