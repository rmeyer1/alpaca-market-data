"""Test get_crypto_snapshot method implementation."""

import pytest
from unittest.mock import Mock, patch
from alpaca_data import AlpacaClient, Snapshot, Trade, Quote, Bar
from alpaca_data.exceptions import AlpacaAPIError


class TestGetCryptoSnapshot:
    """Test cases for the get_crypto_snapshot method."""

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_single_symbol(self, mock_request):
        """Test get_crypto_snapshot with a single crypto symbol."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshot": {
                "latest_trade": {
                    "t": "2024-01-01T15:45:00Z",
                    "x": "CBSE",
                    "p": 45000.25,
                    "s": 0.5
                },
                "latest_quote": {
                    "t": "2024-01-01T15:44:30Z",
                    "ax": "CBSE",
                    "ap": 45010.30,
                    "as": 2.5,
                    "bx": "CBSE",
                    "bp": 44990.20,
                    "bs": 1.8
                },
                "minute_bar": {
                    "t": "2024-01-01T15:44:00Z",
                    "o": 44950.00,
                    "h": 45025.35,
                    "l": 44940.95,
                    "c": 45000.25,
                    "v": 125.5
                },
                "daily_bar": {
                    "t": "2024-01-01T00:00:00Z",
                    "o": 44000.00,
                    "h": 45200.50,
                    "l": 43850.75,
                    "c": 45000.25,
                    "v": 2500.75
                }
            }
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot
        result = client.get_crypto_snapshot("BTC/USD")

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "BTC/USD"
        assert len(result["snapshots"]) == 1
        
        snapshot = result["snapshots"][0]
        assert isinstance(snapshot, Snapshot)
        assert snapshot.symbol == "BTC/USD"
        
        # Verify latest trade
        assert snapshot.latest_trade is not None
        assert snapshot.latest_trade.price == 45000.25
        assert snapshot.latest_trade.size == 0.5
        assert snapshot.latest_trade.exchange == "CBSE"
        
        # Verify latest quote
        assert snapshot.latest_quote is not None
        assert snapshot.latest_quote.ask_price == 45010.30
        assert snapshot.latest_quote.bid_price == 44990.20
        
        # Verify minute bar
        assert snapshot.minute_bar is not None
        assert snapshot.minute_bar.close == 45000.25
        assert snapshot.minute_bar.volume == 125.5
        
        # Verify daily bar
        assert snapshot.daily_bar is not None
        assert snapshot.daily_bar.close == 45000.25
        assert snapshot.daily_bar.volume == 2500.75
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "crypto/snapshots/BTC/USD" in call_args[1]["url"]

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_multiple_symbols(self, mock_request):
        """Test get_crypto_snapshot with multiple crypto symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshots": [
                {
                    "S": "BTC/USD",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:00Z",
                        "x": "CBSE",
                        "p": 45000.25,
                        "s": 0.5
                    },
                    "latest_quote": {
                        "t": "2024-01-01T15:44:30Z",
                        "ax": "CBSE",
                        "ap": 45010.30,
                        "as": 2.5,
                        "bx": "CBSE",
                        "bp": 44990.20,
                        "bs": 1.8
                    }
                },
                {
                    "S": "ETH/USD",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:15Z",
                        "x": "CBSE",
                        "p": 2800.50,
                        "s": 15.0
                    },
                    "latest_quote": {
                        "t": "2024-01-01T15:45:00Z",
                        "ax": "CBSE",
                        "ap": 2810.00,
                        "as": 50.0,
                        "bx": "CBSE",
                        "bp": 2790.00,
                        "bs": 35.0
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot with multiple symbols
        result = client.get_crypto_snapshot(["BTC/USD", "ETH/USD"])

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == ["BTC/USD", "ETH/USD"]
        assert len(result["snapshots"]) == 2
        
        # Verify first snapshot
        snapshot1 = result["snapshots"][0]
        assert snapshot1.symbol == "BTC/USD"
        assert snapshot1.latest_trade.price == 45000.25
        
        # Verify second snapshot
        snapshot2 = result["snapshots"][1]
        assert snapshot2.symbol == "ETH/USD"
        assert snapshot2.latest_trade.price == 2800.50
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "crypto/snapshots" in call_args[1]["url"]
        params = call_args[1]["params"]
        assert params["symbols"] == "BTC/USD,ETH/USD"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_with_exchange_parameter(self, mock_request):
        """Test get_crypto_snapshot with exchange filter."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshot": {}
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot with exchange filter
        result = client.get_crypto_snapshot("BTC/USD", exchange="CBSE")

        # Verify result structure
        assert result["count"] == 1
        assert result["symbol"] == "BTC/USD"
        assert result["exchange"] == "CBSE"
        
        # Verify API call
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["exchange"] == "CBSE"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_empty_response(self, mock_request):
        """Test get_crypto_snapshot with empty snapshot data."""
        # Mock successful response with empty snapshot
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshot": {}
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot
        result = client.get_crypto_snapshot("BTC/USD")

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "BTC/USD"
        assert len(result["snapshots"]) == 1
        
        snapshot = result["snapshots"][0]
        assert snapshot.symbol == "BTC/USD"
        # All fields should be None for empty snapshot
        assert snapshot.latest_trade is None
        assert snapshot.latest_quote is None
        assert snapshot.minute_bar is None
        assert snapshot.daily_bar is None
        assert snapshot.prev_daily_bar is None

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_multiple_symbols_empty_response(self, mock_request):
        """Test get_crypto_snapshot with multiple symbols but empty data."""
        # Mock successful response with empty snapshots
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshots": []
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot with multiple symbols
        result = client.get_crypto_snapshot(["BTC/USD", "ETH/USD"])

        # Verify results
        assert result["count"] == 0
        assert result["symbol"] == ["BTC/USD", "ETH/USD"]
        assert len(result["snapshots"]) == 0

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_different_crypto_pairs(self, mock_request):
        """Test get_crypto_snapshot with various crypto pairs."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshots": [
                {
                    "S": "BTC/USD",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:00Z",
                        "x": "CBSE",
                        "p": 45000.25,
                        "s": 0.5
                    }
                },
                {
                    "S": "ETH/USD",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:15Z",
                        "x": "CBSE",
                        "p": 2800.50,
                        "s": 15.0
                    }
                },
                {
                    "S": "ADA/USD",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:30Z",
                        "x": "CBSE",
                        "p": 0.85,
                        "s": 5000.0
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot with various pairs
        result = client.get_crypto_snapshot(["BTC/USD", "ETH/USD", "ADA/USD"])

        # Verify results
        assert result["count"] == 3
        assert len(result["snapshots"]) == 3
        
        # Verify different crypto pairs
        assert result["snapshots"][0].symbol == "BTC/USD"
        assert result["snapshots"][0].latest_trade.price == 45000.25
        
        assert result["snapshots"][1].symbol == "ETH/USD"
        assert result["snapshots"][1].latest_trade.price == 2800.50
        
        assert result["snapshots"][2].symbol == "ADA/USD"
        assert result["snapshots"][2].latest_trade.price == 0.85

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_with_exchange_filter_multiple(self, mock_request):
        """Test get_crypto_snapshot with exchange filter for multiple symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshots": [
                {
                    "S": "BTC/USD",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:00Z",
                        "x": "CBSE",
                        "p": 45000.25,
                        "s": 0.5
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot with exchange filter
        result = client.get_crypto_snapshot(["BTC/USD", "ETH/USD"], exchange="CBSE")

        # Verify results
        assert result["count"] == 1
        assert result["exchange"] == "CBSE"
        
        # Verify API call with exchange parameter
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["exchange"] == "CBSE"
        assert params["symbols"] == "BTC/USD,ETH/USD"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_handles_api_error(self, mock_request):
        """Test get_crypto_snapshot handles API errors gracefully."""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "message": "Rate limit exceeded"
        }
        mock_response.headers = {"Retry-After": "60"}
        mock_response.raise_for_status.side_effect = AlpacaAPIError("Rate limit exceeded", 429)
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot and expect AlpacaAPIError
        with pytest.raises(AlpacaAPIError) as exc_info:
            client.get_crypto_snapshot("BTC/USD")
        
        assert "Rate limit exceeded" in str(exc_info.value)

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_api_call_parameters(self, mock_request):
        """Test that get_crypto_snapshot makes correct API calls."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"snapshot": {}}
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot
        client.get_crypto_snapshot("BTC/USD")

        # Verify API call was made with correct parameters
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        
        assert call_kwargs["method"] == "GET"
        assert "crypto/snapshots/BTC/USD" in call_kwargs["url"]
        assert "APCA-API-KEY-ID" in call_kwargs["headers"]
        assert "APCA-API-SECRET-KEY" in call_kwargs["headers"]
        assert call_kwargs["headers"]["APCA-API-KEY-ID"] == "test_key"
        assert call_kwargs["headers"]["APCA-API-SECRET-KEY"] == "test_secret"

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_multiple_symbols_api_call_parameters(self, mock_request):
        """Test API call parameters for multiple crypto symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"snapshots": []}
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_crypto_snapshot with multiple symbols
        client.get_crypto_snapshot(["BTC/USD", "ETH/USD"])

        # Verify API call was made with correct parameters
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        
        assert call_kwargs["method"] == "GET"
        assert "crypto/snapshots" in call_kwargs["url"]
        params = call_kwargs["params"]
        assert params["symbols"] == "BTC/USD,ETH/USD"

    def test_crypto_snapshot_model_from_dict(self):
        """Test that crypto snapshots work with the same model as regular snapshots."""
        # This test ensures the same Snapshot model works for both stock and crypto data
        crypto_snapshot_data = {
            "latest_trade": {
                "t": "2024-01-01T15:45:00Z",
                "x": "CBSE",
                "p": 45000.25,
                "s": 0.5
            },
            "latest_quote": {
                "t": "2024-01-01T15:44:30Z",
                "ax": "CBSE",
                "ap": 45010.30,
                "as": 2.5,
                "bx": "CBSE",
                "bp": 44990.20,
                "bs": 1.8
            }
        }
        
        # Create snapshot from crypto data
        snapshot = Snapshot.from_dict("BTC/USD", crypto_snapshot_data)
        
        assert snapshot.symbol == "BTC/USD"
        assert snapshot.latest_trade.price == 45000.25
        assert snapshot.latest_trade.exchange == "CBSE"
        assert snapshot.latest_quote.ask_price == 45010.30
        assert snapshot.latest_quote.bid_price == 44990.20

    @patch('alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_with_special_crypto_symbols(self, mock_request):
        """Test get_crypto_snapshot with various crypto symbol formats."""
        test_cases = [
            "BTC/USD",
            "ETH/USD", 
            "ADA/USD",
            "SOL/USD",
            "DOGE/USD"
        ]
        
        for symbol in test_cases:
            # Reset mock
            mock_request.reset_mock()
            
            # Mock response for this symbol
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "snapshot": {
                    "latest_trade": {
                        "t": "2024-01-01T15:45:00Z",
                        "x": "CBSE",
                        "p": 100.0,
                        "s": 1.0
                    }
                }
            }
            mock_request.return_value = mock_response

            # Create client
            client = AlpacaClient(api_key="test_key", secret_key="test_secret")

            # Call get_crypto_snapshot
            result = client.get_crypto_snapshot(symbol)

            # Verify results
            assert result["count"] == 1
            assert result["symbol"] == symbol
            assert len(result["snapshots"]) == 1
            assert result["snapshots"][0].symbol == symbol
            
            # Verify API call for this symbol
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert symbol in call_args[1]["url"]