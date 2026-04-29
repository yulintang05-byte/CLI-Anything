from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI-Anything harness for YouTube & TikTok viral trend scraping, account optimization, and theme page strategy",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "requests>=2.28.0",
        "google-api-python-client>=2.80.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "python-dotenv>=1.0.0",
        "tabulate>=0.9.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "responses>=0.23.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social=cli_anything.social_trends.__main__:main",
        ]
    },
)
