"""
Setup configuration for Professional Messenger CLI.

This file configures the package for installation via pip. It defines:
- Package metadata (name, version, description)
- Dependencies (click, groq, pyyaml)
- Entry points (command-line commands)
- Package discovery

To install in development mode:
    pip install -e .

This creates a 'pm' command that runs the CLI.
"""

from setuptools import setup, find_packages

setup(
    name="professional-messenger",
    version="0.1.0",
    description="Compose professional messages from unstructured thoughts using AI",
    author="Gourav Khurana",
    python_requires=">=3.8",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "groq>=0.4.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "pm=src.cli:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Email",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
