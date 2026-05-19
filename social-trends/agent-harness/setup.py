from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
        ],
    },
    python_requires=">=3.10",
)
