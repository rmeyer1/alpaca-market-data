"""Test get_trades method implementation."""

import pytest
from unittest.mock import Mock, patch
from alpaca_data import AlpacaClient, Trade
from alpaca_data.exceptions import AlpacaAPIError


class TestGetTrades:
    """Test cases for the get_trades method."""

    @patch('alpaca_data.client.requests.request')
    def test_get_trades_single_symbol(self, mock_request):
        """Test get_trades with a single symbol."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trades": [
                {
                    "t": "2024-01-01T14:30:00Z",
                    "x": "XNAS",
                    "p": 150.25,
                    "s": 100,
                    "c": ["A"],
                    "i": "12345",
                    "z": "B"
                }
            ],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_trades
        result = client.get_trades("AAPL", limit=10)

        # Verify results
        assert result["count"] == 1
        assert result["symbol"] == "AAPL"
        assert len(result["trades"]) == 1
        
        trade = result["trades"][0]
        assert isinstance(trade, Trade)
        assert trade.symbol == "AAPL"
        assert trade.exchange == "XNAS"
        assert trade.price == 150.25
        assert trade.size == 100
        assert trade.conditions == ["A"]
        assert trade.id == "12345"
        assert trade.tape == "B"
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "stocks/AAPL/trades" in call_args[1]["url"]

    @patch('alpaca_data.client.requests.request')
    def test_get_trades_multiple_symbols(self, mock_request):
        """Test get_trades with multiple symbols."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trades": [
                {
                    "t": "2024-01-01T14:30:00Z",
                    "x": "XNAS",
                    "p": 150.25,
                    "s": 100,
                    "S": "AAPL"
                },
                {
                    "t": "2024-01-01T14:31:00Z",
                    "x": "XNAS",
                    "p": 2500.50,
                    "s": 50,
                    "S": "GOOGL"
                }
            ],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_trades with multiple symbols
        result = client.get_trades(["AAPL", "GOOGL"], limit=10)

        # Verify results
        assert result["count"] == 2
        assert result["symbol"] == ["AAPL", "GOOGL"]
        assert len(result["trades"]) == 2
        
        # Verify first trade
        trade1 = result["trades"][0]
        assert trade1.symbol == "AAPL"
        assert trade1.price == 150.25
        
        # Verify second trade
        trade2 = result["trades"][1]
        assert trade2.symbol == "GOOGL"
        assert trade2.price == 2500.50
        
        # Verify API call
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "stocks/trades" in call_args[1]["url"]

    @patch('alpaca_data.client.requests.request')
    def test_get_trades_with_date_range(self, mock_request):
        """Test get_trades with date range parameters."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trades": [],
            "next_page_token": None
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_trades with date range
        result = client.get_trades(
            "AAPL",
            start="2024-01-01T09:30:00-05:00",
            end="2024-01-01T16:00:00-05:00",
            limit=50,
            feed="sip",
            sort="desc"
        )

        # Verify result structure
        assert result["count"] == 0
        assert result["symbol"] == "AAPL"
        assert result["feed"] == "sip"
        
        # Verify API call parameters
        call_args = mock_request.call_args
        params = call_args[1]["params"]
        assert params["start"] == "2024-01-01T09:30:00-05:00"
        assert params["end"] == "2024-01-01T16:00:00-05:00"
        assert params["limit"] == 50
        assert params["feed"] == "sip"
        assert params["sort"] == "desc"

    @patch('alpaca_data.client.requests.request')
    def test_get_trades_pagination(self, mock_request):
        """Test get_trades with pagination."""
        # Mock response with next page token
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trades": [
                {
                    "t": "2024-01-01T14:30:00Z",
                    "x": "XNAS",
                    "p": 150.25,
                    "s": 100
                }
            ],
            "next_page_token": "next_page_123"
        }
        mock_request.return_value = mock_response

        # Create client
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")

        # Call get_trades
        result = client.get_trades("AAPL")

        # Verify pagination info
        assert result["has_next_page"] is True
        assert result["next_page_token"] == "next_page_123"

    def test_trade_from_dict(self):
        """Test Trade.from_dict method."""
        trade_data = {
            "t": "2024-01-01T14:30:00Z",
            "x": "XNAS",
            "p": 150.25,
            "s": 100,
            "c": ["A", "B"],
            "i": "12345",
            "z": "C"
        }
        
        trade = Trade.from_dict("AAPL", trade_data)
        
        assert trade.symbol == "AAPL"
        assert trade.exchange == "XNAS"
        assert trade.price == 150.25
        assert trade.size == 100
        assert trade.conditions == ["A", "B"]
        assert trade.id == "12345"
        assert trade.tape == "C"

    def test_trade_from_dict_minimal(self):
        """Test Trade.from_dict with minimal data."""
        trade_data = {
            "t": "2024-01-01T14:30:00Z",
            "x": "XNAS",
            "p": 150.25,
            "s": 100
        }
        
        trade = Trade.from_dict("AAPL", trade_data)
        
        assert trade.symbol == "AAPL"
        assert trade.exchange == "XNAS"
        assert trade.price == 150.25
        assert trade.size == 100
        assert trade.conditions is None
        assert trade.id is None
        assert trade.tape is None