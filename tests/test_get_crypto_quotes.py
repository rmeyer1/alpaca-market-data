"""Tests for get_crypto_quotes endpoint."""

import pytest
import responses
from alpaca_data import AlpacaClient
from alpaca_data.models import Quote
from datetime import datetime


class TestGetCryptoQuotes:
    """Test suite for get_crypto_quotes method."""

    @pytest.fixture
    def client(self):
        """Create AlpacaClient instance for testing."""
        return AlpacaClient(
            api_key="test_key",
            secret_key="test_secret",
            base_url="https://paper-api.alpaca.markets"
        )

    @pytest.fixture
    def mock_single_quote_response(self):
        """Mock response for single crypto quote."""
        return {
            "quotes": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "bp": 45000.0,
                    "bs": 2.5,
                    "bx": "CBSE",
                    "ap": 45010.0,
                    "as": 1.8,
                    "ax": "CBSE"
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }

    @pytest.fixture
    def mock_multiple_quotes_response(self):
        """Mock response for multiple crypto quotes."""
        return {
            "quotes": [
                {
                    "S": "BTC/USD",
                    "t": "2024-01-01T10:00:00.000Z",
                    "bp": 45000.0,
                    "bs": 2.5,
                    "bx": "CBSE",
                    "ap": 45010.0,
                    "as": 1.8,
                    "ax": "CBSE"
                },
                {
                    "S": "ETH/USD", 
                    "t": "2024-01-01T10:01:00.000Z",
                    "bp": 2800.0,
                    "bs": 10.0,
                    "bx": "CBSE",
                    "ap": 2805.0,
                    "as": 8.5,
                    "ax": "CBSE"
                }
            ],
            "symbols": "BTC/USD,ETH/USD",
            "next_page_token": None
        }

    @responses.activate
    def test_get_single_crypto_quote_basic(self, client, mock_single_quote_response):
        """Test getting a single crypto quote with default parameters."""
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_single_quote_response,
            status=200
        )

        result = client.get_crypto_quotes("BTC/USD")

        # Verify response structure
        assert "quotes" in result
        assert "symbol" in result
        assert "next_page_token" in result
        assert "count" in result
        assert result["symbol"] == "BTC/USD"
        assert result["count"] == 1
        assert result["has_next_page"] is False

        # Verify quote data
        quotes = result["quotes"]
        assert len(quotes) == 1
        quote = quotes[0]
        
        assert isinstance(quote, Quote)
        assert quote.symbol == "BTC/USD"
        assert isinstance(quote.timestamp, datetime)
        assert quote.bid_price == 45000.0
        assert quote.bid_size == 2.5
        assert quote.bid_exchange == "CBSE"
        assert quote.ask_price == 45010.0
        assert quote.ask_size == 1.8
        assert quote.ask_exchange == "CBSE"
        assert quote.conditions is None
        assert quote.tape is None

    @responses.activate
    def test_get_multiple_crypto_quotes(self, client, mock_multiple_quotes_response):
        """Test getting quotes for multiple crypto symbols."""
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes",
            json=mock_multiple_quotes_response,
            status=200
        )

        result = client.get_crypto_quotes(["BTC/USD", "ETH/USD"])

        # Verify response structure
        assert "quotes" in result
        assert "symbol" in result
        assert "count" in result
        assert result["symbol"] == ["BTC/USD", "ETH/USD"]
        assert result["count"] == 2

        # Verify quotes
        quotes = result["quotes"]
        assert len(quotes) == 2

        # First quote (BTC/USD)
        btc_quote = quotes[0]
        assert btc_quote.symbol == "BTC/USD"
        assert btc_quote.bid_price == 45000.0
        assert btc_quote.ask_price == 45010.0

        # Second quote (ETH/USD)
        eth_quote = quotes[1]
        assert eth_quote.symbol == "ETH/USD"
        assert eth_quote.bid_price == 2800.0
        assert eth_quote.ask_price == 2805.0

    @responses.activate
    def test_get_crypto_quotes_with_date_range(self, client):
        """Test getting crypto quotes with start and end dates."""
        mock_response = {
            "quotes": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        start_time = "2024-01-01T09:00:00-05:00"
        end_time = "2024-01-01T17:00:00-05:00"
        
        result = client.get_crypto_quotes(
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
    def test_get_crypto_quotes_with_exchange_filter(self, client):
        """Test getting crypto quotes filtered by exchange."""
        mock_response = {
            "quotes": [],
            "symbol": "BTC/USD",
            "exchange": "CBSE",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_quotes("BTC/USD", exchange="CBSE")

        # Verify exchange filter was applied
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "exchange=CBSE" in request.url
        
        # Verify response includes exchange info
        assert "exchange" in result
        assert result["exchange"] == "CBSE"

    @responses.activate
    def test_get_crypto_quotes_with_custom_sort(self, client):
        """Test getting crypto quotes with custom sort order."""
        mock_response = {
            "quotes": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        client.get_crypto_quotes("BTC/USD", sort="desc")

        # Verify sort parameter was applied
        request = responses.calls[0].request
        assert "sort=desc" in request.url

    @responses.activate
    def test_get_crypto_quotes_with_pagination(self, client):
        """Test getting crypto quotes with pagination token."""
        mock_response = {
            "quotes": [],
            "symbol": "BTC/USD",
            "next_page_token": "next_page_token_123"
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_quotes("BTC/USD", page_token="test_token")

        # Verify pagination token was sent
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "page_token=test_token" in request.url
        
        # Verify response indicates more pages
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "next_page_token_123"

    @responses.activate
    def test_get_crypto_quotes_with_quote_conditions(self, client):
        """Test crypto quotes with additional quote conditions."""
        mock_response = {
            "quotes": [
                {
                    "t": "2024-01-01T10:00:00.000Z",
                    "bp": 45000.0,
                    "bs": 2.5,
                    "bx": "CBSE",
                    "ap": 45010.0,
                    "as": 1.8,
                    "ax": "CBSE",
                    "c": ["R", "H"],  # Quote conditions
                    "z": "A"  # Tape code
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_quotes("BTC/USD")
        quote = result["quotes"][0]

        # Verify quote conditions and tape were parsed
        assert quote.conditions == ["R", "H"]
        assert quote.tape == "A"

    @responses.activate
    def test_get_crypto_quotes_empty_response(self, client):
        """Test getting crypto quotes when no quotes are available."""
        mock_response = {
            "quotes": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        result = client.get_crypto_quotes("BTC/USD")

        assert result["quotes"] == []
        assert result["count"] == 0
        assert result["has_next_page"] is False

    @responses.activate
    def test_get_crypto_quotes_large_limit(self, client):
        """Test getting crypto quotes with large limit."""
        mock_response = {
            "quotes": [],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        
        responses.add(
            responses.GET,
            "https://paper-api.alpaca.markets/v1beta1/crypto/quotes/BTC/USD",
            json=mock_response,
            status=200
        )

        client.get_crypto_quotes("BTC/USD", limit=1000)

        # Verify large limit was applied
        request = responses.calls[0].request
        assert "limit=1000" in request.url

    def test_get_crypto_quotes_type_validation(self, client):
        """Test that get_crypto_quotes handles different input types correctly."""
        # Test that the method exists and is callable
        assert callable(getattr(client, 'get_crypto_quotes', None))
        
        # Test type hints would catch incorrect usage at runtime
        # This is more of a runtime check than a unit test
        try:
            client.get_crypto_quotes(123)  # Should raise TypeError
            assert False, "Expected TypeError for invalid symbol type"
        except (TypeError, AttributeError):
            pass  # Expected

    def test_crypto_quotes_quote_model_compatibility(self, client):
        """Test that crypto quotes work with the Quote model."""
        # This test verifies the Quote.from_dict can handle crypto data
        crypto_quote_data = {
            "t": "2024-01-01T10:00:00.000Z",
            "bp": 45000.0,
            "bs": 2.5,
            "bx": "CBSE",
            "ap": 45010.0,
            "as": 1.8,
            "ax": "CBSE"
        }
        
        quote = Quote.from_dict("BTC/USD", crypto_quote_data)
        
        # Verify all Quote attributes work with crypto data
        assert quote.symbol == "BTC/USD"
        assert quote.bid_price == 45000.0
        assert quote.ask_price == 45010.0
        assert quote.bid_exchange == "CBSE"
        assert quote.ask_exchange == "CBSE"
        assert isinstance(quote.timestamp, datetime)