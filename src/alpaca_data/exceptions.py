"""Custom exceptions for Alpaca Market Data SDK."""


class AlpacaAPIError(Exception):
    """Base exception for Alpaca API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        """Initialize the error.

        Args:
            message: Error message.
            status_code: HTTP status code if applicable.
        """
        super().__init__(message)
        self.status_code = status_code


class AlpacaAuthError(AlpacaAPIError):
    """Raised when authentication fails (401 Unauthorized)."""

    pass


class AlpacaNotFoundError(AlpacaAPIError):
    """Raised when a resource is not found (404 Not Found)."""

    pass


class AlpacaValidationError(AlpacaAPIError):
    """Raised when request validation fails (422 Unprocessable Entity)."""

    pass


class AlpacaRateLimitError(AlpacaAPIError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""

    def __init__(self, message: str, retry_after: Optional[int] = None):
        """Initialize the rate limit error.

        Args:
            message: Error message.
            retry_after: Seconds to wait before retrying.
        """
        super().__init__(message, 429)
        self.retry_after = retry_after
