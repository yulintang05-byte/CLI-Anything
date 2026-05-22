"""Setup for social-media agent harness."""
from setuptools import setup, find_packages

setup(
    name="social-media-cli",
    version="1.0.0",
    packages=find_packages(),
    py_modules=["cli"],
    entry_points={
        "console_scripts": [
            "social-media=cli:main",
        ],
    },
    python_requires=">=3.10",
    install_requires=[],  # stdlib only — no extra deps
)
