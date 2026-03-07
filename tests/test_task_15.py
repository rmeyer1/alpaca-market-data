"""Test for TASK-15: Data Models with Validation"""

import unittest
from datetime import datetime
from src.alpaca_data.models import Bar, Quote, Trade, Snapshot, News


class TestDataModels(unittest.TestCase):
    """Test cases for data model validation."""

    def test_bar_validation(self):
        """Test Bar model validation."""
        # Valid bar
        valid_bar = Bar(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=150.0,
            high=155.0,
            low=149.0,
            close=153.0,
            volume=1000000,
            trade_count=5000,
            vwap=152.5
        )
        self.assertIsInstance(valid_bar, Bar)
        
        # Invalid bar - high < open
        with self.assertRaises(ValueError):
            Bar(
                symbol="AAPL",
                timestamp=datetime.now(),
                open=150.0,
                high=140.0,  # Invalid: high < open
                low=149.0,
                close=153.0,
                volume=1000000
            )
        
        # Invalid bar - negative price
        with self.assertRaises(ValueError):
            Bar(
                symbol="AAPL",
                timestamp=datetime.now(),
                open=-150.0,  # Invalid: negative price
                high=155.0,
                low=149.0,
                close=153.0,
                volume=1000000
            )

    def test_bar_from_dict_validation(self):
        """Test Bar.from_dict with invalid data."""
        # Missing required field
        with self.assertRaises(ValueError):
            Bar.from_dict("AAPL", {"t": "2024-01-01T00:00:00Z"})  # Missing o, h, l, c, v
        
        # Invalid data format
        with self.assertRaises(ValueError):
            Bar.from_dict("AAPL", {
                "t": "2024-01-01T00:00:00Z",
                "o": "invalid",  # Not a number
                "h": 155.0,
                "l": 149.0,
                "c": 153.0,
                "v": 1000000
            })

    def test_quote_validation(self):
        """Test Quote model validation."""
        # Valid quote
        valid_quote = Quote(
            symbol="AAPL",
            timestamp=datetime.now(),
            ask_exchange="XNAS",
            ask_price=153.5,
            ask_size=100,
            bid_exchange="XNAS",
            bid_price=153.0,
            bid_size=200,
            conditions=["R"],
            tape="A"
        )
        self.assertIsInstance(valid_quote, Quote)
        
        # Invalid quote - ask <= bid
        with self.assertRaises(ValueError):
            Quote(
                symbol="AAPL",
                timestamp=datetime.now(),
                ask_exchange="XNAS",
                ask_price=153.0,  # Invalid: ask <= bid
                ask_size=100,
                bid_exchange="XNAS",
                bid_price=153.5,
                bid_size=200
            )
        
        # Invalid quote - negative size
        with self.assertRaises(ValueError):
            Quote(
                symbol="AAPL",
                timestamp=datetime.now(),
                ask_exchange="XNAS",
                ask_price=153.5,
                ask_size=-100,  # Invalid: negative size
                bid_exchange="XNAS",
                bid_price=153.0,
                bid_size=200
            )

    def test_trade_validation(self):
        """Test Trade model validation."""
        # Valid trade
        valid_trade = Trade(
            symbol="AAPL",
            timestamp=datetime.now(),
            exchange="XNAS",
            price=153.0,
            size=100,
            conditions=["@"],
            id="12345",
            tape="A"
        )
        self.assertIsInstance(valid_trade, Trade)
        
        # Invalid trade - negative price
        with self.assertRaises(ValueError):
            Trade(
                symbol="AAPL",
                timestamp=datetime.now(),
                exchange="XNAS",
                price=-153.0,  # Invalid: negative price
                size=100
            )
        
        # Invalid trade - zero size
        with self.assertRaises(ValueError):
            Trade(
                symbol="AAPL",
                timestamp=datetime.now(),
                exchange="XNAS",
                price=153.0,
                size=0  # Invalid: zero size
            )

    def test_snapshot_validation(self):
        """Test Snapshot model validation."""
        # Valid snapshot with trade
        valid_snapshot = Snapshot(
            symbol="AAPL",
            latest_trade=Trade(
                symbol="AAPL",
                timestamp=datetime.now(),
                exchange="XNAS",
                price=153.0,
                size=100
            )
        )
        self.assertIsInstance(valid_snapshot, Snapshot)
        
        # Valid empty snapshot - no data components (for empty API responses)
        empty_snapshot = Snapshot(symbol="AAPL")
        self.assertIsInstance(empty_snapshot, Snapshot)
        self.assertEqual(empty_snapshot.symbol, "AAPL")
        self.assertIsNone(empty_snapshot.latest_trade)
        self.assertIsNone(empty_snapshot.latest_quote)
        self.assertIsNone(empty_snapshot.minute_bar)
        self.assertIsNone(empty_snapshot.daily_bar)
        self.assertIsNone(empty_snapshot.prev_daily_bar)

    def test_news_validation(self):
        """Test News model validation."""
        # Valid news
        valid_news = News(
            id="12345",
            headline="Test Headline",
            created_at=datetime.now(),
            symbols=["AAPL"],
            source="Test Source"
        )
        self.assertIsInstance(valid_news, News)
        
        # Invalid news - empty headline
        with self.assertRaises(ValueError):
            News(
                id="12345",
                headline="",  # Invalid: empty headline
                created_at=datetime.now(),
                symbols=["AAPL"],
                source="Test Source"
            )
        
        # Invalid news - empty symbols list
        with self.assertRaises(ValueError):
            News(
                id="12345",
                headline="Test Headline",
                created_at=datetime.now(),
                symbols=[],  # Invalid: empty list
                source="Test Source"
            )

    def test_bar_to_dict(self):
        """Test Bar.to_dict serialization."""
        bar = Bar(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            open=150.0,
            high=155.0,
            low=149.0,
            close=153.0,
            volume=1000000
        )
        
        result = bar.to_dict()
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["open"], 150.0)
        self.assertEqual(result["high"], 155.0)
        self.assertEqual(result["low"], 149.0)
        self.assertEqual(result["close"], 153.0)
        self.assertEqual(result["volume"], 1000000)
        self.assertIn("timestamp", result)

    def test_immutability(self):
        """Test that models are immutable (frozen)."""
        bar = Bar(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=150.0,
            high=155.0,
            low=149.0,
            close=153.0,
            volume=1000000
        )
        
        # Should not be able to modify frozen dataclass
        with self.assertRaises(AttributeError):
            bar.open = 160.0

    def test_complex_snapshot(self):
        """Test complex Snapshot with multiple components."""
        # Create individual components
        trade = Trade(
            symbol="BTC/USD",
            timestamp=datetime.now(),
            exchange="CBSE",
            price=50000.0,
            size=1.5
        )
        
        quote = Quote(
            symbol="BTC/USD",
            timestamp=datetime.now(),
            ask_exchange="CBSE",
            ask_price=50010.0,
            ask_size=2.0,
            bid_exchange="CBSE",
            bid_price=49990.0,
            bid_size=1.0
        )
        
        bar = Bar(
            symbol="BTC/USD",
            timestamp=datetime.now(),
            open=49950.0,
            high=50020.0,
            low=49940.0,
            close=50000.0,
            volume=100.5
        )
        
        # Create snapshot with multiple components
        snapshot = Snapshot(
            symbol="BTC/USD",
            latest_trade=trade,
            latest_quote=quote,
            daily_bar=bar
        )
        
        self.assertEqual(snapshot.symbol, "BTC/USD")
        self.assertIsNotNone(snapshot.latest_trade)
        self.assertIsNotNone(snapshot.latest_quote)
        self.assertIsNotNone(snapshot.daily_bar)

    def test_news_with_optional_fields(self):
        """Test News model with all optional fields."""
        news = News(
            id="67890",
            headline="Breaking: Market Update",
            created_at=datetime(2024, 1, 1, 10, 0, 0),
            updated_at=datetime(2024, 1, 1, 11, 0, 0),
            symbols=["AAPL", "GOOGL", "MSFT"],
            source="Financial Times",
            summary="Market shows positive trends",
            author="John Doe",
            url="https://example.com/news/123",
            content="Full article content here..."
        )
        
        self.assertEqual(news.id, "67890")
        self.assertEqual(len(news.symbols), 3)
        self.assertEqual(news.author, "John Doe")
        self.assertIsNotNone(news.updated_at)


if __name__ == '__main__':
    unittest.main()