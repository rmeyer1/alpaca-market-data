# Alpaca Market Data SDK

A Python SDK for accessing Alpaca's Market Data API.

## Features

- Historical and real-time market data
- Stock and cryptocurrency support
- Rate limiting and retry logic
- Multiple output formats (JSON, CSV, DataFrame)
- CLI tools for quick data access

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and add your API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your credentials from [Alpaca Dashboard](https://app.alpaca.markets/paper/dashboard).

## Quick Start

```python
from alpaca_data import AlpacaClient

# Initialize client (loads from environment variables)
client = AlpacaClient()

# Get historical bars
bars = client.get_bars("AAPL", timeframe="1Day", start="2024-01-01")
```

## CLI Usage

```bash
# Get historical bars
alpaca-bars AAPL MSFT --timeframe 1Day --start 2024-01-01 --output json

# Get quotes
alpaca-quotes AAPL --output csv

# Get news
alpaca-news --symbols AAPL TSLA --limit 10

# Get snapshots
alpaca-snapshot AAPL MSFT GOOGL

# Get crypto data
alpaca-crypto bars BTC/USD ETH/USD --timeframe 1Hour
```

## License

MIT
