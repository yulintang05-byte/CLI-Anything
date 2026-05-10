from setuptools import setup, find_namespace_packages

setup(
    name="cli-anything-social-trends",
    version="1.0.0",
    description="CLI-Anything harness for YouTube/TikTok trend scraping, account optimization, and theme page tools",
    long_description=open("README.md").read() if __import__("os").path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    author="CLI-Anything",
    python_requires=">=3.10",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    install_requires=[
        "click>=8.0.0",
        "prompt-toolkit>=3.0.0",
        "requests>=2.28.0",
        "google-api-python-client>=2.0.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-mock>=3.0.0"],
    },
    entry_points={
        "console_scripts": [
            "social-trends=cli_anything.social_trends.social_trends_cli:main",
            "cli-anything-social-trends=cli_anything.social_trends.social_trends_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Topic :: Internet",
        "Topic :: Utilities",
    ],
)
