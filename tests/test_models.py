"""Tests for data models."""

from datetime import datetime
import pytest
from alpaca_data.models import Bar, Quote, Trade, Snapshot, News


class TestBar:
    """Test cases for Bar model."""

    def test_bar_creation(self):
        """Test Bar can be created with required fields."""
        bar = Bar(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            open=150.0,
            high=155.0,
            low=149.0,
            close=152.0,
            volume=1000000.0,
        )
        assert bar.symbol == "AAPL"
        assert bar.open == 150.0
        assert bar.high == 155.0
        assert bar.low == 149.0
        assert bar.close == 152.0
        assert bar.volume == 1000000.0
        assert bar.trade_count is None
        assert bar.vwap is None

    def test_bar_from_dict(self):
        """Test Bar can be created from API response dict."""
        data = {
            "t": "2024-01-01T12:00:00Z",
            "o": 150.0,
            "h": 155.0,
            "l": 149.0,
            "c": 152.0,
            "v": 1000000.0,
            "n": 5000,
            "vw": 151.5,
        }
        bar = Bar.from_dict("AAPL", data)
        assert bar.symbol == "AAPL"
        assert bar.open == 150.0
        assert bar.close == 152.0
        assert bar.trade_count == 5000
        assert bar.vwap == 151.5


class TestQuote:
    """Test cases for Quote model."""

    def test_quote_creation(self):
        """Test Quote can be created."""
        quote = Quote(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            ask_exchange="Q",
            ask_price=152.0,
            ask_size=100.0,
            bid_exchange="Q",
            bid_price=151.9,
            bid_size=200.0,
        )
        assert quote.symbol == "AAPL"
        assert quote.ask_price == 152.0
        assert quote.bid_price == 151.9


class TestNews:
    """Test cases for News model."""

    def test_news_creation(self):
        """Test News can be created."""
        news = News(
            id="news_123",
            headline="Apple announces new product",
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            symbols=["AAPL"],
            source="Example News",
            summary="Summary here",
            author="John Doe",
        )
        assert news.id == "news_123"
        assert news.headline == "Apple announces new product"
        assert "AAPL" in news.symbols
