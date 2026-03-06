"""Test get_snapshot method implementation."""

import pytest
from unittest.mock import Mock, patch
from alpaca_data import AlpacaClient, Snapshot, Trade, Quote, Bar
from alpaca_data.exceptions import AlpacaAPIError


class TestGetSnapshot:
    """Test cases for the get_snapshot method."""

    @patch('alpaca_data.client.requests.request')
    def test_get_snapshot_single_symbol(self, mock_request):
        """Test get_snapshot with a single symbol."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshot": {
                "latest_trade": {
                    "t": "2024-01-01T15:45:00Z",
                    "x": "XNAS",
                    "p": 150.25,
                    "s": 100
                },
                "latest_quote": {
                    "t": "2024-01-01T15:44:30Z",
                    "ax": "XNAS",
                    "ap": 150.30,
                    "as": 500,
                    "bx": "XNAS",
                    "bp": 150.20,
                    "bs": 300
                },
                "minute_bar": {
                    "t": "2024-01-01T15:44:00Z",
                    "o": 150.00,
                    "h": 150.35,
                    "l": 149.95,
                    "c": 150.25,
                    "v": 5000
                },
                "daily_bar": {
                    "t": "2024-01-01T00:00:00Z",
                    "o": 149.00,
                    "h": 151.50,
                    "l": 148.75,
                    "c": 150.25,
                    "v": 100000
                }
            }
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_snapshot
        result = client.get_snapshot("AAPL")

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "AAPL"
        assert result["feed"] == "iex"
        assert len(result["snapshots"]) == 1
        
        snapshot = result["snapshots"][0]
        assert isinstance(snapshot, Snapshot)
        assert snapshot.symbol == "AAPL"
        
        # Verify latest trade
        assert snapshot.latest_trade is not None
        assert snapshot.latest_trade.price == 150.25
        assert snapshot.latest_trade.size == 100
        assert snapshot.latest_trade.exchange == "XNAS"
        
        # Verify latest quote
        assert snapshot.latest_quote is not None
        assert snapshot.latest_quote.ask_price == 150.30
        assert snapshot.latest_quote.bid_price == 150.20
        
        # Verify minute bar
        assert snapshot.minute_bar is not None
        assert snapshot.minute_bar.close == 150.25
        assert snapshot.minute_bar.volume == 5000
        
        # Verify daily bar
        assert snapshot.daily_bar is not None
        assert snapshot.daily_bar.close == 150.25
        assert snapshot.daily_bar.volume == 100000
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "stocks/AAPL/snapshot" in call_args[1]["url"]

    @patch('alpaca_data.client.requests.request')
    def test_get_snapshot_multiple_symbols(self, mock_request):
        """Test get_snapshot with multiple symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshots": [
                {
                    "S": "AAPL",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:00Z",
                        "x": "XNAS",
                        "p": 150.25,
                        "s": 100
                    },
                    "latest_quote": {
                        "t": "2024-01-01T15:44:30Z",
                        "ax": "XNAS",
                        "ap": 150.30,
                        "as": 500,
                        "bx": "XNAS",
                        "bp": 150.20,
                        "bs": 300
                    }
                },
                {
                    "S": "GOOGL",
                    "latest_trade": {
                        "t": "2024-01-01T15:45:15Z",
                        "x": "XNAS",
                        "p": 2500.50,
                        "s": 50
                    },
                    "latest_quote": {
                        "t": "2024-01-01T15:45:00Z",
                        "ax": "XNAS",
                        "ap": 2501.00,
                        "as": 200,
                        "bx": "XNAS",
                        "bp": 2500.00,
                        "bs": 150
                    }
                }
            ]
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_snapshot with multiple symbols
        result = client.get_snapshot(["AAPL", "GOOGL"])

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == ["AAPL", "GOOGL"]
        assert result["feed"] == "iex"
        assert len(result["snapshots"]) == 2
        
        # Verify first snapshot
        snapshot1 = result["snapshots"][0]
        assert snapshot1.symbol == "AAPL"
        assert snapshot1.latest_trade.price == 150.25
        
        # Verify second snapshot
        snapshot2 = result["snapshots"][1]
        assert snapshot2.symbol == "GOOGL"
        assert snapshot2.latest_trade.price == 2500.50
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "stocks/snapshots" in call_args[1]["url"]

    @patch('alpaca_data.client.requests.request')
    def test_get_snapshot_with_feed_parameter(self, mock_request):
        """Test get_snapshot with different data feed."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshot": {}
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_snapshot with SIP feed
        result = client.get_snapshot("AAPL", feed="sip")

        # Verify result structure
        assert result["count"] == 1
        assert result["symbol"] == "AAPL"
        assert result["feed"] == "sip"
        
        # Verify API call
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["feed"] == "sip"

    @patch('alpaca_data.client.requests.request')
    def test_get_snapshot_empty_response(self, mock_request):
        """Test get_snapshot with empty snapshot data."""
        # Mock successful response with empty snapshot
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshot": {}
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_snapshot
        result = client.get_snapshot("AAPL")

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "AAPL"
        assert len(result["snapshots"]) == 1
        
        snapshot = result["snapshots"][0]
        assert snapshot.symbol == "AAPL"
        # All fields should be None for empty snapshot
        assert snapshot.latest_trade is None
        assert snapshot.latest_quote is None
        assert snapshot.minute_bar is None
        assert snapshot.daily_bar is None
        assert snapshot.prev_daily_bar is None

    @patch('alpaca_data.client.requests.request')
    def test_get_snapshot_multiple_symbols_empty_response(self, mock_request):
        """Test get_snapshot with multiple symbols but empty data."""
        # Mock successful response with empty snapshots
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "snapshots": []
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_snapshot with multiple symbols
        result = client.get_snapshot(["AAPL", "GOOGL"])

        # Verify results
        assert result["count"] == 0
        assert result["symbol"] == ["AAPL", "GOOGL"]
        assert len(result["snapshots"]) == 0

    def test_snapshot_from_dict_full_data(self):
        """Test Snapshot.from_dict with complete data."""
        snapshot_data = {
            "latest_trade": {
                "t": "2024-01-01T15:45:00Z",
                "x": "XNAS",
                "p": 150.25,
                "s": 100,
                "c": ["A"]
            },
            "latest_quote": {
                "t": "2024-01-01T15:44:30Z",
                "ax": "XNAS",
                "ap": 150.30,
                "as": 500,
                "bx": "XNAS",
                "bp": 150.20,
                "bs": 300
            },
            "minute_bar": {
                "t": "2024-01-01T15:44:00Z",
                "o": 150.00,
                "h": 150.35,
                "l": 149.95,
                "c": 150.25,
                "v": 5000
            },
            "daily_bar": {
                "t": "2024-01-01T00:00:00Z",
                "o": 149.00,
                "h": 151.50,
                "l": 148.75,
                "c": 150.25,
                "v": 100000
            }
        }
        
        snapshot = Snapshot.from_dict("AAPL", snapshot_data)
        
        assert snapshot.symbol == "AAPL"
        assert snapshot.latest_trade is not None
        assert snapshot.latest_trade.price == 150.25
        assert snapshot.latest_quote is not None
        assert snapshot.latest_quote.ask_price == 150.30
        assert snapshot.minute_bar is not None
        assert snapshot.minute_bar.close == 150.25
        assert snapshot.daily_bar is not None
        assert snapshot.daily_bar.close == 150.25

    def test_snapshot_from_dict_minimal_data(self):
        """Test Snapshot.from_dict with minimal data."""
        snapshot_data = {}
        
        snapshot = Snapshot.from_dict("AAPL", snapshot_data)
        
        assert snapshot.symbol == "AAPL"
        assert snapshot.latest_trade is None
        assert snapshot.latest_quote is None
        assert snapshot.minute_bar is None
        assert snapshot.daily_bar is None
        assert snapshot.prev_daily_bar is None

    def test_snapshot_from_dict_partial_data(self):
        """Test Snapshot.from_dict with partial data."""
        snapshot_data = {
            "latest_trade": {
                "t": "2024-01-01T15:45:00Z",
                "x": "XNAS",
                "p": 150.25,
                "s": 100
            }
        }
        
        snapshot = Snapshot.from_dict("AAPL", snapshot_data)
        
        assert snapshot.symbol == "AAPL"
        assert snapshot.latest_trade is not None
        assert snapshot.latest_trade.price == 150.25
        assert snapshot.latest_quote is None
        assert snapshot.minute_bar is None
        assert snapshot.daily_bar is None
        assert snapshot.prev_daily_bar is None