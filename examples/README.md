# Alpaca Market Data SDK Examples

This directory contains comprehensive examples showing how to use the Alpaca Market Data SDK for various use cases.

## 📁 Directory Structure

```
examples/
├── README.md                 # This file
├── python/                   # Python API examples
│   ├── basic_usage.py        # Basic market data patterns
│   └── advanced_usage.py     # Advanced patterns and best practices
├── cli/                      # Command-line interface examples
│   ├── basic_cli_usage.sh    # Basic CLI commands
│   └── advanced_cli_usage.sh # Advanced CLI workflows
└── notebooks/                # Jupyter notebook examples
    └── market_analysis.ipynb # Comprehensive market analysis
```

## 🚀 Quick Start Examples

### Python API

```python
from alpaca_data import AlpacaClient

# Initialize client
client = AlpacaClient()

# Get historical bars
bars = client.get_bars("AAPL", timeframe="1Day", start="2024-01-01")
print(f"Got {len(bars['bars'])} bars")

# Get real-time quotes
quotes = client.get_quotes(["AAPL", "GOOGL"])
for quote in quotes['quotes']:
    print(f"{quote.symbol}: ${quote.bid_price:.2f} - ${quote.ask_price:.2f}")

# Get market snapshots
snapshots = client.get_snapshot(["AAPL", "TSLA"])
for snapshot in snapshots['snapshots']:
    print(f"{snapshot.symbol}: Last trade ${snapshot.latest_trade.price:.2f}")
```

### CLI Commands

```bash
# Install CLI tools
pip install -e .

# Basic usage
alpaca-bars AAPL --timeframe 1Day --limit 10
alpaca-quotes AAPL GOOGL
alpaca-snapshot AAPL MSFT

# Save to files
alpaca-bars AAPL --format json --output-file data.json
alpaca-quotes AAPL --format csv --output-file quotes.csv

# Cryptocurrency data
alpaca-crypto bars BTC/USD --timeframe 1Hour
```

## 📋 Example Categories

### 1. Basic Usage (`python/basic_usage.py`)

**What it covers:**
- Client initialization
- Basic API calls
- Historical bars, quotes, snapshots, news
- Error handling basics

**Run it:**
```bash
python examples/python/basic_usage.py
```

### 2. Advanced Usage (`python/advanced_usage.py`)

**What it covers:**
- Multiple symbols analysis
- Different output formats (JSON, CSV, DataFrame)
- Rate limiting best practices
- Data export and saving
- Error handling patterns

**Run it:**
```bash
python examples/python/advanced_usage.py
```

### 3. Basic CLI (`cli/basic_cli_usage.sh`)

**What it covers:**
- All basic CLI commands
- Interactive examples
- Help and documentation
- Common workflows

**Run it:**
```bash
chmod +x examples/cli/basic_cli_usage.sh
./examples/cli/basic_cli_usage.sh
```

### 4. Advanced CLI (`cli/advanced_cli_usage.sh`)

**What it covers:**
- Complex query examples
- Batch processing
- Data analysis pipelines
- Workflow automation
- Integration with other tools

**Run it:**
```bash
chmod +x examples/cli/advanced_cli_usage.sh
./examples/cli/advanced_cli_usage.sh
```

### 5. Jupyter Notebook (`notebooks/market_analysis.ipynb`)

**What it covers:**
- Comprehensive market analysis
- Data visualization with matplotlib/seaborn
- Technical indicators (RSI, Bollinger Bands, moving averages)
- Statistical analysis and correlation
- Real-time data monitoring
- Cryptocurrency integration

**Run it:**
```bash
# Start Jupyter
jupyter notebook

# Open: examples/notebooks/market_analysis.ipynb
```

## 🛠️ Prerequisites

### For Python Examples
```bash
# Required
pip install alpaca-market-data

# Recommended for advanced examples
pip install pandas matplotlib seaborn jupyter
```

### For CLI Examples
```bash
# Install the package to get CLI tools
pip install -e .
```

### For Notebook Examples
```bash
# Install additional dependencies
pip install jupyter pandas matplotlib seaborn numpy

# Start notebook server
jupyter notebook
```

## 🔧 Setup Instructions

### 1. Environment Setup

Create a `.env` file in your project root:
```bash
# Copy from example
cp .env.example .env

# Edit with your credentials
ALPACA_API_KEY=your_api_key_here
ALPACA_API_SECRET=your_secret_key_here
```

### 2. Test Setup

Verify everything works:
```bash
# Test Python API
python -c "from alpaca_data import AlpacaClient; print('✅ API import works')"

# Test CLI tools
alpaca-bars --help
echo "✅ CLI tools work"
```

## 📊 Use Cases Covered

### Data Collection
- Historical OHLCV bars (1Min, 5Min, 1Hour, 1Day, etc.)
- Real-time quotes (bid/ask prices and sizes)
- Trade data (price, size, exchange)
- Market snapshots (comprehensive data)
- News articles (with content option)
- Cryptocurrency data (stocks and crypto)
- Options data (quotes, trades, snapshots, and Greeks)

### Data Analysis
- Price trend analysis
- Volatility calculations
- Technical indicators (SMA, RSI, Bollinger Bands)
- Correlation analysis
- Performance metrics

### Output Formats
- JSON (API responses)
- CSV (for spreadsheets)
- pandas DataFrames (for analysis)
- Pretty printed terminal output

### CLI Workflows
- Single and multiple symbol queries
- Different timeframes and date ranges
- Output format selection
- File saving and redirection
- Batch processing
- Real-time monitoring

## 🔍 Common Patterns

### Multiple Symbols
```python
# Python
symbols = ["AAPL", "GOOGL", "MSFT"]
result = client.get_bars(symbols=symbols, timeframe="1Day")

# CLI
alpaca-bars AAPL GOOGL MSFT --timeframe 1Day
```

### Date Ranges
```python
# Python
from datetime import datetime, timedelta

start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)
result = client.get_bars("AAPL", start=start.isoformat(), end=end.isoformat())

# CLI
alpaca-bars AAPL --start 2024-01-01 --end 2024-01-31
```

### Output Formats
```python
# Python
json_data = client.get_bars("AAPL", output_format="json")
df_data = client.get_bars("AAPL", output_format="dataframe")

# CLI
alpaca-bars AAPL --format json
alpaca-bars AAPL --format csv --output-file data.csv
```

### Error Handling
```python
# Python
try:
    result = client.get_bars("INVALID_SYMBOL")
except Exception as e:
    print(f"Error: {e}")

# CLI - commands will show helpful error messages
alpaca-bars INVALID_SYMBOL
```

## 💡 Best Practices

### 1. Rate Limiting
- Use batch requests when possible
- Respect API rate limits
- Consider `rate_limit_per_minute` parameter

### 2. Error Handling
- Always wrap API calls in try/catch blocks
- Validate symbols and parameters
- Handle empty results gracefully

### 3. Data Handling
- Use appropriate output formats for your use case
- Cache frequently accessed data
- Consider DataFrame for analysis work

### 4. CLI Usage
- Use `--help` to see all options
- Save output to files for analysis
- Combine CLI tools with other Unix commands

## 🔗 More Resources

- [Main README](../README.md) - Complete SDK documentation
- [API Reference](../README.md#api-reference) - Detailed method documentation
- [CLI Tools](../README.md#cli-tools) - Complete CLI reference
- [GitHub Repository](https://github.com/rmeyer1/alpaca-market-data)

## 🤝 Contributing

Found a bug? Have an improvement idea?

1. Fork the repository
2. Create an example or improve existing ones
3. Test your changes
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

**Happy coding!** 🚀