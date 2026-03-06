"""Tests for get_quotes functionality."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from alpaca_data import AlpacaClient
from alpaca_data.models import Quote


class TestGetQuotes:
    """Test cases for get_quotes method."""

    def test_get_quotes_single_symbol_success(self):
        """Test getting quotes for a single symbol."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data
        mock_response_data = {
            "quotes": [
                {
                    "t": "2024-01-01T15:59:00Z",
                    "ax": "Q",
                    "ap": 151.75,
                    "as": 1000.0,
                    "bx": "D",
                    "bp": 151.70,
                    "bs": 800.0,
                    "c": ["A"],
                    "z": "A"
                },
                {
                    "t": "2024-01-01T16:00:00Z",
                    "ax": "Q",
                    "ap": 151.80,
                    "as": 1200.0,
                    "bx": "D",
                    "bp": 151.75,
                    "bs": 900.0,
                    "c": ["A"],
                    "z": "A"
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_quotes("AAPL", limit=2)
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                "GET",
                "/v2/stocks/AAPL/quotes",
                params={
                    "limit": 2,
                    "feed": "iex",
                    "sort": "asc"
                }
            )
            
            # Verify the response structure
            assert "quotes" in result
            assert len(result["quotes"]) == 2
            assert result["symbol"] == "AAPL"
            assert result["feed"] == "iex"
            assert result["count"] == 2
            assert result["has_next_page"] is False
            
            # Verify quote objects
            quote1, quote2 = result["quotes"]
            assert isinstance(quote1, Quote)
            assert quote1.symbol == "AAPL"
            assert quote1.ask_exchange == "Q"
            assert quote1.ask_price == 151.75
            assert quote1.ask_size == 1000.0
            assert quote1.bid_exchange == "D"
            assert quote1.bid_price == 151.70
            assert quote1.bid_size == 800.0
            assert quote1.conditions == ["A"]
            assert quote1.tape == "A"

    def test_get_quotes_multiple_symbols_success(self):
        """Test getting quotes for multiple symbols."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for multiple symbols
        mock_response_data = {
            "quotes": [
                {
                    "S": "AAPL",
                    "t": "2024-01-01T16:00:00Z",
                    "ax": "Q",
                    "ap": 151.75,
                    "as": 1000.0,
                    "bx": "D",
                    "bp": 151.70,
                    "bs": 800.0
                },
                {
                    "S": "GOOGL", 
                    "t": "2024-01-01T16:00:00Z",
                    "ax": "P",
                    "ap": 2815.50,
                    "as": 500.0,
                    "bx": "M",
                    "bp": 2815.25,
                    "bs": 400.0
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_quotes(["AAPL", "GOOGL"])
            
            # Verify the request was made correctly
            mock_request.assert_called_once_with(
                "GET",
                "/v2/stocks/quotes",
                params={
                    "symbols": "AAPL,GOOGL",
                    "limit": 1000,
                    "feed": "iex",
                    "sort": "asc"
                }
            )
            
            # Verify the response structure
            assert len(result["quotes"]) == 2
            assert result["symbol"] == ["AAPL", "GOOGL"]
            
            # Verify quote objects
            quote1, quote2 = result["quotes"]
            assert quote1.symbol == "AAPL"
            assert quote1.ask_price == 151.75
            assert quote2.symbol == "GOOGL"
            assert quote2.ask_price == 2815.50

    def test_get_quotes_with_date_range(self):
        """Test getting quotes with start and end dates."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"quotes": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            client.get_quotes(
                "AAPL",
                start="2024-01-01T09:30:00-05:00",
                end="2024-01-01T16:00:00-05:00"
            )
            
            # Verify date range parameters were included
            params = mock_request.call_args[1]["params"]
            assert params["start"] == "2024-01-01T09:30:00-05:00"
            assert params["end"] == "2024-01-01T16:00:00-05:00"

    def test_get_quotes_with_pagination(self):
        """Test getting quotes with pagination token."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "quotes": [
                {
                    "t": "2024-01-01T16:01:00Z",
                    "ax": "Q",
                    "ap": 151.85,
                    "as": 1100.0,
                    "bx": "D",
                    "bp": 151.80,
                    "bs": 850.0
                }
            ],
            "next_page_token": "pagination_token_456"
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_quotes("AAPL", page_token="next_page_token")
            
            # Verify pagination parameters
            params = mock_request.call_args[1]["params"]
            assert params["page_token"] == "next_page_token"
            
            # Verify pagination response
            assert result["has_next_page"] is True
            assert result["next_page_token"] == "pagination_token_456"
            assert len(result["quotes"]) == 1

    def test_get_quotes_with_custom_parameters(self):
        """Test getting quotes with custom parameters."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"quotes": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            client.get_quotes(
                "AAPL",
                limit=50,
                feed="sip",
                sort="desc"
            )
            
            # Verify custom parameters
            params = mock_request.call_args[1]["params"]
            assert params["limit"] == 50
            assert params["feed"] == "sip"
            assert params["sort"] == "desc"

    def test_get_quotes_empty_response(self):
        """Test getting quotes with empty response."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"quotes": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_quotes("AAPL")
            
            # Verify empty response
            assert len(result["quotes"]) == 0
            assert result["count"] == 0
            assert result["has_next_page"] is False

    def test_get_quotes_error_handling(self):
        """Test error handling in get_quotes."""
        from alpaca_data.exceptions import AlpacaAPIError
        
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Test API error propagation
        with patch.object(client, '_make_request') as mock_request:
            mock_request.side_effect = AlpacaAPIError("API Error", 500)
            
            with pytest.raises(AlpacaAPIError) as exc_info:
                client.get_quotes("AAPL")
            
            assert "API Error" in str(exc_info.value)
            assert exc_info.value.status_code == 500