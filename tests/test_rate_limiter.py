"""Tests for RateLimiter."""

import time
import pytest
from alpaca_data.rate_limiter import RateLimiter, RateLimitStrategy


class TestRateLimiter:
    """Test cases for RateLimiter."""

    def test_rate_limiter_initialization(self):
        """Test RateLimiter can be initialized with default values."""
        limiter = RateLimiter()
        
        assert limiter.rate_per_minute == 200
        assert limiter.bucket_capacity == 200
        assert limiter.strategy == RateLimitStrategy.BLOCK
        assert limiter.tokens == 200.0
        assert limiter.refill_rate == 200 / 60.0

    def test_rate_limiter_custom_configuration(self):
        """Test RateLimiter can be configured with custom values."""
        limiter = RateLimiter(
            rate_per_minute=100,
            bucket_capacity=50,
            strategy=RateLimitStrategy.THROTTLE,
            max_retries=5,
            retry_backoff=2.0,
        )
        
        assert limiter.rate_per_minute == 100
        assert limiter.bucket_capacity == 50
        assert limiter.strategy == RateLimitStrategy.THROTTLE
        assert limiter.max_retries == 5
        assert limiter.retry_backoff == 2.0

    def test_rate_limiter_bucket_capacity_defaults_to_rate(self):
        """Test bucket capacity defaults to rate_per_minute when not specified."""
        limiter = RateLimiter(rate_per_minute=150)
        
        assert limiter.bucket_capacity == 150

    def test_acquire_token_success(self):
        """Test acquiring a token when available."""
        limiter = RateLimiter(rate_per_minute=200)
        
        initial_tokens = limiter.get_available_tokens()
        
        # Acquire a token
        with limiter.acquire() as ctx:
            assert ctx is not None
            # Tokens should decrease by 1 (allow for floating point precision)
            available_after = limiter.get_available_tokens()
            assert abs(available_after - (initial_tokens - 1)) < 0.001

    def test_acquire_multiple_tokens(self):
        """Test acquiring multiple tokens."""
        limiter = RateLimiter(rate_per_minute=10, bucket_capacity=10)
        
        # Acquire multiple tokens
        with limiter.acquire(tokens_needed=3) as ctx:
            assert ctx is not None
        
        # Should have used 3 tokens
        available = limiter.get_available_tokens()
        assert abs(available - 7.0) < 0.001

    def test_block_strategy_when_no_tokens(self):
        """Test BLOCK strategy waits when no tokens available."""
        limiter = RateLimiter(rate_per_minute=600, bucket_capacity=1)  # 10 req/sec
        
        # Use up the only token
        with limiter.acquire():
            pass
        
        # Now request another token - should wait
        start_time = time.time()
        with limiter.acquire() as ctx:
            elapsed = time.time() - start_time
            # Should have waited for 1/10 = 0.1 seconds
            assert elapsed >= 0.05  # Allow some tolerance

    def test_throttle_strategy_raises_error(self):
        """Test THROTTLE strategy raises error when no tokens."""
        limiter = RateLimiter(
            rate_per_minute=600,  # 10/sec
            bucket_capacity=1,
            strategy=RateLimitStrategy.THROTTLE
        )
        
        # Use up the only token
        with limiter.acquire():
            pass
        
        # Next acquisition should raise RuntimeError immediately
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            limiter.acquire()

    def test_get_wait_time(self):
        """Test calculating wait time for tokens."""
        limiter = RateLimiter(rate_per_minute=600)  # 10 tokens per second
        
        # No tokens needed, should return 0
        assert limiter.get_wait_time(1.0) == 0.0
        
        # Use up all tokens
        with limiter.acquire():
            pass
        
        # Should need to wait for tokens to refill
        wait_time = limiter.get_wait_time(1.0)
        assert wait_time > 0.0
        assert wait_time <= 0.5  # Should be around 0.1 seconds for 10/sec

    def test_get_available_tokens(self):
        """Test getting available tokens count."""
        limiter = RateLimiter(rate_per_minute=100)
        
        # Should start with full bucket
        assert abs(limiter.get_available_tokens() - 100.0) < 0.001
        
        # After using tokens, should decrease
        with limiter.acquire():
            available = limiter.get_available_tokens()
            assert abs(available - 99.0) < 0.001

    def test_reset(self):
        """Test resetting rate limiter."""
        limiter = RateLimiter(rate_per_minute=100)
        
        # Use some tokens
        with limiter.acquire():
            pass
        
        # Should not be full
        assert limiter.get_available_tokens() < 100.0
        
        # Reset should refill bucket
        limiter.reset()
        assert abs(limiter.get_available_tokens() - 100.0) < 0.001

    def test_context_manager_behavior(self):
        """Test RateLimiterContext works as context manager."""
        limiter = RateLimiter(rate_per_minute=200)
        
        with limiter.acquire() as ctx:
            assert isinstance(ctx, type(limiter.acquire()))
            # Context should be entered successfully
            assert ctx is not None

    def test_token_bucket_algorithm_behavior(self):
        """Test token bucket algorithm with actual timing."""
        limiter = RateLimiter(rate_per_minute=10, bucket_capacity=5)
        
        # Should allow burst up to bucket capacity
        start_time = time.time()
        for i in range(5):
            with limiter.acquire():
                pass
        
        elapsed = time.time() - start_time
        # First 5 requests should be instant (burst capacity)
        assert elapsed < 0.1
        
        # Next request should be rate-limited
        start_time = time.time()
        with limiter.acquire():
            pass
        elapsed = time.time() - start_time
        # Should have waited for rate limit (10/sec = 0.1s/request)
        assert elapsed >= 0.05  # Allow some tolerance

    def test_very_high_rate_limit(self):
        """Test with very high rate limits."""
        limiter = RateLimiter(rate_per_minute=10000)
        
        # Should handle high rate limits gracefully
        with limiter.acquire():
            available = limiter.get_available_tokens()
            assert abs(available - 9999.0) < 0.001
    
    def test_zero_rate_limit_raises_error(self):
        """Test that zero rate limit raises error."""
        with pytest.raises((ValueError, ZeroDivisionError)):
            RateLimiter(rate_per_minute=0)

    def test_negative_rate_limit_raises_error(self):
        """Test that negative rate limit raises error."""
        with pytest.raises(ValueError):
            RateLimiter(rate_per_minute=-1)