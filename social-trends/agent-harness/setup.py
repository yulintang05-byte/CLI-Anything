from setuptools import setup, find_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="Social Trends CLI — viral trend intelligence for content creators",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
        ],
    },
)
