"""Alpaca API Client implementation."""

import os
import requests
import time
from typing import Optional, Dict, Any
from .rate_limiter import RateLimiter
from .exceptions import AlpacaRateLimitError


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
                    # Handle 429 (rate limit exceeded) with retry logic
                    if e.response.status_code == 429:
                        retry_after = int(e.response.headers.get('Retry-After', 60))
                        # Wait for the specified retry-after period
                        time.sleep(retry_after)
                        
                        # Retry the request once after waiting
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
                    
                    # Handle other HTTP errors
                    elif e.response.status_code == 401:
                        raise ValueError("Invalid API credentials. Check your API key and secret.")
                    else:
                        raise
                        
                except requests.exceptions.RequestException as e:
                    raise ConnectionError(f"Failed to connect to Alpaca API: {e}")
                    
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
