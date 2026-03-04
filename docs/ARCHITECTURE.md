# Architecture Specification: Alpaca Market Data SDK

## 1. System Overview

The Alpaca Market Data SDK is a Python library and CLI toolkit that provides convenient access to Alpaca's Market Data API. It abstracts HTTP requests, authentication, rate limiting, and data parsing into a simple, consistent interface.

### System Context

```
User Workflows:
  - Research Agent (Python Library)
  - Data Analyst (CLI Scripts)  
  - Automation (Scheduled Jobs)

Alpaca Market Data SDK:
  - AlpacaClient (Core HTTP Client)
  - Stock Data Endpoints
  - Crypto Data Endpoints
  - Rate Limiter
  - Auth Handler
  - Response Parser
  - Data Formatter

Alpaca Markets:
  - Market Data API (https://data.alpaca.markets)
```

## 2. Package Structure

```
alpaca-market-data/
├── README.md                      # Project overview
├── requirements.txt               # Dependencies
├── setup.py                       # Package setup
├── .env.example                   # Environment template
├── .gitignore
│
├── src/
│   └── alpaca_market_data/        # Main package
│       ├── __init__.py            # Exports
│       ├── client.py              # HTTP client
│       ├── stocks.py              # Stock endpoints
│       ├── crypto.py              # Crypto endpoints
│       ├── models.py              # Data models
│       ├── rate_limiter.py        # Rate limiting
│       ├── formatters.py          # Output formatters
│       ├── parser.py              # Response parsers
│       ├── exceptions.py          # Custom exceptions
│       └── utils.py               # Utilities
│
├── scripts/                       # CLI scripts
│   ├── get_bars.py
│   ├── get_quotes.py
│   ├── get_trades.py
│   ├── get_snapshots.py
│   ├── get_news.py
│   ├── get_crypto_bars.py
│   └── common.py
│
├── tests/                         # Test suite
│   ├── test_client.py
│   ├── test_stocks.py
│   └── conftest.py
│
└── docs/                          # Documentation
    ├── BRD.md
    ├── PRD.md
    ├── ARCHITECTURE.md
    └── examples/
```

## 3. Core Components

### 3.1 AlpacaClient

```python
class AlpacaClient:
    """Core HTTP client for Alpaca Market Data API."""
    
    def __init__(
        self,
        api_key: str = None,
        secret_key: str = None,
        base_url: str = "https://data.alpaca.markets",
        max_retries: int = 3,
        rate_limit: int = 200
    ):
        ...
    
    def request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """Make authenticated API request with rate limiting."""
        ...
```

### 3.2 Data Functions

```python
# stocks.py

def get_bars(
    symbols: Union[str, List[str]],
    timeframe: str = "1Day",
    start: str = None,
    end: str = None,
    limit: int = 1000,
    as_dataframe: bool = True
) -> Union[pd.DataFrame, List[Bar]]:
    """Get historical OHLCV bars."""
    ...

def get_quotes(symbols, start=None, end=None, ...) -> DataFrame:
    """Get quotes."""
    ...

def get_news(symbols, limit=50, ...) -> DataFrame:
    """Get news articles."""
    ...

def get_snapshot(symbol, ...) -> Snapshot:
    """Get market snapshot."""
    ...
```

### 3.3 Data Models

```python
@dataclass
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

@dataclass
class Quote:
    symbol: str
    timestamp: datetime
    ask_price: float
    ask_size: int
    bid_price: float
    bid_size: int

@dataclass
class NewsArticle:
    id: int
    headline: str
    author: str
    summary: str
    symbols: List[str]
```

## 4. Configuration

### Environment Variables (.env)

```bash
# Required
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here

# Optional
ALPACA_BASE_URL=https://data.alpaca.markets
ALPACA_DATA_FEED=iex
ALPACA_MAX_RETRIES=3
ALPACA_RATE_LIMIT=200
```

### Config Class

```python
class Config:
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    BASE_URL = os.getenv("ALPACA_BASE_URL", "https://data.alpaca.markets")
    
    @classmethod
    def validate(cls):
        if not cls.API_KEY or not cls.SECRET_KEY:
            raise ValueError("API keys required")
```

## 5. Rate Limiting

Token bucket algorithm:
- Capacity: 200 tokens
- Refill rate: 200/minute
- Automatic retry with exponential backoff

```python
class TokenBucket:
    def __init__(self, capacity=200, refill_rate=200/60):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
    
    def consume(self, tokens=1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

## 6. Authentication

```python
def get_auth_headers(api_key: str, secret_key: str) -> dict:
    return {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
        "Accept": "application/json"
    }
```

## 7. CLI Design

### Common Arguments

```python
def setup_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("symbols", help="Comma-separated tickers")
    parser.add_argument("--output", choices=["json", "csv"], default="json")
    parser.add_argument("--filepath", help="Save to file")
    parser.add_argument("--pretty", action="store_true")
    return parser
```

### Example: get_bars.py

```python
#!/usr/bin/env python3
"""Get historical OHLCV bars."""

from alpaca_market_data import get_bars
from common import setup_parser, output_data

def main():
    parser = setup_parser("Get historical bars")
    parser.add_argument("--timeframe", default="1Day")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", help="End date (YYYY-MM-DD)")
    parser.add_argument("--days", type=int, help="Days back")
    
    args = parser.parse_args()
    
    symbols = [s.strip() for s in args.symbols.split(",")]
    data = get_bars(symbols, timeframe=args.timeframe, ...)
    
    output_data(data, args)

if __name__ == "__main__":
    main()
```

## 8. Dependencies

### requirements.txt

```
requests>=2.28.0
python-dotenv>=1.0.0
pandas>=1.5.0
pytest>=7.0.0
```

## 9. Usage Examples

### Python Library

```python
from alpaca_market_data import get_bars, get_quotes, get_news

# Get bars
bars = get_bars(['AAPL', 'MSFT'], timeframe='1Day', start='2024-01-01')

# Get quotes
quotes = get_quotes(['AAPL', 'TSLA'])

# Get news
news = get_news('AAPL', limit=20, include_content=True)
```

### CLI

```bash
# Get daily bars
python scripts/get_bars.py AAPL,MSFT --timeframe 1Day --days 30 --output csv

# Get latest quotes
python scripts/get_quotes.py AAPL,TSLA --output json --pretty

# Get news
python scripts/get_news.py AAPL --limit 20 --output csv
```
