#!/usr/bin/env python3
"""
Alpaca Market Data SDK
A Python SDK for accessing Alpaca Market Data API
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="alpaca-market-data",
    version="0.1.0",
    author="rmeyer1",
    author_email="robmeyer03@gmail.com",
    description="A Python SDK for accessing Alpaca Market Data API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmeyer1/alpaca-market-data",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "alpaca-bars=alpaca_data.cli.bars:main",
            "alpaca-quotes=alpaca_data.cli.quotes:main",
            "alpaca-news=alpaca_data.cli.news:main",
            "alpaca-snapshot=alpaca_data.cli.snapshot:main",
            "alpaca-trades=alpaca_data.cli.trades:main",
            "alpaca-crypto=alpaca_data.cli.crypto:main",
            "alpaca-option-quotes=alpaca_data.cli.option_quotes:main",
            "alpaca-option-snapshot=alpaca_data.cli.option_snapshot:main",
            "alpaca-option-trades=alpaca_data.cli.option_trades:main",
            "alpaca-option-chain=alpaca_data.cli.option_chain:main",
        ],
    },
)
