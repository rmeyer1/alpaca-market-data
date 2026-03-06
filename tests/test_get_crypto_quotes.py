"""Test get_crypto_quotes method implementation."""

import pytest
from unittest.mock import Mock, patch
from alpaca_data import AlpacaClient, Quote
from alpaca_data.exceptions import AlpacaAPIError


class TestGetCryptoQuotes:
    """Test cases for the get_crypto_quotes method."""

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_single_symbol(self, mock_request):
        """Test get_crypto_quotes with a single crypto symbol."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                    "c": ["R"],
                    "z": "B"
                },
                {
                    "t": "2024-01-01T12:01:00Z",
                    "ax": "CBSE",
                    "ap": 42001.00,
                    "as": 3.2,
                    "bx": "CBSE",
                    "bp": 41995.75,
                    "bs": 2.1,
                    "c": ["R"],
                    "z": "B"
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes
        result = client.get_crypto_quotes("BTC/USD")

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == "BTC/USD"
        assert result["has_next_page"] is False
        assert len(result["quotes"]) == 2

        # Verify first quote
        quote1 = result["quotes"][0]
        assert quote1.symbol == "BTC/USD"
        assert quote1.timestamp.isoformat().startswith("2024-01-01T12:00:00")
        assert quote1.ask_exchange == "CBSE"
        assert quote1.ask_price == 42000.50
        assert quote1.ask_size == 2.5
        assert quote1.bid_exchange == "CBSE"
        assert quote1.bid_price == 41995.25
        assert quote1.bid_size == 1.8
        assert quote1.conditions == ["R"]
        assert quote1.tape == "B"

        # Verify second quote
        quote2 = result["quotes"][1]
        assert quote2.symbol == "BTC/USD"
        assert quote2.ask_price == 42001.00
        assert quote2.bid_price == 41995.75

        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "crypto/quotes/BTC/USD" in call_args[1]["url"]
        params = call_args[1]["params"]
        assert params["limit"] == 1000
        assert params["sort"] == "asc"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_multiple_symbols(self, mock_request):
        """Test get_crypto_quotes with multiple crypto symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "S": "BTC/USD",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                    "c": ["R"],
                    "z": "B"
                },
                {
                    "t": "2024-01-01T12:00:00Z",
                    "S": "ETH/USD",
                    "ax": "CBSE",
                    "ap": 2500.75,
                    "as": 5.0,
                    "bx": "CBSE",
                    "bp": 2500.25,
                    "bs": 4.2,
                    "c": ["R"],
                    "z": "B"
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes with multiple symbols
        result = client.get_crypto_quotes(["BTC/USD", "ETH/USD"])

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == ["BTC/USD", "ETH/USD"]
        assert result["has_next_page"] is False
        assert len(result["quotes"]) == 2

        # Verify symbols are correctly assigned
        quote1 = result["quotes"][0]
        quote2 = result["quotes"][1]
        
        assert quote1.symbol == "BTC/USD"
        assert quote2.symbol == "ETH/USD"
        assert quote1.ask_price == 42000.50
        assert quote2.ask_price == 2500.75

        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "crypto/quotes" in call_args[1]["url"]
        params = call_args[1]["params"]
        assert params["symbols"] == "BTC/USD,ETH/USD"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_date_range(self, mock_request):
        """Test get_crypto_quotes with date range parameters."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T09:30:00Z",
                    "ax": "CBSE",
                    "ap": 41900.00,
                    "as": 1.0,
                    "bx": "CBSE",
                    "bp": 41895.00,
                    "bs": 1.0,
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes with date range
        result = client.get_crypto_quotes(
            "BTC/USD",
            start="2024-01-01T09:30:00-05:00",
            end="2024-01-01T16:00:00-05:00"
        )

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "BTC/USD"

        # Verify API call includes date range
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["start"] == "2024-01-01T09:30:00-05:00"
        assert call_args[1]["params"]["end"] == "2024-01-01T16:00:00-05:00"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_limit(self, mock_request):
        """Test get_crypto_quotes with custom limit."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes with custom limit
        result = client.get_crypto_quotes("BTC/USD", limit=50)

        # Verify results
        assert result["count"] == 1

        # Verify API call includes custom limit
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["limit"] == 50

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_exchange(self, mock_request):
        """Test get_crypto_quotes with exchange filter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes with exchange filter
        result = client.get_crypto_quotes("BTC/USD", exchange="CBSE")

        # Verify results
        assert result["count"] == 1
        assert result["exchange"] == "CBSE"

        # Verify API call includes exchange filter
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["exchange"] == "CBSE"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_sort_desc(self, mock_request):
        """Test get_crypto_quotes with descending sort order."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:01:00Z",
                    "ax": "CBSE",
                    "ap": 42001.00,
                    "as": 3.2,
                    "bx": "CBSE",
                    "bp": 41995.75,
                    "bs": 2.1,
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes with descending sort
        result = client.get_crypto_quotes("BTC/USD", sort="desc")

        # Verify results
        assert result["count"] == 1

        # Verify API call includes descending sort
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["sort"] == "desc"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_pagination(self, mock_request):
        """Test get_crypto_quotes with pagination."""
        # Mock successful response with next page token
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                }
            ],
            "next_page_token": "next_page_token_123"
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes
        result = client.get_crypto_quotes("BTC/USD")

        # Verify results
        assert result["count"] == 1
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "next_page_token_123"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_page_token(self, mock_request):
        """Test get_crypto_quotes with page token parameter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes with page token
        result = client.get_crypto_quotes("BTC/USD", page_token="test_token")

        # Verify API call includes page token
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["params"]["page_token"] == "test_token"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_empty_response(self, mock_request):
        """Test get_crypto_quotes with empty quotes response."""
        # Mock empty response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": []
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes
        result = client.get_crypto_quotes("BTC/USD")

        # Verify results
        assert result["count"] == 0
        assert result["symbol"] == "BTC/USD"
        assert len(result["quotes"]) == 0
        assert result["has_next_page"] is False

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_api_error(self, mock_request):
        """Test get_crypto_quotes handles API errors properly."""
        # Mock error response
        import requests
        http_error = requests.exceptions.HTTPError()
        http_error.response = Mock()
        http_error.response.status_code = 401
        http_error.response.json.return_value = {
            "message": "Invalid API key"
        }
        http_error.response.content = b'{"message": "Invalid API key"}'
        mock_request.side_effect = http_error

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Verify AlpacaAPIError is raised
        with pytest.raises(AlpacaAPIError):
            client.get_crypto_quotes("BTC/USD")

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_quotes_with_optional_fields(self, mock_request):
        """Test get_crypto_quotes with all optional fields populated."""
        # Mock response with all optional fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "ax": "CBSE",
                    "ap": 42000.50,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 41995.25,
                    "bs": 1.8,
                    "c": ["R", "I"],
                    "z": "B"
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_quotes
        result = client.get_crypto_quotes("BTC/USD")

        # Verify results
        assert result["count"] == 1
        quote = result["quotes"][0]
        
        # Verify all fields
        assert quote.symbol == "BTC/USD"
        assert quote.conditions == ["R", "I"]
        assert quote.tape == "B"