"""Tests for options data models."""

from datetime import datetime
import pytest
from alpaca_data.models import Bar, Greeks, OptionQuote, OptionTrade, OptionSnapshot


class TestGreeks:
    """Test cases for Greeks model."""

    def test_greeks_creation(self):
        """Test Greeks can be created with valid values."""
        greeks = Greeks(
            delta=0.452,
            gamma=0.0345,
            theta=-0.125,
            vega=0.089,
            rho=0.023,
        )
        assert greeks.delta == 0.452
        assert greeks.gamma == 0.0345
        assert greeks.theta == -0.125
        assert greeks.vega == 0.089
        assert greeks.rho == 0.023

    def test_greeks_delta_validation(self):
        """Test Greeks validates Delta range."""
        with pytest.raises(ValueError, match="Delta must be between -1.0 and 1.0"):
            Greeks(delta=1.5, gamma=0.0, theta=0.0, vega=0.0, rho=0.0)

        with pytest.raises(ValueError, match="Delta must be between -1.0 and 1.0"):
            Greeks(delta=-1.5, gamma=0.0, theta=0.0, vega=0.0, rho=0.0)

    def test_greeks_gamma_validation(self):
        """Test Greeks validates Gamma is non-negative."""
        with pytest.raises(ValueError, match="Gamma must be non-negative"):
            Greeks(delta=0.5, gamma=-0.1, theta=0.0, vega=0.0, rho=0.0)

    def test_greeks_vega_validation(self):
        """Test Greeks validates Vega is non-negative."""
        with pytest.raises(ValueError, match="Vega must be non-negative"):
            Greeks(delta=0.5, gamma=0.0, theta=0.0, vega=-0.1, rho=0.0)

    def test_greeks_from_dict(self):
        """Test Greeks can be created from API response."""
        data = {
            "delta": 0.452,
            "gamma": 0.0345,
            "theta": -0.125,
            "vega": 0.089,
            "rho": 0.023,
        }
        greeks = Greeks.from_dict(data)
        assert greeks.delta == 0.452
        assert greeks.gamma == 0.0345

    def test_greeks_to_dict(self):
        """Test Greeks can be converted to dictionary."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        result = greeks.to_dict()
        assert result["delta"] == 0.452
        assert result["gamma"] == 0.0345
        assert result["theta"] == -0.125

    def test_greeks_missing_fields(self):
        """Test Greeks validates required fields."""
        with pytest.raises(ValueError, match="Required field 'delta' missing"):
            Greeks.from_dict({"gamma": 0.1})


class TestOptionQuote:
    """Test cases for OptionQuote model."""

    def test_option_quote_creation(self):
        """Test OptionQuote can be created with basic fields."""
        quote = OptionQuote(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            bid_price=2.45,
            ask_price=2.55,
            bid_size=100,
            ask_size=150,
            bid_exchange="BOX",
            ask_exchange="BOX",
        )
        assert quote.symbol == "AAPL230120C00150000"
        assert quote.bid_price == 2.45
        assert quote.ask_price == 2.55
        assert quote.bid_size == 100
        assert quote.ask_size == 150

    def test_option_quote_with_greeks(self):
        """Test OptionQuote can include Greeks."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        quote = OptionQuote(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            bid_price=2.45,
            ask_price=2.55,
            bid_size=100,
            ask_size=150,
            bid_exchange="BOX",
            ask_exchange="BOX",
            greeks=greeks,
            iv=0.285,
            open_interest=1250,
            underlying_price=150.25,
        )
        assert quote.greeks.delta == 0.452
        assert quote.iv == 0.285
        assert quote.open_interest == 1250
        assert quote.underlying_price == 150.25

    def test_option_quote_validation(self):
        """Test OptionQuote validates required fields."""
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            OptionQuote(
                symbol="",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                bid_price=2.45,
                ask_price=2.55,
                bid_size=100,
                ask_size=150,
                bid_exchange="BOX",
                ask_exchange="BOX",
            )

    def test_option_quote_price_validation(self):
        """Test OptionQuote validates price relationships."""
        with pytest.raises(ValueError, match="Ask price .* must be greater than bid price"):
            OptionQuote(
                symbol="AAPL230120C00150000",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                bid_price=2.55,
                ask_price=2.45,  # Ask < Bid
                bid_size=100,
                ask_size=150,
                bid_exchange="BOX",
                ask_exchange="BOX",
            )

    def test_option_quote_from_dict(self):
        """Test OptionQuote can be created from API response."""
        data = {
            "t": "2024-01-01T12:00:00Z",
            "bp": 2.45,
            "ap": 2.55,
            "bs": 100,
            "as": 150,
            "bx": "BOX",
            "ax": "BOX",
            "iv": 0.285,
            "oi": 1250,
            "underlying_price": 150.25,
            "greeks": {
                "delta": 0.452,
                "gamma": 0.0345,
                "theta": -0.125,
                "vega": 0.089,
                "rho": 0.023,
            },
        }
        quote = OptionQuote.from_dict("AAPL230120C00150000", data)
        assert quote.symbol == "AAPL230120C00150000"
        assert quote.bid_price == 2.45
        assert quote.greeks.delta == 0.452
        assert quote.iv == 0.285

    def test_option_quote_iv_validation(self):
        """Test OptionQuote validates implied volatility range."""
        with pytest.raises(ValueError, match="Implied volatility must be between 0 and 1"):
            OptionQuote(
                symbol="AAPL230120C00150000",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                bid_price=2.45,
                ask_price=2.55,
                bid_size=100,
                ask_size=150,
                bid_exchange="BOX",
                ask_exchange="BOX",
                iv=1.5,  # > 1.0
            )

    def test_option_quote_to_dict(self):
        """Test OptionQuote can be converted to dictionary."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        quote = OptionQuote(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            bid_price=2.45,
            ask_price=2.55,
            bid_size=100,
            ask_size=150,
            bid_exchange="BOX",
            ask_exchange="BOX",
            greeks=greeks,
            iv=0.285,
        )
        result = quote.to_dict()
        assert result["symbol"] == "AAPL230120C00150000"
        assert result["bid_price"] == 2.45
        assert result["greeks"]["delta"] == 0.452


class TestOptionTrade:
    """Test cases for OptionTrade model."""

    def test_option_trade_creation(self):
        """Test OptionTrade can be created with basic fields."""
        trade = OptionTrade(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            price=2.50,
            size=100,
            exchange="BOX",
        )
        assert trade.symbol == "AAPL230120C00150000"
        assert trade.price == 2.50
        assert trade.size == 100
        assert trade.exchange == "BOX"

    def test_option_trade_with_greeks(self):
        """Test OptionTrade can include Greeks."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        trade = OptionTrade(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            price=2.50,
            size=100,
            exchange="BOX",
            conditions="@",
            iv=0.285,
            underlying_price=150.25,
            greeks=greeks,
        )
        assert trade.greeks.delta == 0.452
        assert trade.conditions == "@"
        assert trade.iv == 0.285

    def test_option_trade_validation(self):
        """Test OptionTrade validates required fields."""
        with pytest.raises(ValueError, match="Price must be positive"):
            OptionTrade(
                symbol="AAPL230120C00150000",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                price=-2.50,  # Negative price
                size=100,
                exchange="BOX",
            )

        with pytest.raises(ValueError, match="Size must be positive"):
            OptionTrade(
                symbol="AAPL230120C00150000",
                timestamp=datetime(2024, 1, 1, 12, 0, 0),
                price=2.50,
                size=-100,  # Negative size
                exchange="BOX",
            )

    def test_option_trade_from_dict(self):
        """Test OptionTrade can be created from API response."""
        data = {
            "t": "2024-01-01T12:00:00Z",
            "p": 2.50,
            "s": 100,
            "x": "BOX",
            "c": "@",
            "iv": 0.285,
            "underlying_price": 150.25,
            "greeks": {
                "delta": 0.452,
                "gamma": 0.0345,
                "theta": -0.125,
                "vega": 0.089,
                "rho": 0.023,
            },
        }
        trade = OptionTrade.from_dict("AAPL230120C00150000", data)
        assert trade.symbol == "AAPL230120C00150000"
        assert trade.price == 2.50
        assert trade.size == 100
        assert trade.greeks.delta == 0.452

    def test_option_trade_to_dict(self):
        """Test OptionTrade can be converted to dictionary."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        trade = OptionTrade(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            price=2.50,
            size=100,
            exchange="BOX",
            greeks=greeks,
        )
        result = trade.to_dict()
        assert result["symbol"] == "AAPL230120C00150000"
        assert result["price"] == 2.50
        assert result["greeks"]["delta"] == 0.452


class TestOptionSnapshot:
    """Test cases for OptionSnapshot model."""

    def test_option_snapshot_creation(self):
        """Test OptionSnapshot can be created with basic fields."""
        snapshot = OptionSnapshot(symbol="AAPL230120C00150000")
        assert snapshot.symbol == "AAPL230120C00150000"
        assert snapshot.latest_trade is None
        assert snapshot.latest_quote is None
        assert snapshot.greeks is None

    def test_option_snapshot_with_all_fields(self):
        """Test OptionSnapshot can include all fields."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        
        # Create nested objects
        trade = OptionTrade(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            price=2.50,
            size=100,
            exchange="BOX",
        )
        
        quote = OptionQuote(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            bid_price=2.45,
            ask_price=2.55,
            bid_size=100,
            ask_size=150,
            bid_exchange="BOX",
            ask_exchange="BOX",
        )
        
        bar = Bar(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            open=2.40,
            high=2.60,
            low=2.35,
            close=2.50,
            volume=1000.0,
        )
        
        snapshot = OptionSnapshot(
            symbol="AAPL230120C00150000",
            iv=0.285,
            open_interest=1250,
            latest_trade=trade,
            latest_quote=quote,
            greeks=greeks,
            minute_bar=bar,
            daily_bar=bar,
            underlying_price=150.25,
        )
        
        assert snapshot.symbol == "AAPL230120C00150000"
        assert snapshot.iv == 0.285
        assert snapshot.open_interest == 1250
        assert snapshot.latest_trade.price == 2.50
        assert snapshot.latest_quote.bid_price == 2.45
        assert snapshot.greeks.delta == 0.452
        assert snapshot.minute_bar.close == 2.50
        assert snapshot.underlying_price == 150.25

    def test_option_snapshot_validation(self):
        """Test OptionSnapshot validates required fields."""
        with pytest.raises(ValueError, match="Symbol must be a non-empty string"):
            OptionSnapshot(symbol="")

        with pytest.raises(ValueError, match="Implied volatility must be between 0 and 1"):
            OptionSnapshot(symbol="AAPL230120C00150000", iv=1.5)

        with pytest.raises(ValueError, match="Open interest must be non-negative"):
            OptionSnapshot(symbol="AAPL230120C00150000", open_interest=-100)

    def test_option_snapshot_from_dict(self):
        """Test OptionSnapshot can be created from API response."""
        data = {
            "iv": 0.285,
            "oi": 1250,
            "underlying_price": 150.25,
            "latest_trade": {
                "t": "2024-01-01T12:00:00Z",
                "p": 2.50,
                "s": 100,
                "x": "BOX",
            },
            "latest_quote": {
                "t": "2024-01-01T12:00:00Z",
                "bp": 2.45,
                "ap": 2.55,
                "bs": 100,
                "as": 150,
                "bx": "BOX",
                "ax": "BOX",
            },
            "greeks": {
                "delta": 0.452,
                "gamma": 0.0345,
                "theta": -0.125,
                "vega": 0.089,
                "rho": 0.023,
            },
            "minute_bar": {
                "t": "2024-01-01T12:00:00Z",
                "o": 2.40,
                "h": 2.60,
                "l": 2.35,
                "c": 2.50,
                "v": 1000.0,
            },
        }
        snapshot = OptionSnapshot.from_dict("AAPL230120C00150000", data)
        assert snapshot.symbol == "AAPL230120C00150000"
        assert snapshot.iv == 0.285
        assert snapshot.latest_trade.price == 2.50
        assert snapshot.latest_quote.bid_price == 2.45
        assert snapshot.greeks.delta == 0.452
        assert snapshot.minute_bar.close == 2.50

    def test_option_snapshot_nested_validation(self):
        """Test OptionSnapshot validates nested objects."""
        # Test invalid latest_trade
        with pytest.raises(ValueError, match="latest_trade must be an OptionTrade object"):
            OptionSnapshot(
                symbol="AAPL230120C00150000",
                latest_trade="invalid"  # Should be OptionTrade
            )

        # Test invalid greeks
        with pytest.raises(ValueError, match="greeks must be a Greeks object"):
            OptionSnapshot(
                symbol="AAPL230120C00150000",
                greeks="invalid"  # Should be Greeks
            )

    def test_option_snapshot_to_dict(self):
        """Test OptionSnapshot can be converted to dictionary."""
        greeks = Greeks(delta=0.452, gamma=0.0345, theta=-0.125, vega=0.089, rho=0.023)
        trade = OptionTrade(
            symbol="AAPL230120C00150000",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            price=2.50,
            size=100,
            exchange="BOX",
        )
        
        snapshot = OptionSnapshot(
            symbol="AAPL230120C00150000",
            iv=0.285,
            latest_trade=trade,
            greeks=greeks,
        )
        
        result = snapshot.to_dict()
        assert result["symbol"] == "AAPL230120C00150000"
        assert result["iv"] == 0.285
        assert result["latest_trade"]["price"] == 2.50
        assert result["greeks"]["delta"] == 0.452