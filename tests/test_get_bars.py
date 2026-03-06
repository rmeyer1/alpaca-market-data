"""Tests for get_bars functionality."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from alpaca_data import AlpacaClient
from alpaca_data.models import Bar


class TestGetBars:
    """Test cases for get_bars method."""

    def test_get_bars_single_symbol_success(self):
        """Test getting bars for a single symbol."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data
        mock_response_data = {
            "bars": [
                {
                    "t": "2024-01-01T16:00:00Z",
                    "o": 150.25,
                    "h": 152.00,
                    "l": 149.50,
                    "c": 151.75,
                    "v": 1000000,
                    "n": 500,
                    "vw": 150.95
                },
                {
                    "t": "2024-01-02T16:00:00Z",
                    "o": 151.75,
                    "h": 153.25,
                    "l": 151.00,
                    "c": 152.50,
                    "v": 1200000,
                    "n": 600,
                    "vw": 152.10
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_bars("AAPL", timeframe="1Day", limit=2)
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                "GET",
                "/v2/stocks/AAPL/bars",
                params={
                    "timeframe": "1Day",
                    "limit": 2,
                    "adjustment": "all",
                    "sort": "asc"
                }
            )
            
            # Verify the response structure
            assert "bars" in result
            assert len(result["bars"]) == 2
            assert result["symbol"] == "AAPL"
            assert result["timeframe"] == "1Day"
            assert result["count"] == 2
            assert result["has_next_page"] is False
            
            # Verify bar objects
            bar1, bar2 = result["bars"]
            assert isinstance(bar1, Bar)
            assert bar1.symbol == "AAPL"
            assert bar1.open == 150.25
            assert bar1.high == 152.00
            assert bar1.low == 149.50
            assert bar1.close == 151.75
            assert bar1.volume == 1000000
            assert bar1.trade_count == 500
            assert bar1.vwap == 150.95

    def test_get_bars_multiple_symbols_success(self):
        """Test getting bars for multiple symbols."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for multiple symbols
        mock_response_data = {
            "bars": [
                {
                    "S": "AAPL",
                    "t": "2024-01-01T16:00:00Z",
                    "o": 150.25,
                    "h": 152.00,
                    "l": 149.50,
                    "c": 151.75,
                    "v": 1000000
                },
                {
                    "S": "GOOGL", 
                    "t": "2024-01-01T16:00:00Z",
                    "o": 2800.50,
                    "h": 2825.00,
                    "l": 2795.25,
                    "c": 2815.75,
                    "v": 500000
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_bars(["AAPL", "GOOGL"], timeframe="1Day")
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                "GET",
                "/v2/stocks/bars",
                params={
                    "symbols": "AAPL,GOOGL",
                    "timeframe": "1Day",
                    "limit": 1000,
                    "adjustment": "all",
                    "sort": "asc"
                }
            )
            
            # Verify the response structure
            assert len(result["bars"]) == 2
            assert result["symbol"] == ["AAPL", "GOOGL"]
            
            # Verify bar objects
            bar1, bar2 = result["bars"]
            assert bar1.symbol == "AAPL"
            assert bar1.close == 151.75
            assert bar2.symbol == "GOOGL"
            assert bar2.close == 2815.75

    def test_get_bars_with_date_range(self):
        """Test getting bars with start and end dates."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"bars": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            client.get_bars(
                "AAPL", 
                timeframe="1Hour",
                start="2024-01-01T09:30:00-05:00",
                end="2024-01-05T16:00:00-05:00"
            )
            
            # Verify date range parameters were included
            params = mock_request.call_args[1]["params"]
            assert params["start"] == "2024-01-01T09:30:00-05:00"
            assert params["end"] == "2024-01-05T16:00:00-05:00"
            assert params["timeframe"] == "1Hour"

    def test_get_bars_with_pagination(self):
        """Test getting bars with pagination token."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "bars": [
                {
                    "t": "2024-01-03T16:00:00Z",
                    "o": 153.00,
                    "h": 154.50,
                    "l": 152.75,
                    "c": 154.00,
                    "v": 800000
                }
            ],
            "next_page_token": "pagination_token_123"
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_bars("AAPL", page_token="next_page_token")
            
            # Verify pagination parameters
            params = mock_request.call_args[1]["params"]
            assert params["page_token"] == "next_page_token"
            
            # Verify pagination response
            assert result["has_next_page"] is True
            assert result["next_page_token"] == "pagination_token_123"
            assert len(result["bars"]) == 1

    def test_get_bars_with_custom_parameters(self):
        """Test getting bars with custom parameters."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"bars": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            client.get_bars(
                "AAPL",
                timeframe="1Week",
                limit=50,
                adjustment="splits_only",
                sort="desc"
            )
            
            # Verify custom parameters
            params = mock_request.call_args[1]["params"]
            assert params["timeframe"] == "1Week"
            assert params["limit"] == 50
            assert params["adjustment"] == "splits_only"
            assert params["sort"] == "desc"

    def test_get_bars_empty_response(self):
        """Test getting bars with empty response."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"bars": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_bars("AAPL")
            
            # Verify empty response
            assert len(result["bars"]) == 0
            assert result["count"] == 0
            assert result["has_next_page"] is False

    def test_get_bars_error_handling(self):
        """Test error handling in get_bars."""
        from alpaca_data.exceptions import AlpacaAPIError
        
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Test API error propagation
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = AlpacaAPIError("API Error", 500)
            
            with pytest.raises(AlpacaAPIError) as exc_info:
                client.get_bars("AAPL")
            
            assert "API Error" in str(exc_info.value)
            assert exc_info.value.status_code == 500