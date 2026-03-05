"""Rate limiter implementation using token bucket algorithm."""

import time
import threading
from typing import Optional, Tuple
from enum import Enum


class RateLimitStrategy(Enum):
    """Rate limiting strategies."""
    BLOCK = "block"  # Block until tokens available
    THROTTLE = "throttle"  # Raise exception immediately
    QUEUE = "queue"  # Queue requests for later processing


class RateLimiter:
    """Token bucket rate limiter for API requests.
    
    Implements the token bucket algorithm to control request rate.
    Ensures requests don't exceed specified rate limits.
    
    Args:
        rate_per_minute: Maximum requests per minute (default: 200 for Alpaca free tier)
        bucket_capacity: Maximum burst capacity (default: same as rate)
        strategy: How to handle when no tokens available
        max_retries: Maximum retry attempts for 429 responses
        retry_backoff: Backoff factor for retry delays
        
    Example:
        >>> limiter = RateLimiter(rate_per_minute=200)
        >>> with limiter.acquire():
        ...     # Make API request
        ...     pass
    """

    def __init__(
        self,
        rate_per_minute: int = 200,
        bucket_capacity: Optional[int] = None,
        strategy: RateLimitStrategy = RateLimitStrategy.BLOCK,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        """Initialize the rate limiter.
        
        Args:
            rate_per_minute: Requests allowed per minute
            bucket_capacity: Max burst capacity (defaults to rate_per_minute)
            strategy: How to handle token exhaustion
            max_retries: Max retry attempts
            retry_backoff: Exponential backoff multiplier
        """
        self.rate_per_minute = rate_per_minute
        self.bucket_capacity = bucket_capacity or rate_per_minute
        self.strategy = strategy
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        
        # Token bucket state
        self.tokens = float(self.bucket_capacity)
        self.last_refill = time.monotonic()
        self._lock = threading.Lock()
        
        # Calculate refill rate (tokens per second)
        self.refill_rate = rate_per_minute / 60.0

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time.
        
        Calculates how many tokens should be added to the bucket based on
        the time elapsed since the last refill and the refill rate.
        """
        now = time.monotonic()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add
        tokens_to_add = elapsed * self.refill_rate
        
        # Add tokens, but don't exceed capacity
        self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)
        self.last_refill = now

    def _wait_for_tokens(self, tokens_needed: float = 1.0) -> bool:
        """Wait until tokens are available.
        
        Args:
            tokens_needed: Number of tokens required
            
        Returns:
            True if tokens were acquired, False if timed out
        """
        while self.tokens < tokens_needed:
            # Calculate how long to wait for next token
            tokens_short = tokens_needed - self.tokens
            wait_time = tokens_short / self.refill_rate
            
            # Sleep for a short time and try again
            time.sleep(min(wait_time, 0.1))  # Max 100ms sleep
            
            # Refill tokens if needed
            self._refill_tokens()
            
        return True

    def acquire(self, tokens_needed: float = 1.0) -> "RateLimiterContext":
        """Acquire tokens for making a request.
        
        Args:
            tokens_needed: Number of tokens to acquire (default: 1)
            
        Returns:
            RateLimiterContext that can be used as a context manager
            
        Raises:
            RuntimeError: If strategy is THROTTLE and no tokens available
        """
        with self._lock:
            # Refill tokens based on elapsed time
            self._refill_tokens()
            
            # Check if we have enough tokens
            if self.tokens >= tokens_needed:
                # Consume tokens immediately
                self.tokens -= tokens_needed
                return RateLimiterContext(self, tokens_needed)
            
            # Handle different strategies when insufficient tokens
            if self.strategy == RateLimitStrategy.THROTTLE:
                raise RuntimeError(
                    f"Rate limit exceeded. {self.tokens:.1f} tokens available, "
                    f"{tokens_needed} needed."
                )
            
            elif self.strategy == RateLimitStrategy.BLOCK:
                # Wait for tokens to become available
                self._wait_for_tokens(tokens_needed)
                self.tokens -= tokens_needed
                return RateLimiterContext(self, tokens_needed)
            
            else:  # QUEUE strategy
                # For queue strategy, return context but don't consume tokens yet
                # In a real implementation, this would add to a queue
                return RateLimiterContext(self, tokens_needed, queued=True)

    def get_wait_time(self, tokens_needed: float = 1.0) -> float:
        """Calculate estimated wait time for tokens.
        
        Args:
            tokens_needed: Number of tokens needed
            
        Returns:
            Estimated seconds to wait for tokens, or 0 if available now
        """
        with self._lock:
            self._refill_tokens()
            
            if self.tokens >= tokens_needed:
                return 0.0
            
            # Calculate time needed to get enough tokens
            tokens_short = tokens_needed - self.tokens
            return tokens_short / self.refill_rate

    def get_available_tokens(self) -> float:
        """Get current number of available tokens.
        
        Returns:
            Number of tokens currently available
        """
        with self._lock:
            self._refill_tokens()
            return self.tokens

    def reset(self) -> None:
        """Reset the rate limiter to initial state.
        
        Fills the bucket to capacity and resets timing.
        """
        with self._lock:
            self.tokens = float(self.bucket_capacity)
            self.last_refill = time.monotonic()


class RateLimiterContext:
    """Context manager for rate-limited operations.
    
    Automatically handles token acquisition and release.
    """

    def __init__(
        self,
        limiter: RateLimiter,
        tokens_needed: float,
        queued: bool = False,
    ):
        """Initialize the context manager.
        
        Args:
            limiter: The RateLimiter instance
            tokens_needed: Number of tokens required
            queued: Whether this is a queued request
        """
        self.limiter = limiter
        self.tokens_needed = tokens_needed
        self.queued = queued
        self._acquired = False

    def __enter__(self) -> "RateLimiterContext":
        """Acquire tokens when entering context."""
        if not self.queued:
            # Tokens were already acquired in acquire() method
            self._acquired = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Release tokens when exiting context."""
        # In token bucket algorithm, tokens are "spent" on use
        # No explicit release needed since they're consumed
        pass

    def retry_after(self, delay: float) -> None:
        """Handle retry-after delay from 429 response.
        
        Args:
            delay: Seconds to wait before retrying
        """
        # For 429 responses, we need to wait for the specified time
        time.sleep(delay)