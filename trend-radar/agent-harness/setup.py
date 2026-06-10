from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-trend-radar",
    version="0.1.0",
    description="CLI-Anything Trend Radar — viral trend intelligence for YouTube, TikTok, and social media",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    entry_points={
        "console_scripts": [
            "cli-anything-trend-radar=cli_anything.trend_radar.trend_radar_cli:main",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "requests>=2.31.0",
        "prompt-toolkit>=3.0.0",
    ],
    python_requires=">=3.9",
)
