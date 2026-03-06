"""Test get_crypto_bars method implementation."""

import pytest
from unittest.mock import Mock, patch
from alpaca_data import AlpacaClient, Bar
from alpaca_data.exceptions import AlpacaAPIError


class TestGetCryptoBars:
    """Test cases for the get_crypto_bars method."""

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_single_symbol(self, mock_request):
        """Test get_crypto_bars with a single crypto symbol."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "o": 42000.50,
                    "h": 42100.75,
                    "l": 41950.25,
                    "c": 42075.30,
                    "v": 1234.56
                },
                {
                    "t": "2024-01-01T13:00:00Z",
                    "o": 42075.30,
                    "h": 42200.00,
                    "l": 42050.00,
                    "c": 42150.45,
                    "v": 987.65
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars
        result = client.get_crypto_bars("BTC/USD")

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == "BTC/USD"
        assert result["timeframe"] == "1Day"
        assert result["has_next_page"] is False
        assert len(result["bars"]) == 2
        
        # Verify bars
        bar1, bar2 = result["bars"]
        assert bar1.symbol == "BTC/USD"
        assert bar1.open == 42000.50
        assert bar1.high == 42100.75
        assert bar1.low == 41950.25
        assert bar1.close == 42075.30
        assert bar1.volume == 1234.56
        
        assert bar2.symbol == "BTC/USD"
        assert bar2.open == 42075.30
        assert bar2.close == 42150.45
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "crypto/bars/BTC/USD" in call_args[1]["url"]
        params = call_args[1]["params"]
        assert params["timeframe"] == "1Day"
        assert params["limit"] == 1000
        assert params["sort"] == "asc"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_multiple_symbols(self, mock_request):
        """Test get_crypto_bars with multiple crypto symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": [
                {
                    "S": "BTC/USD",
                    "t": "2024-01-01T12:00:00Z",
                    "o": 42000.50,
                    "h": 42100.75,
                    "l": 41950.25,
                    "c": 42075.30,
                    "v": 1234.56
                },
                {
                    "S": "ETH/USD",
                    "t": "2024-01-01T12:00:00Z",
                    "o": 2500.25,
                    "h": 2510.50,
                    "l": 2495.00,
                    "c": 2508.75,
                    "v": 5432.10
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars with multiple symbols
        result = client.get_crypto_bars(["BTC/USD", "ETH/USD"])

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == ["BTC/USD", "ETH/USD"]
        assert len(result["bars"]) == 2
        
        # Verify BTC/USD bar
        btc_bar = result["bars"][0]
        assert btc_bar.symbol == "BTC/USD"
        assert btc_bar.close == 42075.30
        
        # Verify ETH/USD bar
        eth_bar = result["bars"][1]
        assert eth_bar.symbol == "ETH/USD"
        assert eth_bar.close == 2508.75
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "crypto/bars" in call_args[1]["url"]
        params = call_args[1]["params"]
        assert "BTC/USD,ETH/USD" in params["symbols"]

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_with_timeframe(self, mock_request):
        """Test get_crypto_bars with different timeframe."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": []
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars with hourly timeframe
        result = client.get_crypto_bars("BTC/USD", timeframe="1Hour", limit=100)

        # Verify result structure
        assert result["count"] == 0
        assert result["symbol"] == "BTC/USD"
        assert result["timeframe"] == "1Hour"
        
        # Verify API call with timeframe
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["timeframe"] == "1Hour"
        assert params["limit"] == 100

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_with_date_range(self, mock_request):
        """Test get_crypto_bars with start and end dates."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": []
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars with date range
        result = client.get_crypto_bars(
            "BTC/USD",
            start="2024-01-01T00:00:00Z",
            end="2024-01-02T00:00:00Z",
            sort="desc"
        )

        # Verify API call with date parameters
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["start"] == "2024-01-01T00:00:00Z"
        assert params["end"] == "2024-01-02T00:00:00Z"
        assert params["sort"] == "desc"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_with_exchange(self, mock_request):
        """Test get_crypto_bars with exchange filter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": []
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars with exchange filter
        result = client.get_crypto_bars("BTC/USD", exchange="CBSE")

        # Verify result includes exchange info
        assert result["exchange"] == "CBSE"
        
        # Verify API call with exchange parameter
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["exchange"] == "CBSE"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_pagination(self, mock_request):
        """Test get_crypto_bars with pagination."""
        # Mock response with next page token
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": [
                {
                    "t": "2024-01-01T14:00:00Z",
                    "o": 42150.00,
                    "h": 42200.00,
                    "l": 42100.00,
                    "c": 42175.50,
                    "v": 567.89
                }
            ],
            "next_page_token": "next_page_token_xyz"
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars
        result = client.get_crypto_bars("BTC/USD")

        # Verify pagination info
        assert result["count"] == 1
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "next_page_token_xyz"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_with_page_token(self, mock_request):
        """Test get_crypto_bars with page token (ignores other params)."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": [],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars with page token
        result = client.get_crypto_bars(
            "BTC/USD",
            start="2024-01-01",
            end="2024-01-02",
            limit=500,
            page_token="existing_token"
        )

        # Verify API call includes page token
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["page_token"] == "existing_token"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_eth_usd(self, mock_request):
        """Test get_crypto_bars with ETH/USD pair."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": [
                {
                    "t": "2024-01-01T12:00:00Z",
                    "o": 2500.00,
                    "h": 2525.50,
                    "l": 2495.25,
                    "c": 2518.75,
                    "v": 8765.43
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_bars for ETH/USD
        result = client.get_crypto_bars("ETH/USD", timeframe="1Hour", limit=50)

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "ETH/USD"
        assert len(result["bars"]) == 1
        
        bar = result["bars"][0]
        assert bar.symbol == "ETH/USD"
        assert bar.open == 2500.00
        assert bar.high == 2525.50
        assert bar.low == 2495.25
        assert bar.close == 2518.75
        assert bar.volume == 8765.43
        
        # Verify API call for ETH/USD
        call_args = mock_request.call_args
        assert "crypto/bars/ETH/USD" in call_args[1]["url"]

    def test_bar_from_dict_crypto_data(self):
        """Test Bar.from_dict with crypto bar data."""
        bar_data = {
            "t": "2024-01-01T15:30:00Z",
            "o": 50000.25,
            "h": 50100.00,
            "l": 49950.75,
            "c": 50075.50,
            "v": 2345.67,
            "vwap": 50050.30,
            "n": 150  # trade count
        }
        
        bar = Bar.from_dict("BTC/USD", bar_data)
        
        assert bar.symbol == "BTC/USD"
        assert bar.timestamp.year == 2024
        assert bar.open == 50000.25
        assert bar.high == 50100.00
        assert bar.low == 49950.75
        assert bar.close == 50075.50
        assert bar.volume == 2345.67
        assert bar.vwap == 50050.30
        assert bar.trade_count == 150

    def test_bar_from_dict_crypto_minimal(self):
        """Test Bar.from_dict with minimal crypto bar data."""
        bar_data = {
            "t": "2024-01-01T10:00:00Z",
            "o": 3000.00,
            "h": 3050.00,
            "l": 2950.00,
            "c": 3025.00,
            "v": 1500.00
        }
        
        bar = Bar.from_dict("ETH/USD", bar_data)
        
        assert bar.symbol == "ETH/USD"
        assert bar.open == 3000.00
        assert bar.close == 3025.00
        assert bar.volume == 1500.00
        # Optional fields should be None
        assert bar.vwap is None
        assert bar.trade_count is None

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_bars_different_timeframes(self, mock_request):
        """Test get_crypto_bars with various timeframes."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bars": []
        }
        mock_request.return_value = mock_response

        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Test various timeframes
        timeframes = ["1Min", "5Min", "15Min", "1Hour", "1Day", "1Week", "1Month"]
        
        for timeframe in timeframes:
            result = client.get_crypto_bars("BTC/USD", timeframe=timeframe)
            assert result["timeframe"] == timeframe
            
            # Verify API call
            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["timeframe"] == timeframe