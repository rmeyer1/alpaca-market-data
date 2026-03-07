# Alpaca Market Data SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)

A comprehensive Python SDK for accessing Alpaca's Market Data API with both programmatic access and CLI tools.

## ✨ Features

- 📊 **Historical & Real-time Data**: OHLCV bars, quotes, trades, news, and market snapshots
- 💰 **Multi-Asset Support**: Stocks, ETFs, and cryptocurrencies
- 🛠️ **Multiple Output Formats**: JSON, CSV, and pandas DataFrames
- ⚡ **CLI Tools**: Quick command-line access for all endpoints
- 🔒 **Rate Limiting**: Built-in rate limiting and retry logic
- 🏗️ **Robust Architecture**: Clean, typed, and well-documented code

## 🚀 Quick Start (Under 5 Minutes)

### 1. Installation

```bash
# Clone and setup
git clone https://github.com/rmeyer1/alpaca-market-data.git
cd alpaca-market-data

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### 2. Configuration

Get your API credentials from [Alpaca Dashboard](https://app.alpaca.markets/paper/dashboard):

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# ALPACA_API_KEY=your_api_key_here
# ALPACA_API_SECRET=your_secret_key_here
```

### 3. First API Call

```python
from alpaca_data import AlpacaClient

# Initialize client (auto-loads from environment)
client = AlpacaClient()

# Get your first data!
bars = client.get_bars("AAPL", timeframe="1Day", start="2024-01-01")
print(f"Got {len(bars['bars'])} bars for AAPL")
```

**🎉 You're ready to go!**

## 📖 Comprehensive Examples

### Python API Examples

<details>
<summary><strong>📊 Historical Bars</strong></summary>

```python
from alpaca_data import AlpacaClient

client = AlpacaClient()

# Single symbol
bars = client.get_bars(
    symbols="AAPL",
    timeframe="1Day",
    start="2024-01-01",
    end="2024-01-31"
)

# Multiple symbols with pandas DataFrame
bars_df = client.get_bars(
    symbols=["AAPL", "GOOGL", "MSFT"],
    timeframe="1Hour",
    limit=100
)['bars']

print(bars_df.head())  # Shows first few bars
```

</details>

<details>
<summary><strong>📈 Real-time Quotes</strong></summary>

```python
# Get current bid/ask prices
quotes = client.get_quotes(
    symbols=["AAPL", "TSLA"],
    limit=5
)

for quote in quotes['quotes']:
    print(f"{quote.symbol}: ${quote.bid_price} x {quote.bid_size} / ${quote.ask_price} x {quote.ask_size}")
```

</details>

<details>
<summary><strong>📰 Market News</strong></summary>

```python
# Get latest news
news = client.get_news(
    symbols=["AAPL", "GOOGL"],
    limit=10,
    include_content=True
)

for article in news['news']:
    print(f"{article.headline} - {article.source}")
    if article.summary:
        print(f"Summary: {article.summary[:100]}...")
```

</details>

<details>
<summary><strong>🔍 Market Snapshots</strong></summary>

```python
# Get comprehensive market data
snapshots = client.get_snapshot(
    symbols=["AAPL", "TSLA", "SPY"]
)

for snapshot in snapshots['snapshots']:
    print(f"{snapshot.symbol}:")
    if snapshot.latest_trade:
        print(f"  Last trade: ${snapshot.latest_trade.price} x {snapshot.latest_trade.size}")
    if snapshot.latest_quote:
        print(f"  Quote: ${snapshot.latest_quote.bid_price} - ${snapshot.latest_quote.ask_price}")
```

</details>

<details>
<summary><strong>₿ Cryptocurrency Data</strong></summary>

```python
# Crypto bars
crypto_bars = client.get_crypto_bars(
    symbols=["BTC/USD", "ETH/USD"],
    timeframe="1Hour",
    exchange="CBSE"
)

# Crypto quotes
crypto_quotes = client.get_crypto_quotes(
    symbols=["BTC/USD"]
)

# Crypto snapshots
crypto_snapshots = client.get_crypto_snapshot(
    symbols=["BTC/USD", "ETH/USD"]
)
```

</details>

### CLI Examples

<details>
<summary><strong>💻 Command Line Interface</strong></summary>

```bash
# Historical bars
alpaca-bars AAPL GOOGL --timeframe 1Day --start 2024-01-01 --format json --output bars.json

# Real-time quotes
alpaca-quotes AAPL TSLA --format csv --output quotes.csv

# Market news
alpaca-news --symbols AAPL TSLA --limit 5 --include-content --format json

# Market snapshots
alpaca-snapshot AAPL MSFT --verbose

# Crypto data
alpaca-crypto bars BTC/USD ETH/USD --timeframe 1Hour --format dataframe

# Multiple output formats
alpaca-bars AAPL --format csv --output-file aapl_daily.csv
alpaca-bars AAPL --format dataframe --output-file aapl_analysis.xlsx
```

</details>

## 🛠️ API Reference

### Core Classes

#### AlpacaClient

Main client for accessing Alpaca Market Data API.

```python
from alpaca_data import AlpacaClient

# Basic initialization
client = AlpacaClient()

# With custom credentials
client = AlpacaClient(
    api_key="your_key",
    secret_key="your_secret"
)

# With rate limiting
client = AlpacaClient(
    rate_limit_per_minute=50
)
```

### Methods

| Method | Description | Parameters |
|--------|-------------|------------|
| `get_bars()` | Historical OHLCV bars | `symbols`, `timeframe`, `start`, `end`, `limit` |
| `get_quotes()` | Real-time quotes | `symbols`, `limit` |
| `get_trades()` | Real-time trades | `symbols`, `limit` |
| `get_news()` | Market news | `symbols`, `limit`, `include_content` |
| `get_snapshot()` | Market snapshots | `symbols` |
| `get_crypto_bars()` | Crypto bars | `symbols`, `timeframe`, `exchange` |
| `get_crypto_quotes()` | Crypto quotes | `symbols`, `exchange` |
| `get_crypto_snapshot()` | Crypto snapshots | `symbols`, `exchange` |

### Output Formats

All methods support multiple output formats:

```python
# Dictionary (default)
result = client.get_bars("AAPL")  # Returns dict

# Pandas DataFrame
bars_df = client.get_bars("AAPL", output_format="dataframe")

# JSON string
json_data = client.get_bars("AAPL", output_format="json")

# CSV
csv_data = client.get_bars("AAPL", output_format="csv")
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_secret_key_here

# Optional
ALPACA_BASE_URL=https://data.alpaca.markets  # Default for live data
ALPACA_PAPER_BASE_URL=https://data-paper.alpaca.markets  # For paper trading
ALPACA_RATE_LIMIT_PER_MINUTE=50  # Rate limit
```

### Initialization Options

```python
from alpaca_data import AlpacaClient

# Environment variables (recommended)
client = AlpacaClient()

# Explicit credentials
client = AlpacaClient(
    api_key="AKBEXAMPLE",
    secret_key="your_secret"
)

# Custom base URL
client = AlpacaClient(
    base_url="https://data-paper.alpaca.markets"
)

# Custom rate limiting
client = AlpacaClient(
    rate_limit_per_minute=30
)
```

## ⚙️ CLI Tools

Install CLI tools with the package:

```bash
pip install -e .
```

Available commands:

| Command | Description | Example |
|---------|-------------|---------|
| `alpaca-bars` | Get historical bars | `alpaca-bars AAPL --timeframe 1Day` |
| `alpaca-quotes` | Get real-time quotes | `alpaca-quotes AAPL TSLA` |
| `alpaca-trades` | Get recent trades | `alpaca-trades AAPL` |
| `alpaca-news` | Get market news | `alpaca-news --symbols AAPL` |
| `alpaca-snapshot` | Get market snapshots | `alpaca-snapshot AAPL` |
| `alpaca-crypto` | Crypto data commands | `alpaca-crypto bars BTC/USD` |

### CLI Help

```bash
# General help
alpaca-bars --help

# Specific option help
alpaca-bars AAPL --help
```

## 📊 Data Models

### Bar

```python
class Bar:
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    trade_count: int
    vwap: float
```

### Quote

```python
class Quote:
    symbol: str
    timestamp: datetime
    bid_price: float
    bid_size: float
    ask_price: float
    ask_size: float
    exchange: str
```

### Trade

```python
class Trade:
    symbol: str
    timestamp: datetime
    price: float
    size: float
    exchange: str
```

### News

```python
class News:
    id: str
    headline: str
    author: str
    created_at: datetime
    updated_at: datetime
    source: str
    summary: str
    content: str
    symbols: List[str]
    url: str
```

## 🧪 Testing

Run the test suite:

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_task_17.py::TestCLIScripts::test_get_bars_basic -v

# Run with coverage
pytest tests/ --cov=src/alpaca_data --cov-report=html
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/rmeyer1/alpaca-market-data.git
cd alpaca-market-data

# Create development environment
python -m venv venv
source venv/bin/activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest
```

### Code Quality

```bash
# Format code
black src/ tests/ scripts/

# Lint code
ruff src/ tests/ scripts/

# Type checking
mypy src/
```

## 📝 Examples Directory

See the `/examples` directory for comprehensive examples:

- `python/` - Python API examples
- `cli/` - CLI usage examples  
- `notebooks/` - Jupyter notebook examples

## 🚨 Rate Limiting

The SDK includes automatic rate limiting:

- **Default**: 50 requests per minute
- **Configurable**: Set via `rate_limit_per_minute` parameter
- **Smart Backoff**: Automatic retries with exponential backoff
- **Queue Management**: Requests are queued when limits are reached

```python
client = AlpacaClient(rate_limit_per_minute=30)
```

## 🔗 Dependencies

- `alpaca-py >= 0.8.0` - Alpaca API client
- `pandas >= 1.5.0` - Data analysis
- `typer >= 0.9.0` - CLI framework
- `requests >= 2.28.0` - HTTP client
- `python-dotenv >= 1.0.0` - Environment variables

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## 🐛 Troubleshooting

### Common Issues

**API Authentication Error:**
```python
# Check your environment variables
import os
print(f"API Key: {os.getenv('ALPACA_API_KEY')}")
print(f"Secret: {os.getenv('ALPACA_API_SECRET')}")
```

**Rate Limit Exceeded:**
```python
# Reduce rate limiting or add delays
client = AlpacaClient(rate_limit_per_minute=30)
```

**No Data Returned:**
- Check if market is open
- Verify symbol is correct (e.g., "AAPL" not "Apple")
- Ensure date range is valid

### Getting Help

- 📚 [Documentation](https://alpaca.markets/docs/market-data)
- 🐛 [GitHub Issues](https://github.com/rmeyer1/alpaca-market-data/issues)
- 💬 [Alpaca Community](https://alpaca.markets/community)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📈 What's New

### v0.1.0 - Current Release
- ✅ Complete Python API for all Alpaca Market Data endpoints
- ✅ CLI tools for all major functions
- ✅ Multi-format output (JSON, CSV, DataFrame)
- ✅ Comprehensive rate limiting
- ✅ Full test coverage
- ✅ Crypto and stock data support

---

**Ready to start building?** Check out the [examples directory](examples/) for practical usage patterns!