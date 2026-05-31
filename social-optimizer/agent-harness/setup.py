"""Setup for cli-anything-social-optimizer."""
from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-optimizer",
    version="1.0.0",
    description="CLI harness for social media account optimization, viral strategy, and theme page creation",
    packages=find_namespace_packages(include=["cli_anything*"]),
    python_requires=">=3.10",
    install_requires=[
        "click>=8.0",
        "prompt_toolkit>=3.0",
    ],
    entry_points={
        "console_scripts": [
            "social-optimizer=cli_anything.social_optimizer.social_optimizer_cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
