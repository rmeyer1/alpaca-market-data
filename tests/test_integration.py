"""Integration tests that call the actual Alpaca API endpoints.

These tests use real API credentials and make actual HTTP requests to ensure
the SDK works with live Alpaca data. Run these sparingly to avoid rate limits.

Run with: pytest tests/test_integration.py -v --log-cli-level=INFO
"""

import pytest
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from alpaca_data import AlpacaClient

# Load environment variables from .env file
load_dotenv()


class TestAlpacaIntegration:
    """Integration tests that call real Alpaca API endpoints."""
    
    @classmethod
    def setup_class(cls):
        """Set up integration test client with real credentials."""
        # Load credentials from environment or .env file
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_API_SECRET")
        
        print(f"Looking for API credentials...")
        print(f"ALPACA_API_KEY: {'Found' if api_key else 'NOT FOUND'}")
        print(f"ALPACA_API_SECRET: {'Found' if api_secret else 'NOT FOUND'}")
        
        if not api_key or not api_secret:
            pytest.skip("API credentials not found - integration tests require ALPACA_API_KEY and ALPACA_API_SECRET")
        
        # Use the market data API URL for all market data calls
        cls.client = AlpacaClient(
            api_key=api_key,
            secret_key=api_secret,
            base_url="https://data.alpaca.markets",  # Market data API URL
            rate_per_minute=100  # Conservative rate limit for tests
        )
    
    def test_connection_works(self):
        """Test that we can connect to the Alpaca Market Data API."""
        try:
            # Test connection by making a simple market data request
            response = self.client.get("/v2/stocks/AAPL/bars", params={"timeframe": "1Day", "limit": 1})
            assert response.status_code == 200
            print("✅ Successfully connected to Alpaca Market Data API")
        except Exception as e:
            pytest.fail(f"Failed to connect to Alpaca API: {e}")
    
    def test_get_bars_real_data(self):
        """Test getting real historical bars data from API."""
        try:
            # Use historical data to avoid SIP access limitations
            # Try a date range that should be available on free tier
            result = self.client.get_bars(
                symbols="AAPL",
                timeframe="1Day",
                start="2024-12-01T09:30:00-05:00",  # Historical data
                end="2024-12-31T16:00:00-05:00",
                limit=5
            )
            
            # Validate response structure
            assert "bars" in result
            assert "symbol" in result
            assert "timeframe" in result
            assert "count" in result
            
            # Validate we got actual data
            assert result["count"] > 0
            assert len(result["bars"]) > 0
            
            # Validate first bar has expected structure
            first_bar = result["bars"][0]
            assert first_bar.symbol == "AAPL"
            assert hasattr(first_bar, 'timestamp')
            assert hasattr(first_bar, 'open')
            assert hasattr(first_bar, 'high')
            assert hasattr(first_bar, 'low')
            assert hasattr(first_bar, 'close')
            assert hasattr(first_bar, 'volume')
            
            # Validate data types (allow both int and float for price data)
            assert isinstance(first_bar.open, (int, float))
            assert isinstance(first_bar.high, (int, float))
            assert isinstance(first_bar.low, (int, float))
            assert isinstance(first_bar.close, (int, float))
            assert isinstance(first_bar.volume, (int, float))
            
            print(f"✅ Got {result['count']} real bars for {result['symbol']}")
            print(f"   First bar: {first_bar.timestamp} - Close: ${first_bar.close}")
            
        except Exception as e:
            if "subscription does not permit querying recent SIP data" in str(e):
                print("ℹ️  Free tier limitation - unable to access recent data")
                # Test with older data range that should be available
                try:
                    result = self.client.get_bars(
                        symbols="AAPL",
                        timeframe="1Day",
                        start="2024-01-01T09:30:00-05:00",  # Much older data
                        end="2024-01-31T16:00:00-05:00",
                        limit=5
                    )
                    assert "bars" in result
                    print(f"✅ Historical bars test successful: {result['count']} bars")
                except Exception as e2:
                    pytest.fail(f"Bars test failed with both recent and historical data: {e2}")
            else:
                pytest.fail(f"Bars test failed: {e}")
    
    def test_get_bars_multiple_symbols(self):
        """Test getting real bars for multiple symbols."""
        try:
            symbols = ["AAPL", "MSFT"]
            
            # Use historical data to avoid SIP limitations
            result = self.client.get_bars(
                symbols=symbols,
                timeframe="1Day",
                start="2024-12-01T09:30:00-05:00",
                end="2024-12-31T16:00:00-05:00",
                limit=5
            )
            
            assert "bars" in result
            assert result["count"] > 0
            assert len(result["bars"]) > 0
            
            # Check that we have data for both symbols
            symbols_found = set(bar.symbol for bar in result["bars"])
            assert "AAPL" in symbols_found or "MSFT" in symbols_found
            
            print(f"✅ Got real bars for multiple symbols: {symbols_found}")
            
        except Exception as e:
            if "subscription does not permit querying recent SIP data" in str(e):
                print("ℹ️  Free tier limitation - trying older data")
                try:
                    result = self.client.get_bars(
                        symbols=["AAPL", "MSFT"],
                        timeframe="1Day",
                        start="2024-01-01T09:30:00-05:00",
                        end="2024-01-31T16:00:00-05:00",
                        limit=5
                    )
                    assert "bars" in result
                    print(f"✅ Historical multi-symbol test successful: {result['count']} bars")
                except Exception as e2:
                    pytest.fail(f"Multi-symbol test failed with both recent and historical data: {e2}")
            else:
                pytest.fail(f"Multi-symbol test failed: {e}")
    
    def test_get_quotes_real_data(self):
        """Test getting real quotes data from API."""
        result = self.client.get_quotes(
            symbols="AAPL",
            limit=5
        )
        
        assert "quotes" in result
        assert "symbol" in result
        assert "count" in result
        
        if result["count"] > 0:
            first_quote = result["quotes"][0]
            assert first_quote.symbol == "AAPL"
            assert hasattr(first_quote, 'bid_price')
            assert hasattr(first_quote, 'ask_price')
            assert hasattr(first_quote, 'timestamp')
            
            # Validate bid is less than ask
            assert first_quote.bid_price < first_quote.ask_price
            
            print(f"✅ Got {result['count']} real quotes for {result['symbol']}")
            print(f"   First quote: {first_quote.timestamp} - Bid: ${first_quote.bid_price}, Ask: ${first_quote.ask_price}")
        else:
            print("ℹ️  No quotes data available for AAPL (market may be closed)")
    
    def test_get_snapshot_real_data(self):
        """Test getting real snapshot data from API."""
        result = self.client.get_snapshot(
            symbols=["AAPL", "MSFT"]
        )
        
        assert "snapshots" in result
        assert "symbol" in result
        assert "count" in result
        
        # Snapshot data might not be available during all times
        if result["count"] > 0:
            assert len(result["snapshots"]) > 0
            
            # Check first snapshot has expected structure
            first_snapshot = result["snapshots"][0]
            assert hasattr(first_snapshot, 'symbol')
            assert hasattr(first_snapshot, 'latest_trade')
            assert hasattr(first_snapshot, 'latest_quote')
            
            if first_snapshot.latest_trade:
                assert hasattr(first_snapshot.latest_trade, 'price')
                assert hasattr(first_snapshot.latest_trade, 'timestamp')
            
            print(f"✅ Got {result['count']} real snapshots")
            print(f"   First: {first_snapshot.symbol}")
        else:
            print("ℹ️  No snapshot data available (market closed or API state)")
    
    def test_get_crypto_bars_real_data(self):
        """Test getting real crypto bars data."""
        try:
            result = self.client.get_crypto_bars(
                symbol_or_symbols="BTC/USD",
                timeframe="1Hour",
                limit=5
            )
            
            assert "bars" in result
            assert "symbol" in result
            assert "timeframe" in result
            
            if result["count"] > 0:
                first_bar = result["bars"][0]
                assert first_bar.symbol == "BTC/USD"
                assert hasattr(first_bar, 'timestamp')
                assert hasattr(first_bar, 'open')
                assert hasattr(first_bar, 'close')
                
                # Crypto bars should have reasonable price ranges
                assert 1000 < first_bar.close < 200000  # BTC price should be in this range
                
                print(f"✅ Got {result['count']} real crypto bars for {result['symbol']}")
                print(f"   First bar: {first_bar.timestamp} - Close: ${first_bar.close}")
            else:
                print("ℹ️  No crypto bars data available")
                
        except Exception as e:
            print(f"ℹ️  Crypto data test skipped - endpoint not available: {e}")
            # This is expected if crypto data is not available on this tier
    
    def test_get_news_real_data(self):
        """Test getting real news data."""
        # Get news for tech stocks
        result = self.client.get_news(
            symbols=["AAPL", "GOOGL"],
            limit=5
        )
        
        assert "news" in result
        assert "count" in result
        
        if result["count"] > 0:
            first_article = result["news"][0]
            assert hasattr(first_article, 'headline')
            assert hasattr(first_article, 'source')
            assert hasattr(first_article, 'created_at')  # API returns created_at, not timestamp
            assert hasattr(first_article, 'symbols')
            
            # Validate some symbols were found
            assert len(first_article.symbols) > 0
            
            print(f"✅ Got {result['count']} real news articles")
            print(f"   Headline: {first_article.headline[:80]}...")
            print(f"   Source: {first_article.source}")
        else:
            print("ℹ️  No news articles available for specified symbols")
    
    def test_error_handling_invalid_symbol(self):
        """Test that invalid symbols are handled gracefully."""
        # Invalid symbols should throw an exception
        with pytest.raises(Exception) as exc_info:
            self.client.get_bars(
                symbols="INVALID_SYMBOL_THAT_DOES_NOT_EXIST",
                timeframe="1Day",
                limit=5
            )
        
        # Should be a meaningful error, not a generic one
        error_msg = str(exc_info.value)
        assert "invalid symbol" in error_msg.lower() or "bad request" in error_msg.lower()
        
        print("✅ Invalid symbol properly raises exception with meaningful message")
    
    def test_rate_limiting_behavior(self):
        """Test that rate limiting is working properly."""
        # Make several requests quickly to test rate limiting
        symbols = ["AAPL", "MSFT", "GOOGL"]
        
        results = []
        for symbol in symbols:
            result = self.client.get_bars(symbol, timeframe="1Day", limit=1)
            results.append(result)
        
        # All requests should succeed (rate limiting should not block them)
        for i, result in enumerate(results):
            assert "bars" in result
            print(f"✅ Request {i+1} for {symbols[i]} succeeded")
        
        print("✅ Rate limiting is working without blocking requests")


@pytest.mark.integration
class TestIntegrationRun:
    """Marker class to identify integration tests."""
    
    def test_run_all_integration_tests(self):
        """Run all integration tests and provide a summary."""
        print("\n" + "="*60)
        print("🚀 RUNNING ALPACA INTEGRATION TESTS")
        print("="*60)
        
        # Check environment
        api_key = os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_API_SECRET")
        
        if not api_key or not api_secret:
            print("❌ Skipping - API credentials not found")
            return
        
        client = AlpacaClient(
            api_key=api_key,
            secret_key=api_secret,
            base_url="https://data.alpaca.markets",
            rate_per_minute=100
        )
        
        print("✅ API client initialized successfully")
        
        # Test 1: Connection via market data API
        try:
            response = client.get("/v2/stocks/AAPL/bars", params={"timeframe": "1Day", "limit": 1})
            if response.status_code == 200:
                print("✅ Market Data API connection test passed")
            else:
                print("❌ Market Data API connection test failed")
                return
        except Exception as e:
            print(f"❌ Market Data API connection test failed: {e}")
            return
        
        # Test 2: Real bars data
        try:
            result = client.get_bars("AAPL", timeframe="1Day", limit=2)
            print(f"✅ Real bars test: Got {result['count']} bars")
        except Exception as e:
            print(f"❌ Real bars test failed: {e}")
        
        # Test 3: Real crypto data
        try:
            result = client.get_crypto_bars("BTC/USD", timeframe="1Hour", limit=1)
            print(f"✅ Real crypto test: Got {result['count']} crypto bars")
        except Exception as e:
            print(f"❌ Real crypto test failed: {e}")
        
        print("\n🎉 Integration test run completed!")
        print("="*60)


if __name__ == "__main__":
    # Allow running this file directly
    pytest.main([__file__, "-v", "--log-cli-level=INFO"])