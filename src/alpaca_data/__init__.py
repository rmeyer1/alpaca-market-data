"""Alpaca Market Data SDK - Python SDK for Alpaca Market Data API.

This package provides a Python SDK for accessing Alpaca's market data API,
including stock and cryptocurrency historical and real-time data.

Example:
    >>> from alpaca_data import AlpacaClient
    >>> client = AlpacaClient()
    >>> bars = client.get_bars("AAPL", timeframe="1Day", start="2024-01-01")
"""

__version__ = "0.1.0"
__author__ = "Alpaca Market Data SDK Contributors"
__license__ = "MIT"

from .client import AlpacaClient
from .rate_limiter import RateLimiter, RateLimitStrategy
from .exceptions import (
    AlpacaAPIError,
    AlpacaAuthError,
    AlpacaRateLimitError,
    AlpacaNotFoundError,
    AlpacaValidationError,
)
from .models import Bar, Quote, Trade, Snapshot, News
from .formatters import (
    OutputFormatter,
    JSONFormatter,
    CSVFormatter,
    DataFrameFormatter,
    format_output,
    to_json,
    to_csv,
    to_dataframe,
)

__all__ = [
    "AlpacaClient",
    "RateLimiter",
    "RateLimitStrategy",
    "AlpacaAPIError",
    "AlpacaAuthError",
    "AlpacaRateLimitError",
    "AlpacaNotFoundError",
    "AlpacaValidationError",
    "Bar",
    "Quote",
    "Trade",
    "Snapshot",
    "News",
    "OutputFormatter",
    "JSONFormatter",
    "CSVFormatter",
    "DataFrameFormatter",
    "format_output",
    "to_json",
    "to_csv",
    "to_dataframe",
]
