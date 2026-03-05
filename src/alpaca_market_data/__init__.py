"""
Alpaca Market Data SDK

A Python SDK for accessing Alpaca Market Data API.
"""

__version__ = "0.1.0"
__author__ = "rmeyer1"
__email__ = "robmeyer03@gmail.com"

from .client import AlpacaClient
from .models import Bar, Quote, Trade, Snapshot, NewsArticle
from .formatters import to_dataframe, to_csv, to_json

__all__ = [
    "AlpacaClient",
    "Bar",
    "Quote", 
    "Trade",
    "Snapshot",
    "NewsArticle",
    "to_dataframe",
    "to_csv",
    "to_json",
]
