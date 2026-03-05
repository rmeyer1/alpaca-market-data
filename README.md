# Alpaca Market Data SDK

A Python SDK for accessing Alpaca's Market Data API.

## Features

- Historical and real-time market data
- Stock and cryptocurrency support
- Rate limiting and retry logic
- Multiple output formats (JSON, CSV, DataFrame)
- CLI tools for quick data access

## Installation

### Using Virtual Environment (Recommended)

It's recommended to use a virtual environment to avoid conflicts with system packages.

**Create virtual environment:**
```bash
# Using venv (Python 3.3+)
python -m venv alpaca-env

# Activate virtual environment
# On macOS/Linux:
source alpaca-env/bin/activate

# On Windows:
alpaca-env\Scripts\activate
```

**Install package:**
```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

**Verify installation:**
```bash
pip list | grep alpaca-market-data
```

**Deactivate when done:**
```bash
deactivate
```

### Alternative Installation Methods

**Global installation (not recommended):**
```bash
pip install -e .
```

For development (global install):
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
