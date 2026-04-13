"""
ContentForge AI Python SDK — Package Setup

Install with:
    pip install -e ./sdk

Or from PyPI (once published):
    pip install contentforge
"""
from setuptools import setup, find_packages

setup(
    name="contentforge",
    version="0.1.0",
    description="Python SDK for the ContentForge AI API",
    long_description=open("sdk/README.md").read() if __import__("os").path.exists("sdk/README.md") else "",
    long_description_content_type="text/markdown",
    author="ContentForge AI",
    author_email="dev@contentforge.ai",
    url="https://github.com/jdev-bot/contentforge-ai",
    license="MIT",
    package_dir={"": "sdk"},
    packages=find_packages(where="sdk"),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "responses>=0.23.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="contentforge ai content sdk api",
)