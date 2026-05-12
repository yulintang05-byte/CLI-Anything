from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI harness for YouTube & TikTok viral trend research and account optimization",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "google-api-python-client>=2.0",
    ],
    extras_require={
        "repl": ["prompt-toolkit>=3.0"],
        "dev": ["pytest>=7.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "cli-anything-social-trends=cli_anything.social_trends.cli:main",
        ],
    },
    package_data={
        "cli_anything.social_trends": ["*.md", "tests/*.md"],
    },
)
