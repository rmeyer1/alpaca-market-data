"""Alpaca API Client implementation."""

import os
import requests
import time
from typing import Optional, Dict, Any, List, Union
from .rate_limiter import RateLimiter
from .exceptions import (
    AlpacaAPIError,
    AlpacaAuthError,
    AlpacaNotFoundError,
    AlpacaValidationError,
    AlpacaRateLimitError
)
from .formatters import OutputFormatter
from .formatters import OutputFormatter


class AlpacaClient:
    """HTTP client for Alpaca Market Data API.

    This class handles authentication, rate limiting, and HTTP requests
    to the Alpaca Market Data API.

    Args:
        api_key: Alpaca API key. If not provided, reads from ALPACA_API_KEY env var.
        secret_key: Alpaca secret key. If not provided, reads from ALPACA_API_SECRET env var.
        base_url: API base URL. Defaults to paper trading URL.

    Raises:
        ValueError: If API credentials are not provided or invalid.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
        rate_per_minute: int = 200,
    ):
        """Initialize the Alpaca client.

        Args:
            api_key: Alpaca API key. If not provided, reads from ALPACA_API_KEY env var.
            secret_key: Alpaca secret key. If not provided, reads from ALPACA_API_SECRET env var.
            base_url: API base URL. Defaults to paper trading URL.
            rate_per_minute: Maximum requests per minute (default: 200 for Alpaca free tier).
        """
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_API_SECRET")
        self.base_url = base_url or os.getenv(
            "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"
        )

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(rate_per_minute=rate_per_minute)

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "API credentials required. Provide api_key and secret_key "
                "or set ALPACA_API_KEY and ALPACA_API_SECRET environment variables."
            )

        # Ensure base_url ends without trailing slash for proper URL joining
        self.base_url = self.base_url.rstrip('/')

    def _get_headers(self) -> Dict[str, str]:
        """Generate authentication headers for API requests."""
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.secret_key,
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """Make authenticated HTTP request to the Alpaca API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., '/v2/bars')
            params: URL query parameters
            data: Request body data for POST/PUT requests

        Returns:
            requests.Response: The HTTP response object

        Raises:
            requests.HTTPError: For HTTP error status codes
            requests.ConnectionError: For network-related errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        # Apply rate limiting - acquire token before making request
        try:
            with self.rate_limiter.acquire():
                try:
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=headers,
                        params=params,
                        json=data,
                        timeout=30,
                    )
                    response.raise_for_status()
                    return response
                except requests.exceptions.HTTPError as e:
                    status_code = e.response.status_code

                    # Handle specific HTTP status codes with custom exceptions
                    if status_code == 401:
                        raise AlpacaAuthError(
                            "Invalid API credentials. Check your API key and secret.",
                            status_code
                        )
                    elif status_code == 404:
                        raise AlpacaNotFoundError(
                            f"Resource not found: {endpoint}",
                            status_code
                        )
                    elif status_code == 422:
                        error_data = e.response.json() if e.response.content else {}
                        message = error_data.get('message', 'Request validation failed')
                        raise AlpacaValidationError(message, status_code)
                    elif status_code == 429:
                        retry_after = int(e.response.headers.get('Retry-After', 60))
                        raise AlpacaRateLimitError(
                            f"Rate limit exceeded. Retry after {retry_after} seconds.",
                            retry_after
                        )
                    else:
                        # For other 4xx and 5xx errors
                        error_data = e.response.json() if e.response.content else {}
                        message = error_data.get('message', f'HTTP error {status_code}')
                        raise AlpacaAPIError(message, status_code)

                except requests.exceptions.ConnectionError as e:
                    raise AlpacaAPIError(f"Failed to connect to Alpaca API: {e}", None)

                except requests.exceptions.Timeout as e:
                    raise AlpacaAPIError(f"Request timed out: {e}", None)

                except requests.exceptions.RequestException as e:
                    raise AlpacaAPIError(f"Request failed: {e}", None)

        except RuntimeError as e:
            # Rate limiter threw an exception (THROTTLE strategy)
            raise AlpacaRateLimitError(str(e), retry_after=None)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint path
            params: URL query parameters

        Returns:
            requests.Response: The HTTP response object
        """
        return self._make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            requests.Response: The HTTP response object
        """
        return self._make_request("POST", endpoint, data=data)

    def test_connection(self) -> bool:
        """Test the connection to Alpaca API with current credentials.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to get account info to test credentials
            response = self.get("/v2/account")
            return response.status_code == 200
        except Exception:
            return False

    def get_bars(
        self,
        symbols: str | List[str],
        timeframe: str = "1Day",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        adjustment: str = "all",
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get historical OHLCV bars for one or more symbols.

        Args:
            symbols: Single symbol (str) or multiple symbols (list) to retrieve bars for
            timeframe: Bar timeframe (1Min, 5Min, 15Min, 1Hour, 1Day, 1Week, 1Month)
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of bars to return (max 1000, default 1000)
            adjustment: Split adjustment ('all', 'raw', 'splits_only', 'dividends_only')
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - bars: List of Bar objects
                - symbol: The symbol(s) requested
                - timeframe: The timeframe used
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of bars returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_bars("AAPL", timeframe="1Day", start="2024-01-01")
            >>> print(f"Got {len(result['bars'])} bars for {result['symbol']}")

            >>> # Multiple symbols
            >>> result = client.get_bars(["AAPL", "GOOGL"], timeframe="1Hour")
            >>> for bar in result['bars']:
            ...     print(f"{bar.symbol}: {bar.timestamp} {bar.close}")
        """
        from .models import Bar

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v2/stocks/{symbols}/bars"
            params = {
                "timeframe": timeframe,
                "limit": limit,
                "adjustment": adjustment,
                "sort": sort,
            }
        else:
            endpoint = "/v2/stocks/bars"
            params = {
                "symbols": ",".join(symbols),
                "timeframe": timeframe,
                "limit": limit,
                "adjustment": adjustment,
                "sort": sort,
            }

        # Add date range parameters if provided
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse bars from response
        bars = []
        bars_data = data.get("bars", [])

        if isinstance(symbols, str):
            # Single symbol response
            for bar_data in bars_data:
                bars.append(Bar.from_dict(symbols, bar_data))
        else:
            # Multi-symbol response - the API returns {symbol: [bars]}
            if isinstance(bars_data, dict):
                # New format: bars_data is a dict {symbol: [bar_data]}
                for symbol, symbol_bars in bars_data.items():
                    for bar_data in symbol_bars:
                        bars.append(Bar.from_dict(symbol, bar_data))
            else:
                # Old format: bars_data is a list of bar objects with symbol field
                for bar_data in bars_data:
                    if isinstance(bar_data, dict):
                        symbol = bar_data.get("S", bar_data.get("symbol", "UNKNOWN"))
                        # Remove symbol field from data for Bar.from_dict
                        bar_data_copy = bar_data.copy()
                        bar_data_copy.pop("S", None)
                        bar_data_copy.pop("symbol", None)
                        bars.append(Bar.from_dict(symbol, bar_data_copy))

        # Build response with metadata
        result = {
            "bars": bars,
            "symbol": symbols,
            "timeframe": timeframe,
            "next_page_token": data.get("next_page_token"),
            "count": len(bars),
        }

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        # Apply output formatting if requested
        if output_format.lower() != "dict":
            formatter = OutputFormatter()
            return formatter.format(result, output_format.lower())

        return self._apply_formatting(result, output_format)

    def get_quotes(
        self,
        symbols: str | List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        feed: str = "iex",
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest and historical NBBO quotes for one or more symbols.

        Args:
            symbols: Single symbol (str) or multiple symbols (list) to retrieve quotes for
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of quotes to return (max 1000, default 1000)
            feed: Data feed ('iex' for free tier, 'sip' for premium)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - quotes: List of Quote objects
                - symbol: The symbol(s) requested
                - feed: The data feed used
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of quotes returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_quotes("AAPL", limit=100)
            >>> print(f"Got {len(result['quotes'])} quotes for {result['symbol']}")

            >>> # With date range
            >>> result = client.get_quotes("AAPL", start="2024-01-01T09:30:00-05:00", end="2024-01-01T16:00:00-05:00")
        """
        from .models import Quote

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v2/stocks/{symbols}/quotes"
            params = {
                "limit": limit,
                "feed": feed,
                "sort": sort,
            }
        else:
            endpoint = "/v2/stocks/quotes"
            params = {
                "symbols": ",".join(symbols),
                "limit": limit,
                "feed": feed,
                "sort": sort,
            }

        # Add date range parameters if provided
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse quotes from response
        quotes = []
        quotes_data = data.get("quotes", [])

        if isinstance(symbols, str):
            # Single symbol response
            for quote_data in quotes_data:
                quotes.append(Quote.from_dict(symbols, quote_data))
        else:
            # Multi-symbol response - each quote includes symbol field
            for quote_data in quotes_data:
                symbol = quote_data.get("S", quote_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Quote.from_dict
                quote_data_copy = quote_data.copy()
                quote_data_copy.pop("S", None)
                quote_data_copy.pop("symbol", None)
                quotes.append(Quote.from_dict(symbol, quote_data_copy))

        # Build response with metadata
        result = {
            "quotes": quotes,
            "symbol": symbols,
            "feed": feed,
            "next_page_token": data.get("next_page_token"),
            "count": len(quotes),
        }

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        # Apply output formatting if requested
        return self._apply_formatting(result, output_format)

    def get_snapshot(
        self,
        symbols: str | List[str],
        feed: str = "iex",
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest market data snapshot for one or more symbols.

        Args:
            symbols: Single symbol (str) or multiple symbols (list) to retrieve snapshots for
            feed: Data feed ('iex' for free tier, 'sip' for premium)

        Returns:
            Dictionary containing:
                - snapshots: List of Snapshot objects
                - symbol: The symbol(s) requested
                - feed: The data feed used
                - count: Number of snapshots returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_snapshot("AAPL")
            >>> print(f"Got snapshot for {result['symbol']}: {result['snapshots'][0]}")

            >>> # Multiple symbols
            >>> result = client.get_snapshot(["AAPL", "GOOGL"])
            >>> for snapshot in result['snapshots']:
            ...     print(f"{snapshot.symbol}: Latest trade {snapshot.latest_trade.price}")
        """
        from .models import Snapshot

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v2/stocks/{symbols}/snapshot"
            params = {
                "feed": feed,
            }
        else:
            endpoint = "/v2/stocks/snapshots"
            params = {
                "symbols": ",".join(symbols),
                "feed": feed,
            }

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse snapshots from response
        snapshots = []

        if isinstance(symbols, str):
            # Single symbol response
            snapshot_data = data.get("snapshot", {})
            snapshots.append(Snapshot.from_dict(symbols, snapshot_data))
        else:
            # Multi-symbol response
            snapshots_data = data.get("snapshots", [])
            for snapshot_data in snapshots_data:
                symbol = snapshot_data.get("S", snapshot_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Snapshot.from_dict
                snapshot_data_copy = snapshot_data.copy()
                snapshot_data_copy.pop("S", None)
                snapshot_data_copy.pop("symbol", None)
                snapshots.append(Snapshot.from_dict(symbol, snapshot_data_copy))

        # Build response with metadata
        result = {
            "snapshots": snapshots,
            "symbol": symbols,
            "feed": feed,
            "count": len(snapshots),
        }

        return self._apply_formatting(result, output_format)

    def get_trades(
        self,
        symbols: str | List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        feed: str = "iex",
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get historical trades for one or more symbols.

        Args:
            symbols: Single symbol (str) or multiple symbols (list) to retrieve trades for
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of trades to return (max 1000, default 1000)
            feed: Data feed ('iex' for free tier, 'sip' for premium)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - trades: List of Trade objects
                - symbol: The symbol(s) requested
                - feed: The data feed used
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of trades returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_trades("AAPL", limit=100)
            >>> print(f"Got {len(result['trades'])} trades for {result['symbol']}")

            >>> # With date range
            >>> result = client.get_trades("AAPL", start="2024-01-01T09:30:00-05:00", end="2024-01-01T16:00:00-05:00")
            >>> for trade in result['trades']:
            ...     print(f"Trade: {trade.timestamp} {trade.price} @ {trade.size}")
        """
        from .models import Trade

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v2/stocks/{symbols}/trades"
            params = {
                "limit": limit,
                "feed": feed,
                "sort": sort,
            }
        else:
            endpoint = "/v2/stocks/trades"
            params = {
                "symbols": ",".join(symbols),
                "limit": limit,
                "feed": feed,
                "sort": sort,
            }

        # Add date range parameters if provided
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse trades from response
        trades = []
        trades_data = data.get("trades", [])

        if isinstance(symbols, str):
            # Single symbol response
            for trade_data in trades_data:
                trades.append(Trade.from_dict(symbols, trade_data))
        else:
            # Multi-symbol response - each trade includes symbol field
            for trade_data in trades_data:
                symbol = trade_data.get("S", trade_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Trade.from_dict
                trade_data_copy = trade_data.copy()
                trade_data_copy.pop("S", None)
                trade_data_copy.pop("symbol", None)
                trades.append(Trade.from_dict(symbol, trade_data_copy))

        # Build response with metadata
        result = {
            "trades": trades,
            "symbol": symbols,
            "feed": feed,
            "next_page_token": data.get("next_page_token"),
            "count": len(trades),
        }

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        return self._apply_formatting(result, output_format)

    def get_news(
        self,
        symbols: Optional[List[str]] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 50,
        include_content: bool = False,
        sort: str = "desc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get news articles for specified symbols and date range.

        Args:
            symbols: List of symbols to filter news by (optional)
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of articles to return (default 50)
            include_content: Whether to include full article content (default False)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored)

        Returns:
            Dictionary containing:
                - news: List of News objects
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of articles returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_news(symbols=["AAPL", "GOOGL"], limit=10)
            >>> print(f"Got {len(result['news'])} news articles")

            >>> # With date range
            >>> result = client.get_news(start="2024-01-01", end="2024-01-02", include_content=True)
            >>> for article in result['news']:
            ...     print(f"Headline: {article.headline}")
            ...     print(f"Source: {article.source}")
            ...     print(f"Related: {article.symbols}")
        """
        from .models import News

        # Build API endpoint and parameters
        endpoint = "/v1beta1/news"
        params = {
            "limit": limit,
            "include_content": include_content,
            "sort": sort,
        }

        # Add symbol filters
        if symbols:
            params["symbols"] = ",".join(symbols)

        # Add date range parameters if provided
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse news articles from response
        news_articles = []
        news_data = data.get("news", [])

        for article_data in news_data:
            news_articles.append(News.from_dict(article_data))

        # Build response with metadata
        result = {
            "news": news_articles,
            "next_page_token": data.get("next_page_token"),
            "count": len(news_articles),
        }

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        # Add filter info
        if symbols:
            result["symbols"] = symbols
        if start:
            result["start"] = start
        if end:
            result["end"] = end

        return self._apply_formatting(result, output_format)

    def get_crypto_bars(
        self,
        symbol_or_symbols: str | List[str],
        timeframe: str = "1Day",
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        exchange: Optional[str] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get historical OHLCV bars for crypto pairs (BTC/USD, ETH/USD, etc.).

        Args:
            symbol_or_symbols: Single crypto symbol (e.g., "BTC/USD") or list of symbols
            timeframe: Bar timeframe (1Min, 5Min, 15Min, 1Hour, 1Day, 1Week, 1Month)
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of bars to return (max 1000, default 1000)
            exchange: Exchange to filter by (e.g., "NYSE", "CBSE") (optional)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - bars: List of Bar objects
                - symbol: The crypto symbol(s) requested
                - timeframe: The timeframe used
                - exchange: Exchange filter applied (if any)
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of bars returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_crypto_bars("BTC/USD", timeframe="1Hour", limit=50)
            >>> print(f"Got {len(result['bars'])} bars for {result['symbol']}")

            >>> # Multiple crypto pairs
            >>> result = client.get_crypto_bars(["BTC/USD", "ETH/USD"], timeframe="1Day")
            >>> for bar in result['bars']:
            ...     print(f"{bar.symbol}: {bar.timestamp} ${bar.close}")
        """
        from .models import Bar

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbol_or_symbols, str):
            endpoint = f"/v1beta1/crypto/bars/{symbol_or_symbols}"
            params = {
                "timeframe": timeframe,
                "limit": limit,
                "sort": sort,
            }
        else:
            endpoint = "/v1beta1/crypto/bars"
            params = {
                "symbols": ",".join(symbol_or_symbols),
                "timeframe": timeframe,
                "limit": limit,
                "sort": sort,
            }

        # Add optional parameters
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if exchange:
            params["exchange"] = exchange
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse bars from response
        bars = []
        bars_data = data.get("bars", [])

        if isinstance(symbol_or_symbols, str):
            # Single symbol response
            for bar_data in bars_data:
                bars.append(Bar.from_dict(symbol_or_symbols, bar_data))
        else:
            # Multi-symbol response - each bar includes symbol field
            for bar_data in bars_data:
                symbol = bar_data.get("S", bar_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Bar.from_dict
                bar_data_copy = bar_data.copy()
                bar_data_copy.pop("S", None)
                bar_data_copy.pop("symbol", None)
                bars.append(Bar.from_dict(symbol, bar_data_copy))

        # Build response with metadata
        result = {
            "bars": bars,
            "symbol": symbol_or_symbols,
            "timeframe": timeframe,
            "next_page_token": data.get("next_page_token"),
            "count": len(bars),
        }

        # Add optional metadata
        if exchange:
            result["exchange"] = exchange

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        return self._apply_formatting(result, output_format)

    def get_crypto_quotes(
        self,
        symbol_or_symbols: str | List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        exchange: Optional[str] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest and historical quotes for crypto pairs (BTC/USD, ETH/USD, etc.).

        Args:
            symbol_or_symbols: Single crypto symbol (e.g., "BTC/USD") or list of symbols
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of quotes to return (max 1000, default 1000)
            exchange: Exchange to filter by (optional)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - quotes: List of Quote objects
                - symbol: The crypto symbol(s) requested
                - exchange: Exchange filter applied (if any)
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of quotes returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_crypto_quotes("BTC/USD", limit=50)
            >>> print(f"Got {len(result['quotes'])} quotes for {result['symbol']}")

            >>> # Multiple crypto pairs
            >>> result = client.get_crypto_quotes(["BTC/USD", "ETH/USD"], limit=100)
            >>> for quote in result['quotes']:
            ...     print(f"{quote.symbol}: Bid ${quote.bid_price}, Ask ${quote.ask_price}")
        """
        from .models import Quote

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbol_or_symbols, str):
            endpoint = f"/v1beta1/crypto/quotes/{symbol_or_symbols}"
            params = {
                "limit": limit,
                "sort": sort,
            }
        else:
            endpoint = "/v1beta1/crypto/quotes"
            params = {
                "symbols": ",".join(symbol_or_symbols),
                "limit": limit,
                "sort": sort,
            }

        # Add optional parameters
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if exchange:
            params["exchange"] = exchange
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse quotes from response
        quotes = []
        quotes_data = data.get("quotes", [])

        if isinstance(symbol_or_symbols, str):
            # Single symbol response
            for quote_data in quotes_data:
                quotes.append(Quote.from_dict(symbol_or_symbols, quote_data))
        else:
            # Multi-symbol response - each quote includes symbol field
            for quote_data in quotes_data:
                symbol = quote_data.get("S", quote_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Quote.from_dict
                quote_data_copy = quote_data.copy()
                quote_data_copy.pop("S", None)
                quote_data_copy.pop("symbol", None)
                quotes.append(Quote.from_dict(symbol, quote_data_copy))

        # Build response with metadata
        result = {
            "quotes": quotes,
            "symbol": symbol_or_symbols,
            "next_page_token": data.get("next_page_token"),
            "count": len(quotes),
        }

        # Add optional metadata
        if exchange:
            result["exchange"] = exchange

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        return self._apply_formatting(result, output_format)


    def get_crypto_trades(
        self,
        symbol_or_symbols: str | List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        exchange: Optional[str] = None,
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest and historical trades for crypto pairs (BTC/USD, ETH/USD, etc.).

        Args:
            symbol_or_symbols: Single crypto symbol (e.g., "BTC/USD") or list of symbols
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of trades to return (max 1000, default 1000)
            exchange: Exchange to filter by (optional)
            sort: Sort order ("asc" for ascending, "desc" for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - trades: List of Trade objects
                - symbol: The crypto symbol(s) requested
                - exchange: Exchange filter applied (if any)
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of trades returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_crypto_trades("BTC/USD", limit=50)
            >>> print(f"Got {len(result["trades"])} trades for {result["symbol"]}")

            >>> # Multiple crypto pairs
            >>> result = client.get_crypto_trades(["BTC/USD", "ETH/USD"], limit=100)
            >>> for trade in result["trades"]:
            ...     print(f"{trade.symbol}: {trade.size} @ ${trade.price}")
        """
        from .models import Trade

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbol_or_symbols, str):
            endpoint = f"/v1beta1/crypto/trades/{symbol_or_symbols}"
            params = {
                "limit": limit,
                "sort": sort,
            }
        else:
            endpoint = "/v1beta1/crypto/trades"
            params = {
                "symbols": ",".join(symbol_or_symbols),
                "limit": limit,
                "sort": sort,
            }

        # Add optional parameters
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if exchange:
            params["exchange"] = exchange
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse trades from response
        trades = []
        trades_data = data.get("trades", [])

        if isinstance(symbol_or_symbols, str):
            # Single symbol response
            for trade_data in trades_data:
                trades.append(Trade.from_dict(symbol_or_symbols, trade_data))
        else:
            # Multi-symbol response - each trade includes symbol field
            for trade_data in trades_data:
                symbol = trade_data.get("S", trade_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Trade.from_dict
                trade_data_copy = trade_data.copy()
                trade_data_copy.pop("S", None)
                trade_data_copy.pop("symbol", None)
                trades.append(Trade.from_dict(symbol, trade_data_copy))

        # Build response with metadata
        result = {
            "trades": trades,
            "symbol": symbol_or_symbols,
            "next_page_token": data.get("next_page_token"),
            "count": len(trades),
        }

        # Add optional metadata
        if exchange:
            result["exchange"] = exchange

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        return self._apply_formatting(result, output_format)

    def get_crypto_snapshot(
        self,
        symbol_or_symbols: str | List[str],
        exchange: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest market data snapshot for crypto pairs (BTC/USD, ETH/USD, etc.).

        Args:
            symbol_or_symbols: Single crypto symbol (e.g., "BTC/USD") or list of symbols
            exchange: Exchange to filter by (optional)

        Returns:
            Dictionary containing:
                - snapshots: List of Snapshot objects
                - symbol: The crypto symbol(s) requested
                - exchange: Exchange filter applied (if any)
                - count: Number of snapshots returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_crypto_snapshot("BTC/USD")
            >>> print(f"Got snapshot for {result["symbol"]}: {result["snapshots"][0]}")

            >>> # Multiple crypto pairs
            >>> result = client.get_crypto_snapshot(["BTC/USD", "ETH/USD"])
            >>> for snapshot in result["snapshots"]:
            ...     print(f"{snapshot.symbol}: Latest trade ${snapshot.latest_trade.price}")
        """
        from .models import Snapshot

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbol_or_symbols, str):
            endpoint = f"/v1beta1/crypto/snapshots/{symbol_or_symbols}"
            params = {}
        else:
            endpoint = "/v1beta1/crypto/snapshots"
            params = {
                "symbols": ",".join(symbol_or_symbols),
            }

        # Add optional parameters
        if exchange:
            params["exchange"] = exchange

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse snapshots from response
        snapshots = []

        if isinstance(symbol_or_symbols, str):
            # Single symbol response
            snapshot_data = data.get("snapshot", {})
            snapshots.append(Snapshot.from_dict(symbol_or_symbols, snapshot_data))
        else:
            # Multi-symbol response
            snapshots_data = data.get("snapshots", [])
            for snapshot_data in snapshots_data:
                symbol = snapshot_data.get("S", snapshot_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for Snapshot.from_dict
                snapshot_data_copy = snapshot_data.copy()
                snapshot_data_copy.pop("S", None)
                snapshot_data_copy.pop("symbol", None)
                snapshots.append(Snapshot.from_dict(symbol, snapshot_data_copy))

        # Build response with metadata
        result = {
            "snapshots": snapshots,
            "symbol": symbol_or_symbols,
            "count": len(snapshots),
        }

        # Add optional metadata
        if exchange:
            result["exchange"] = exchange

        return self._apply_formatting(result, output_format)

    def get_option_quotes(
        self,
        symbols: str | List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest and historical quotes for options symbols.

        Args:
            symbols: Single option symbol (str) or multiple option symbols (list)
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of quotes to return (max 1000, default 1000)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - quotes: List of OptionQuote objects
                - symbol: The option symbol(s) requested
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of quotes returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_option_quotes("AAPL220121C00150000", limit=100)
            >>> print(f"Got {len(result['quotes'])} option quotes")
            >>> for quote in result['quotes']:
            ...     print(f"{quote.symbol}: Bid ${quote.bid_price}, Ask ${quote.ask_price}")
            ...     if quote.greeks:
            ...         print(f"  Delta: {quote.greeks.delta:.3f}, IV: {quote.iv}")
        """
        from .models import OptionQuote

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v1beta1/options/quotes/{symbols}"
            params = {
                "limit": limit,
                "sort": sort,
            }
        else:
            endpoint = "/v1beta1/options/quotes"
            params = {
                "symbols": ",".join(symbols),
                "limit": limit,
                "sort": sort,
            }

        # Add date range parameters if provided
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse option quotes from response
        quotes = []
        quotes_data = data.get("quotes", [])

        if isinstance(symbols, str):
            # Single symbol response
            for quote_data in quotes_data:
                quotes.append(OptionQuote.from_dict(symbols, quote_data))
        else:
            # Multi-symbol response - each quote includes symbol field
            for quote_data in quotes_data:
                symbol = quote_data.get("S", quote_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for OptionQuote.from_dict
                quote_data_copy = quote_data.copy()
                quote_data_copy.pop("S", None)
                quote_data_copy.pop("symbol", None)
                quotes.append(OptionQuote.from_dict(symbol, quote_data_copy))

        # Build response with metadata
        result = {
            "quotes": quotes,
            "symbol": symbols,
            "next_page_token": data.get("next_page_token"),
            "count": len(quotes),
        }

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        return self._apply_formatting(result, output_format)

    def get_option_trades(
        self,
        symbols: str | List[str],
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 1000,
        sort: str = "asc",
        page_token: Optional[str] = None,
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest and historical trades for options symbols.

        Args:
            symbols: Single option symbol (str) or multiple option symbols (list)
            start: Start date/time in ISO format (e.g., "2024-01-01T09:30:00-05:00")
            end: End date/time in ISO format
            limit: Maximum number of trades to return (max 1000, default 1000)
            sort: Sort order ('asc' for ascending, 'desc' for descending)
            page_token: Pagination token for next page (if provided, other params ignored except symbols)

        Returns:
            Dictionary containing:
                - trades: List of OptionTrade objects
                - symbol: The option symbol(s) requested
                - next_page_token: Token for next page (None if no more pages)
                - count: Number of trades returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_option_trades("AAPL220121C00150000", limit=100)
            >>> print(f"Got {len(result['trades'])} option trades")
            >>> for trade in result['trades']:
            ...     print(f"{trade.symbol}: {trade.size} @ ${trade.price}")
            ...     if trade.greeks:
            ...         print(f"  Greeks: Δ={trade.greeks.delta:.3f}, Γ={trade.greeks.gamma:.4f}")
        """
        from .models import OptionTrade

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v1beta1/options/trades/{symbols}"
            params = {
                "limit": limit,
                "sort": sort,
            }
        else:
            endpoint = "/v1beta1/options/trades"
            params = {
                "symbols": ",".join(symbols),
                "limit": limit,
                "sort": sort,
            }

        # Add date range parameters if provided
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if page_token:
            params["page_token"] = page_token

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse option trades from response
        trades = []
        trades_data = data.get("trades", [])

        if isinstance(symbols, str):
            # Single symbol response
            for trade_data in trades_data:
                trades.append(OptionTrade.from_dict(symbols, trade_data))
        else:
            # Multi-symbol response - each trade includes symbol field
            for trade_data in trades_data:
                symbol = trade_data.get("S", trade_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for OptionTrade.from_dict
                trade_data_copy = trade_data.copy()
                trade_data_copy.pop("S", None)
                trade_data_copy.pop("symbol", None)
                trades.append(OptionTrade.from_dict(symbol, trade_data_copy))

        # Build response with metadata
        result = {
            "trades": trades,
            "symbol": symbols,
            "next_page_token": data.get("next_page_token"),
            "count": len(trades),
        }

        # Add pagination info if present
        if data.get("next_page_token"):
            result["has_next_page"] = True
            result["next_page_token"] = data["next_page_token"]
        else:
            result["has_next_page"] = False

        return self._apply_formatting(result, output_format)

    def get_option_snapshot(
        self,
        symbols: str | List[str],
        output_format: str = "dict",
    ) -> Union[Dict[str, Any], str]:
        """Get latest market data snapshot for options symbols including greeks.

        Args:
            symbols: Single option symbol (str) or multiple option symbols (list)

        Returns:
            Dictionary containing:
                - snapshots: List of OptionSnapshot objects
                - symbol: The option symbol(s) requested
                - count: Number of snapshots returned

        Example:
            >>> client = AlpacaClient()
            >>> result = client.get_option_snapshot("AAPL220121C00150000")
            >>> print(f"Got snapshot for {result['symbol']}")
            >>> snapshot = result['snapshots'][0]
            >>> print(f"Latest trade: ${snapshot.latest_trade.price} with delta: {snapshot.greeks.delta:.3f}")
            >>> print(f"Open interest: {snapshot.open_interest}, IV: {snapshot.iv}")

            >>> # Multiple option symbols
            >>> result = client.get_option_snapshot(["AAPL220121C00150000", "AAPL220121P00150000"])
            >>> for snapshot in result['snapshots']:
            ...     option_type = "CALL" if "C" in snapshot.symbol else "PUT"
            ...     print(f"{snapshot.symbol} ({option_type}): ${snapshot.latest_quote.bid_price} - ${snapshot.latest_quote.ask_price}")
        """
        from .models import OptionSnapshot

        # Determine API endpoint based on single or multiple symbols
        if isinstance(symbols, str):
            endpoint = f"/v1beta1/options/snapshots/{symbols}"
            params = {}
        else:
            endpoint = "/v1beta1/options/snapshots"
            params = {
                "symbols": ",".join(symbols),
            }

        # Make the API request
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()

        # Parse option snapshots from response
        snapshots = []

        if isinstance(symbols, str):
            # Single symbol response
            snapshot_data = data.get("snapshot", {})
            snapshots.append(OptionSnapshot.from_dict(symbols, snapshot_data))
        else:
            # Multi-symbol response
            snapshots_data = data.get("snapshots", [])
            for snapshot_data in snapshots_data:
                symbol = snapshot_data.get("S", snapshot_data.get("symbol", "UNKNOWN"))
                # Remove symbol field from data for OptionSnapshot.from_dict
                snapshot_data_copy = snapshot_data.copy()
                snapshot_data_copy.pop("S", None)
                snapshot_data_copy.pop("symbol", None)
                snapshots.append(OptionSnapshot.from_dict(symbol, snapshot_data_copy))

        # Build response with metadata
        result = {
            "snapshots": snapshots,
            "symbol": symbols,
            "count": len(snapshots),
        }

        return self._apply_formatting(result, output_format)

    def _apply_formatting(
        self,
        data: Dict[str, Any],
        output_format: str,
        filename: Optional[str] = None
    ) -> Union[Dict[str, Any], str]:
        """Apply output formatting to API response data.

        Args:
            data: API response data
            output_format: Output format ('dict', 'json', 'csv', 'dataframe')
            filename: Optional filename for CSV output

        Returns:
            Formatted data (dict, string, or DataFrame)
        """
        if output_format.lower() == "dict":
            return data

        formatter = OutputFormatter()
        return formatter.format(data, output_format.lower(), filename=filename)
