"""Setup script for StockAnalysisHelper"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="stock-analysis-helper",
    version="0.1.0",
    author="JewelIT",
    description="AI powered stock analysis and investment helper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JewelIT/StockAnalysisHelper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
        "yfinance>=0.2.28",
        "transformers>=4.30.0",
        "torch>=2.0.0",
        "vaderSentiment>=3.3.2",
        "feedparser>=6.0.10",
        "newspaper3k>=0.2.8",
        "matplotlib>=3.7.0",
        "mplfinance>=0.12.9",
        "plotly>=5.14.0",
        "openai>=1.0.0",
        "langchain>=0.1.0",
        "tiktoken>=0.5.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "stock-analysis-helper=main:main",
        ],
    },
    include_package_data=True,
    keywords="stock analysis investment ai portfolio sentiment news charts trading",
)
