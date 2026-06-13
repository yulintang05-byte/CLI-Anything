from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social",
    version="1.0.0",
    description="CLI-Anything harness for social media trend scraping & account optimization",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "beautifulsoup4>=4.11",
        "yt-dlp>=2023.1",
        "rich>=13.0",
        "python-dateutil>=2.8",
        "tabulate>=0.9",
        "colorama>=0.4",
    ],
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social.__main__:main",
        ]
    },
    python_requires=">=3.10",
)
