"""Alpaca API Client implementation."""

import os
from typing import Optional


class AlpacaClient:
    """HTTP client for Alpaca Market Data API.

    This class handles authentication, rate limiting, and HTTP requests
to the Alpaca Market Data API.

    Args:
        api_key: Alpaca API key. If not provided, reads from ALPACA_API_KEY env var.
        secret_key: Alpaca secret key. If not provided, reads from ALPACA_SECRET_KEY env var.
        base_url: API base URL. Defaults to paper trading URL.

    Raises:
        AlpacaAuthError: If API credentials are not provided or invalid.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize the Alpaca client."""
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.base_url = base_url or os.getenv(
            "ALPACA_BASE_URL", "https://paper-api.alpaca.markets"
        )

        if not self.api_key or not self.secret_key:
            raise ValueError(
                "API credentials required. Provide api_key and secret_key "
                "or set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables."
            )
