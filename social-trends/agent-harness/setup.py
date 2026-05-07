from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI-Anything harness for viral trend scraping, hashtag analysis, account optimization, and theme page building",
    long_description=open("SOCIAL_TRENDS.md").read(),
    long_description_content_type="text/markdown",
    author="CLI-Anything",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything*"]),
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
    ],
    extras_require={
        "youtube": ["yt-dlp>=2024.1.1"],
        "tiktok-playwright": ["TikTokApi>=6.0.0", "playwright>=1.40.0"],
        "full": [
            "yt-dlp>=2024.1.1",
            "TikTokApi>=6.0.0",
            "playwright>=1.40.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Video",
    ],
)
