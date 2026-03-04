# Product Requirement Document: Alpaca Market Data Python SDK

## 1. Problem Statement

Agents need a reliable, consistent interface to Alpaca Market Data API without handling low-level HTTP requests, authentication, rate limiting, and data parsing manually. The current barrier to entry requires understanding REST API patterns, pagination, and Alpaca-specific quirks.

## 2. Goals

- **Single-command data retrieval**: One function call to get any market data type
- **Consistent return format**: JSON, CSV, or Pandas DataFrame based on preference
- **Automatic pagination**: Handle large datasets without manual page token management
- **Built-in rate limiting**: Respect Alpaca's limits without user intervention
- **Environment-based configuration**: Simple .env file setup
- **CLI + Library dual interface**: Usable as Python library or command-line scripts

## 3. Non-Goals

- Trading functionality (orders, positions, account management) - **Out of scope**
- Real-time WebSocket streaming - **Future version**
- Data persistence/storage layer - **Return data only**
- Historical options data - **Alpaca limitation**

## 4. Target Users

- Research agents running quantitative analysis
- Data scientists synthesizing market information  
- Automated research workflows
- CLI users who need quick market data exports

## 5. Core Workflows

### Workflow 1: Get Historical Bars (OHLCV)
```python
# As Python library
from alpaca_market_data import get_bars
df = get_bars(['AAPL', 'MSFT'], timeframe='1Day', start='2024-01-01', end='2024-01-31')

# As CLI
python get_bars.py AAPL,MSFT --timeframe 1Day --start 2024-01-01 --output csv
```

### Workflow 2: Get Real-time Quotes
```python
from alpaca_market_data import get_quotes
quotes = get_quotes(['AAPL', 'TSLA'])
```

### Workflow 3: Get Latest News with Sentiment
```python
from alpaca_market_data import get_news
news = get_news(['AAPL', 'MSFT'], limit=50, include_content=True)
```

## 6. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Support all Stock Market Data endpoints | P0 |
| FR-2 | Support all Crypto Market Data endpoints | P0 |
| FR-3 | Accept single ticker or list of tickers | P0 |
| FR-4 | Return data as dict, JSON, CSV, or DataFrame | P0 |
| FR-5 | Handle rate limiting with exponential backoff | P0 |
| FR-6 | Validate inputs before API calls | P0 |
| FR-7 | Support date range queries for historical data | P0 |
| FR-8 | CLI scripts for all data types | P0 |
| FR-9 | Virtual environment setup (requirements.txt) | P0 |
| FR-10 | Comprehensive error messages | P1 |

## 7. API Endpoints to Support

### Stock Market Data
| Endpoint | Purpose | Priority |
|----------|---------|----------|
| GET /v2/stocks/{symbol}/quotes/latest | Latest NBBO quote | P0 |
| GET /v2/stocks/{symbol}/quotes | Historical quotes | P1 |
| GET /v2/stocks/{symbol}/bars | Historical OHLCV bars | P0 |
| GET /v2/stocks/{symbol}/bars/latest | Latest bar | P0 |
| GET /v2/stocks/{symbol}/trades | Historical trades | P1 |
| GET /v2/stocks/{symbol}/trades/latest | Latest trade | P1 |
| GET /v2/stocks/{symbol}/snapshot | Current market state | P0 |
| GET /v2/stocks/{symbol}/news | News articles | P0 |
| GET /v2/stocks/snapshots | Multiple snapshots | P0 |

### Crypto Market Data
| Endpoint | Purpose | Priority |
|----------|---------|----------|
| GET /v2/crypto/{symbol}/quotes/latest | Latest crypto quote | P0 |
| GET /v2/crypto/{symbol}/quotes | Historical quotes | P1 |
| GET /v2/crypto/{symbol}/bars | Historical bars | P0 |
| GET /v2/crypto/{symbol}/bars/latest | Latest bar | P0 |
| GET /v2/crypto/{symbol}/trades | Historical trades | P1 |
| GET /v2/crypto/{symbol}/trades/latest | Latest trade | P1 |
| GET /v2/crypto/{symbol}/snapshot | Current crypto state | P0 |
| GET /v2/crypto/snapshots | Multiple snapshots | P0 |

## 8. Data Models

### Stock Bar (OHLCV)
```json
{
  "t": "2024-01-15T09:30:00Z",  // timestamp
  "o": 185.50,                    // open
  "h": 187.20,                    // high
  "l": 185.10,                    // low
  "c": 186.80,                    // close
  "v": 1250000,                   // volume
  "n": 4520,                      // trade count
  "vw": 186.45                    // volume weighted average price
}
```

### Quote
```json
{
  "t": "2024-01-15T09:30:00Z",
  "ax": "V",                      // ask exchange
  "ap": 186.85,                   // ask price
  "as": 100,                      // ask size
  "bx": "V",                      // bid exchange
  "bp": 186.75,                   // bid price
  "bs": 200,                      // bid size
  "c": ["R"]                      // conditions
}
```

### News Article
```json
{
  "id": 123456789,
  "headline": "Apple announces...",
  "author": "Reuters",
  "created_at": "2024-01-15T09:30:00Z",
  "updated_at": "2024-01-15T09:30:00Z",
  "summary": "...",
  "content": "...",                 // optional
  "url": "https://...",
  "images": [...],
  "symbols": ["AAPL"],
  "source": "businesswire.com",
  "tags": ["earnings", "technology"]
}
```

## 9. Configuration

### Environment Variables (.env)
```bash
# Required
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here

# Optional (defaults shown)
ALPACA_BASE_URL=https://data.alpaca.markets  # use paper for testing
ALPACA_DATA_FEED=iex  # or sip (subscription required)
```

## 10. Rate Limiting

### Limits
- Free tier: 200 requests/minute
- Paid tier: 200 requests/minute (can be increased)

### Implementation
- Token bucket algorithm
- Automatic retry with exponential backoff
- Respect `Retry-After` header on 429 responses
- Configurable max retries (default: 3)

## 11. Error Handling

| Error Code | Behavior | User Message |
|------------|----------|--------------|
| 401 | Invalid API credentials | "Authentication failed. Check your API keys." |
| 403 | Forbidden (wrong endpoint tier) | "Your subscription doesn't include this data." |
| 404 | Invalid symbol | "Symbol not found: {symbol}" |
| 422 | Invalid parameters | Detailed validation error |
| 429 | Rate limited | Wait and retry automatically |
| 500+ | Server error | Retry with backoff, then fail |

## 12. CLI Interface

### Common Arguments (all scripts)
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| symbols | str | required | Comma-separated ticker(s) |
| --output | str | json | json, csv, or dataframe |
| --filepath | str | None | Save to file path |
| --pretty | bool | False | Pretty print JSON |

### Script-Specific Arguments

**get_bars.py**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| --timeframe | str | 1Day | 1Min, 5Min, 15Min, 1Hour, 1Day |
| --start | str | None | Start date (YYYY-MM-DD) |
| --end | str | None | End date (YYYY-MM-DD) |
| --days | int | None | Days back (alternative to start) |
| --adjust | str | raw | raw, split, or all |
| --feed | str | iex | iex or sip |

**get_quotes.py**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| --latest | bool | False | Get only latest quote |
| --start | str | None | Historical start |
| --end | str | None | Historical end |

**get_news.py**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| --limit | int | 50 | Max articles (1-1000) |
| --start | str | None | Start date |
| --end | str | None | End date |
| --include-content | bool | False | Include full article |
| --sort | str | desc | desc or asc |

## 13. Usage Examples

### Python Library
```python
from alpaca_market_data import get_bars, get_quotes, get_news, get_snapshot

# Get daily bars for multiple stocks
bars = get_bars(
    symbols=['AAPL', 'MSFT', 'GOOGL'],
    timeframe='1Day',
    start='2024-01-01',
    end='2024-03-01'
)
# Returns: Pandas DataFrame

# Get latest quotes
quotes = get_quotes(['AAPL', 'TSLA'])

# Get news with sentiment
news = get_news('AAPL', limit=10, include_content=True)

# Get full market snapshot
snapshot = get_snapshot('AAPL')
```

### Command Line
```bash
# Setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# Get daily bars
python scripts/get_bars.py AAPL --timeframe 1Day --days 30 --output csv

# Get latest quotes for multiple stocks
python scripts/get_quotes.py AAPL,MSFT,TSLA --output json --pretty

# Get news
python scripts/get_news.py AAPL,MSFT --limit 20 --include-content --output csv

# Get snapshot
python scripts/get_snapshot.py SPY

# Get crypto data
python scripts/get_crypto_bars.py BTC/USD --timeframe 1Hour --days 7
```

## 14. Acceptance Criteria

- [ ] AC-1: `pip install -r requirements.txt` installs all dependencies
- [ ] AC-2: `.env` file configuration works for both paper and live environments
- [ ] AC-3: `get_bars()` returns valid OHLCV data for single ticker
- [ ] AC-4: `get_bars()` returns valid data for multiple tickers
- [ ] AC-5: All scripts support `--output csv` for data analysis workflows
- [ ] AC-6: Rate limits handled automatically without user intervention
- [ ] AC-7: Clear error messages for invalid tickers or date ranges
- [ ] AC-8: Documentation includes all supported endpoints
- [ ] AC-9: CLI help (`--help`) works for all scripts
- [ ] AC-10: Pagination handled automatically for requests > 10,000 records
- [ ] AC-11: All endpoints return consistent data structures
- [ ] AC-12: Crypto endpoints work with standard pairs (BTC/USD, ETH/USD)

## 15. Future Enhancements

- WebSocket streaming support for real-time data
- Options market data (when available from Alpaca)
- Caching layer for frequently requested data
- Async/await support for concurrent requests
- Data validation and cleaning utilities
