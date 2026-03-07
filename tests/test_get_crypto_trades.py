"""Tests for get_crypto_trades endpoint."""

import pytest
import responses
from alpaca_data import AlpacaClient
from alpaca_data.models import Trade
from datetime import datetime


class TestGetCryptoTrades:
    """Test suite for get_crypto_trades method."""

    @pytest.fixture
    def client(self):
        """Create AlpacaClient instance for testing."""
        return AlpacaClient(
            api_key="test_key",
            secret_key="test_secret",
            base_url="https://paper-api.alpaca.markets"
        )

    @pytest.fixture
    def mock_single_trade_response(self):
        """Mock response for single crypto trade."""
        return {
            "trades": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "p": 45000.0,
                    "s": 2.5,
                    "x": "CBSE",
                    "i": "trade_id_123"
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }

    @pytest.fixture
    def mock_multiple_trades_response(self):
        """Mock response for multiple crypto trades."""
        return {
            "trades": [
                {
                    "S": "BTC/USD",
                    "t": "2024-01-01T10:00:00.000Z",
                    "p": 45000.0,
                    "s": 2.5,
                    "x": "CBSE",
                    "i": "btc_trade_001"
                },
                {
                    "S": "ETH/USD", 
                    "t": "2024-01-01T10:01:00.000Z",
                    "p": 2800.0,
                    "s": 10.0,
                    "x": "CBSE",
                    "i": "eth_trade_001"
                }
            ],
            "symbols": "BTC/USD,ETH/USD",
            "next_page_token": None
        }

    @responses.activate
    def test_get_single_crypto_trade_basic(self, client, mock_single_trade_response):
        """Test getting a single crypto trade with default parameters."""
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_single_trade_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD")

        # Verify response structure
        assert "trades" in result
        assert "symbol" in result
        assert "next_page_token" in result
        assert "count" in result
        assert result["symbol"] == "BTC/USD"
        assert result["count"] == 1
        assert result["has_next_page"] is False

        # Verify trade data
        trades = result["trades"]
        assert len(trades) == 1
        trade = trades[0]
        
        assert isinstance(trade, Trade)
        assert trade.symbol == "BTC/USD"
        assert isinstance(trade.timestamp, datetime)
        assert trade.price == 45000.0
        assert trade.size == 2.5
        assert trade.exchange == "CBSE"
        assert trade.id == "trade_id_123"
        assert trade.conditions is None
        assert trade.tape is None

    @responses.activate
    def test_get_multiple_crypto_trades(self, client, mock_multiple_trades_response):
        """Test getting trades for multiple crypto symbols."""
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades",
            json=mock_multiple_trades_response,
            status=200
        )

        result = client.get_crypto_trades(["BTC/USD", "ETH/USD"])

        # Verify response structure
        assert "trades" in result
        assert "symbol" in result
        assert "count" in result
        assert result["symbol"] == ["BTC/USD", "ETH/USD"]
        assert result["count"] == 2

        # Verify trades
        trades = result["trades"]
        assert len(trades) == 2

        # First trade (BTC/USD)
        btc_trade = trades[0]
        assert btc_trade.symbol == "BTC/USD"
        assert btc_trade.price == 45000.0
        assert btc_trade.size == 2.5
        assert btc_trade.exchange == "CBSE"
        assert btc_trade.id == "btc_trade_001"

        # Second trade (ETH/USD)
        eth_trade = trades[1]
        assert eth_trade.symbol == "ETH/USD"
        assert eth_trade.price == 2800.0
        assert eth_trade.size == 10.0
        assert eth_trade.exchange == "CBSE"
        assert eth_trade.id == "eth_trade_001"

    @responses.activate
    def test_get_crypto_trades_with_date_range(self, client):
        """Test getting crypto trades with start and end dates."""
        mock_response = {
            "trades": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        start_time = "2024-01-01T09:00:00-05:00"
        end_time = "2024-01-01T17:00:00-05:00"
        
        result = client.get_crypto_trades(
            "BTC/USD",
            start=start_time,
            end=end_time,
            limit=100
        )

        # Verify request was made with correct parameters
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        
        # Check URL parameters (account for URL encoding)
        assert "BTC/USD" in request.url
        # The datetime strings get URL-encoded, so check for the encoded versions
        assert "start=" in request.url
        assert "end=" in request.url
        assert "limit=100" in request.url

    @responses.activate
    def test_get_crypto_trades_with_exchange_filter(self, client):
        """Test getting crypto trades filtered by exchange."""
        mock_response = {
            "trades": [],
            "symbol": "BTC/USD",
            "exchange": "CBSE",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD", exchange="CBSE")

        # Verify exchange filter was applied
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "exchange=CBSE" in request.url
        
        # Verify response includes exchange info
        assert "exchange" in result
        assert result["exchange"] == "CBSE"

    @responses.activate
    def test_get_crypto_trades_with_custom_sort(self, client):
        """Test getting crypto trades with custom sort order."""
        mock_response = {
            "trades": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        client.get_crypto_trades("BTC/USD", sort="desc")

        # Verify sort parameter was applied
        request = responses.calls[0].request
        assert "sort=desc" in request.url

    @responses.activate
    def test_get_crypto_trades_with_pagination(self, client):
        """Test getting crypto trades with pagination token."""
        mock_response = {
            "trades": [],
            "symbol": "BTC/USD",
            "next_page_token": "next_page_token_456"
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD", page_token="test_token")

        # Verify pagination token was sent
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "page_token=test_token" in request.url
        
        # Verify response indicates more pages
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "next_page_token_456"

    @responses.activate
    def test_get_crypto_trades_with_conditions_and_id(self, client):
        """Test crypto trades with conditions, tape, and trade ID."""
        mock_response = {
            "trades": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "p": 45000.0,
                    "s": 2.5,
                    "x": "CBSE",
                    "i": "unique_trade_id",
                    "c": ["T", "O"],  # Trade conditions
                    "z": "B"  # Tape code
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD")
        trade = result["trades"][0]

        # Verify trade conditions, ID, and tape were parsed
        assert trade.conditions == ["T", "O"]
        assert trade.tape == "B"
        assert trade.id == "unique_trade_id"

    @responses.activate
    def test_get_crypto_trades_with_different_exchanges(self, client):
        """Test crypto trades from different exchanges."""
        mock_response = {
            "trades": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "p": 45000.0,
                    "s": 1.0,
                    "x": "CBSE",
                    "i": "cbse_trade"
                },
                {
                    "t": "2024-01-01T10:01:00.000Z",
                    "p": 45005.0,
                    "s": 0.5,
                    "x": "NYSE",
                    "i": "nyse_trade"
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD")
        trades = result["trades"]

        # Verify trades from different exchanges
        assert len(trades) == 2
        assert trades[0].exchange == "CBSE"
        assert trades[1].exchange == "NYSE"
        assert trades[0].price == 45000.0
        assert trades[1].price == 45005.0

    @responses.activate
    def test_get_crypto_trades_empty_response(self, client):
        """Test getting crypto trades when no trades are available."""
        mock_response = {
            "trades": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD")

        assert result["trades"] == []
        assert result["count"] == 0
        assert result["has_next_page"] is False

    @responses.activate
    def test_get_crypto_trades_large_limit(self, client):
        """Test getting crypto trades with large limit."""
        mock_response = {
            "trades": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        client.get_crypto_trades("BTC/USD", limit=1000)

        # Verify large limit was applied
        request = responses.calls[0].request
        assert "limit=1000" in request.url

    def test_get_crypto_trades_type_validation(self, client):
        """Test that get_crypto_trades handles different input types correctly."""
        # Test that the method exists and is callable
        assert callable(getattr(client, 'get_crypto_trades', None))
        
        # Test type hints would catch incorrect usage at runtime
        try:
            client.get_crypto_trades(123)  # Should raise TypeError
            assert False, "Expected TypeError for invalid symbol type"
        except (TypeError, AttributeError):
            pass  # Expected

    def test_crypto_trades_trade_model_compatibility(self, client):
        """Test that crypto trades work with the Trade model."""
        # This test verifies the Trade.from_dict can handle crypto data
        crypto_trade_data = {
            "t": "2024-01-01T10:00:00.000Z",
            "p": 45000.0,
            "s": 2.5,
            "x": "CBSE",
            "i": "crypto_trade_001"
        }
        
        trade = Trade.from_dict("BTC/USD", crypto_trade_data)
        
        # Verify all Trade attributes work with crypto data
        assert trade.symbol == "BTC/USD"
        assert trade.price == 45000.0
        assert trade.size == 2.5
        assert trade.exchange == "CBSE"
        assert trade.id == "crypto_trade_001"
        assert isinstance(trade.timestamp, datetime)

    @responses.activate
    def test_get_crypto_trades_various_timeframes(self, client):
        """Test crypto trades with different trade sizes and prices."""
        mock_response = {
            "trades": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "p": 0.01,  # Very small trade
                    "s": 0.001,  # Very small size
                    "x": "CBSE"
                },
                {
                    "t": "2024-01-01T10:01:00.000Z",
                    "p": 50000.0,  # Large price
                    "s": 100.0,   # Large size
                    "x": "CBSE"
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD")
        trades = result["trades"]

        # Verify different trade sizes and prices are handled correctly
        assert trades[0].price == 0.01
        assert trades[0].size == 0.001
        assert trades[1].price == 50000.0
        assert trades[1].size == 100.0

    @responses.activate
    def test_get_crypto_trades_multiple_symbols_limit(self, client):
        """Test getting trades for multiple symbols with custom limit."""
        mock_response = {
            "trades": [],
            "symbols": "BTC/USD,ETH/USD,LTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades(
            ["BTC/USD", "ETH/USD", "LTC/USD"],
            limit=50
        )

        # Verify multiple symbols and limit were applied
        request = responses.calls[0].request
        # The "/" in symbols gets URL-encoded to "%2F"
        assert "BTC%2FUSD" in request.url
        assert "limit=50" in request.url

    @responses.activate
    def test_get_crypto_trades_api_response_structure(self, client):
        """Test that the API response structure is parsed correctly."""
        mock_response = {
            "trades": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "p": 45000.0,
                    "s": 1.0,
                    "x": "CBSE",
                    "i": "btc_001"
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": "page_token_789"
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/trades/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_trades("BTC/USD")

        # Verify complete response structure
        assert "trades" in result
        assert "symbol" in result
        assert "next_page_token" in result
        assert "count" in result
        assert "has_next_page" in result
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "page_token_789"