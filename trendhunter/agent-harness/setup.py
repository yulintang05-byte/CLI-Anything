from setuptools import setup, find_packages

setup(
    name="cli-anything-trendhunter",
    version="1.0.0",
    description="CLI harness for scraping viral trends, optimizing social accounts, and building converting theme pages",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.11",
        "lxml>=4.9",
        "prompt-toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-trendhunter=cli_anything.trendhunter.trendhunter_cli:cli",
        ]
    },
)
