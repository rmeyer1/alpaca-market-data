"""Tests for options API methods."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from alpaca_data import AlpacaClient
from alpaca_data.models import Greeks, OptionQuote, OptionTrade, OptionSnapshot


class TestGetOptionQuotes:
    """Test cases for get_option_quotes method."""

    def test_get_option_quotes_single_symbol_success(self):
        """Test getting option quotes for a single symbol."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for single symbol
        mock_response_data = {
            "quotes": [
                {
                    "t": "2024-01-01T15:59:00Z",
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
                    }
                },
                {
                    "t": "2024-01-01T16:00:00Z",
                    "bp": 2.47,
                    "ap": 2.57,
                    "bs": 120,
                    "as": 180,
                    "bx": "BOX",
                    "ax": "BOX",
                    "iv": 0.290,
                    "oi": 1280,
                    "underlying_price": 150.30,
                    "greeks": {
                        "delta": 0.458,
                        "gamma": 0.0351,
                        "theta": -0.130,
                        "vega": 0.091,
                        "rho": 0.025,
                    }
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_quotes("AAPL230120C00150000", limit=2)
            
            assert "quotes" in result
            assert len(result["quotes"]) == 2
            assert result["symbol"] == "AAPL230120C00150000"
            assert result["count"] == 2
            
            # Check first quote
            quote1 = result["quotes"][0]
            assert isinstance(quote1, OptionQuote)
            assert quote1.symbol == "AAPL230120C00150000"
            assert quote1.bid_price == 2.45
            assert quote1.ask_price == 2.55
            assert quote1.bid_size == 100
            assert quote1.ask_size == 150
            assert quote1.iv == 0.285
            assert quote1.open_interest == 1250
            assert quote1.underlying_price == 150.25
            assert quote1.greeks is not None
            assert quote1.greeks.delta == 0.452
            assert quote1.greeks.gamma == 0.0345
            
            # Check second quote
            quote2 = result["quotes"][1]
            assert quote2.bid_price == 2.47
            assert quote2.greeks.delta == 0.458
            
            # Verify API call
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/quotes/AAPL230120C00150000",
                params={"limit": 2, "sort": "asc"}
            )

    def test_get_option_quotes_multiple_symbols_success(self):
        """Test getting option quotes for multiple symbols."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for multiple symbols
        mock_response_data = {
            "quotes": [
                {
                    "S": "AAPL230120C00150000",
                    "t": "2024-01-01T15:59:00Z",
                    "bp": 2.45,
                    "ap": 2.55,
                    "bs": 100,
                    "as": 150,
                    "bx": "BOX",
                    "ax": "BOX",
                    "greeks": {"delta": 0.452, "gamma": 0.0345, "theta": -0.125, "vega": 0.089, "rho": 0.023}
                },
                {
                    "S": "AAPL230120P00150000",
                    "t": "2024-01-01T15:59:00Z",
                    "bp": 1.85,
                    "ap": 1.95,
                    "bs": 80,
                    "as": 120,
                    "bx": "BOX",
                    "ax": "BOX",
                    "greeks": {"delta": -0.548, "gamma": 0.0289, "theta": -0.102, "vega": 0.085, "rho": -0.018}
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            symbols = ["AAPL230120C00150000", "AAPL230120P00150000"]
            result = client.get_option_quotes(symbols, limit=100)
            
            assert "quotes" in result
            assert len(result["quotes"]) == 2
            assert result["symbol"] == symbols
            assert result["count"] == 2
            
            # Check call symbol
            call_quote = result["quotes"][0]
            assert call_quote.symbol == "AAPL230120C00150000"
            assert call_quote.greeks.delta == 0.452
            
            # Check put symbol
            put_quote = result["quotes"][1]
            assert put_quote.symbol == "AAPL230120P00150000"
            assert put_quote.greeks.delta == -0.548
            
            # Verify API call for multiple symbols
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/quotes",
                params={
                    "symbols": "AAPL230120C00150000,AAPL230120P00150000",
                    "limit": 100,
                    "sort": "asc"
                }
            )

    def test_get_option_quotes_with_date_range(self):
        """Test getting option quotes with date range parameters."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"quotes": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_quotes(
                "AAPL230120C00150000",
                start="2024-01-01T09:30:00-05:00",
                end="2024-01-02T16:00:00-05:00",
                limit=50
            )
            
            # Verify API call with date parameters
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/quotes/AAPL230120C00150000",
                params={
                    "start": "2024-01-01T09:30:00-05:00",
                    "end": "2024-01-02T16:00:00-05:00",
                    "limit": 50,
                    "sort": "asc"
                }
            )

    def test_get_option_quotes_with_pagination(self):
        """Test getting option quotes with pagination token."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "quotes": [
                {
                    "t": "2024-01-01T16:00:00Z",
                    "bp": 2.50,
                    "ap": 2.60,
                    "bs": 100,
                    "as": 150,
                    "bx": "BOX",
                    "ax": "BOX",
                }
            ],
            "next_page_token": "next_page_token_value"
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_quotes(
                "AAPL230120C00150000",
                page_token="test_token",
                limit=100
            )
            
            assert result["has_next_page"] is True
            assert result["next_page_token"] == "next_page_token_value"
            assert len(result["quotes"]) == 1
            
            # Verify API call with pagination token
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/quotes/AAPL230120C00150000",
                params={
                    "page_token": "test_token",
                    "limit": 100,
                    "sort": "asc"
                }
            )

    def test_get_option_quotes_output_formats(self):
        """Test getting option quotes with different output formats."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "quotes": [
                {
                    "t": "2024-01-01T15:59:00Z",
                    "bp": 2.45,
                    "ap": 2.55,
                    "bs": 100,
                    "as": 150,
                    "bx": "BOX",
                    "ax": "BOX",
                    "greeks": {"delta": 0.452, "gamma": 0.0345, "theta": -0.125, "vega": 0.089, "rho": 0.023}
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            # Test JSON output
            result_json = client.get_option_quotes("AAPL230120C00150000", output_format="json")
            assert isinstance(result_json, str)
            
            # Test dict output (default)
            result_dict = client.get_option_quotes("AAPL230120C00150000", output_format="dict")
            assert isinstance(result_dict, dict)
            assert "quotes" in result_dict
            assert len(result_dict["quotes"]) == 1

    def test_get_option_quotes_empty_response(self):
        """Test getting option quotes when no quotes are available."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"quotes": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_quotes("AAPL230120C00150000")
            
            assert "quotes" in result
            assert len(result["quotes"]) == 0
            assert result["count"] == 0
            assert result["has_next_page"] is False


class TestGetOptionTrades:
    """Test cases for get_option_trades method."""

    def test_get_option_trades_single_symbol_success(self):
        """Test getting option trades for a single symbol."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for single symbol
        mock_response_data = {
            "trades": [
                {
                    "t": "2024-01-01T15:59:30Z",
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
                    }
                },
                {
                    "t": "2024-01-01T16:00:15Z",
                    "p": 2.52,
                    "s": 50,
                    "x": "BOX",
                    "c": "@",
                    "iv": 0.287,
                    "underlying_price": 150.28,
                    "greeks": {
                        "delta": 0.455,
                        "gamma": 0.0347,
                        "theta": -0.127,
                        "vega": 0.090,
                        "rho": 0.024,
                    }
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_trades("AAPL230120C00150000", limit=2)
            
            assert "trades" in result
            assert len(result["trades"]) == 2
            assert result["symbol"] == "AAPL230120C00150000"
            assert result["count"] == 2
            
            # Check first trade
            trade1 = result["trades"][0]
            assert isinstance(trade1, OptionTrade)
            assert trade1.symbol == "AAPL230120C00150000"
            assert trade1.price == 2.50
            assert trade1.size == 100
            assert trade1.exchange == "BOX"
            assert trade1.conditions == "@"
            assert trade1.iv == 0.285
            assert trade1.underlying_price == 150.25
            assert trade1.greeks is not None
            assert trade1.greeks.delta == 0.452
            
            # Check second trade
            trade2 = result["trades"][1]
            assert trade2.price == 2.52
            assert trade2.size == 50
            assert trade2.greeks.delta == 0.455
            
            # Verify API call
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/trades/AAPL230120C00150000",
                params={"limit": 2, "sort": "asc"}
            )

    def test_get_option_trades_multiple_symbols_success(self):
        """Test getting option trades for multiple symbols."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for multiple symbols
        mock_response_data = {
            "trades": [
                {
                    "S": "AAPL230120C00150000",
                    "t": "2024-01-01T15:59:30Z",
                    "p": 2.50,
                    "s": 100,
                    "x": "BOX",
                    "greeks": {"delta": 0.452, "gamma": 0.0345, "theta": -0.125, "vega": 0.089, "rho": 0.023}
                },
                {
                    "S": "AAPL230120P00150000",
                    "t": "2024-01-01T16:00:00Z",
                    "p": 1.90,
                    "s": 75,
                    "x": "BOX",
                    "greeks": {"delta": -0.548, "gamma": 0.0289, "theta": -0.102, "vega": 0.085, "rho": -0.018}
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            symbols = ["AAPL230120C00150000", "AAPL230120P00150000"]
            result = client.get_option_trades(symbols, limit=100)
            
            assert "trades" in result
            assert len(result["trades"]) == 2
            assert result["symbol"] == symbols
            assert result["count"] == 2
            
            # Check call trade
            call_trade = result["trades"][0]
            assert call_trade.symbol == "AAPL230120C00150000"
            assert call_trade.greeks.delta == 0.452
            
            # Check put trade
            put_trade = result["trades"][1]
            assert put_trade.symbol == "AAPL230120P00150000"
            assert put_trade.greeks.delta == -0.548
            
            # Verify API call for multiple symbols
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/trades",
                params={
                    "symbols": "AAPL230120C00150000,AAPL230120P00150000",
                    "limit": 100,
                    "sort": "asc"
                }
            )

    def test_get_option_trades_with_date_range(self):
        """Test getting option trades with date range parameters."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"trades": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_trades(
                "AAPL230120C00150000",
                start="2024-01-01T09:30:00-05:00",
                end="2024-01-02T16:00:00-05:00",
                limit=50
            )
            
            # Verify API call with date parameters
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/trades/AAPL230120C00150000",
                params={
                    "start": "2024-01-01T09:30:00-05:00",
                    "end": "2024-01-02T16:00:00-05:00",
                    "limit": 50,
                    "sort": "asc"
                }
            )

    def test_get_option_trades_with_pagination(self):
        """Test getting option trades with pagination token."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "trades": [
                {
                    "t": "2024-01-01T16:00:00Z",
                    "p": 2.50,
                    "s": 100,
                    "x": "BOX",
                }
            ],
            "next_page_token": "next_page_token_value"
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_trades(
                "AAPL230120C00150000",
                page_token="test_token",
                limit=100
            )
            
            assert result["has_next_page"] is True
            assert result["next_page_token"] == "next_page_token_value"
            assert len(result["trades"]) == 1

    def test_get_option_trades_output_formats(self):
        """Test getting option trades with different output formats."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "trades": [
                {
                    "t": "2024-01-01T15:59:30Z",
                    "p": 2.50,
                    "s": 100,
                    "x": "BOX",
                    "greeks": {"delta": 0.452, "gamma": 0.0345, "theta": -0.125, "vega": 0.089, "rho": 0.023}
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            # Test JSON output
            result_json = client.get_option_trades("AAPL230120C00150000", output_format="json")
            assert isinstance(result_json, str)
            
            # Test dict output (default)
            result_dict = client.get_option_trades("AAPL230120C00150000", output_format="dict")
            assert isinstance(result_dict, dict)
            assert "trades" in result_dict
            assert len(result_dict["trades"]) == 1

    def test_get_option_trades_empty_response(self):
        """Test getting option trades when no trades are available."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {"trades": []}
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_trades("AAPL230120C00150000")
            
            assert "trades" in result
            assert len(result["trades"]) == 0
            assert result["count"] == 0
            assert result["has_next_page"] is False


class TestGetOptionSnapshot:
    """Test cases for get_option_snapshot method."""

    def test_get_option_snapshot_single_symbol_success(self):
        """Test getting option snapshot for a single symbol."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for single symbol
        mock_response_data = {
            "snapshot": {
                "iv": 0.285,
                "oi": 1250,
                "underlying_price": 150.25,
                "latest_trade": {
                    "t": "2024-01-01T15:59:30Z",
                    "p": 2.50,
                    "s": 100,
                    "x": "BOX",
                    "c": "@",
                    "iv": 0.285,
                    "underlying_price": 150.25,
                },
                "latest_quote": {
                    "t": "2024-01-01T16:00:00Z",
                    "bp": 2.45,
                    "ap": 2.55,
                    "bs": 100,
                    "as": 150,
                    "bx": "BOX",
                    "ax": "BOX",
                    "iv": 0.285,
                    "oi": 1250,
                },
                "greeks": {
                    "delta": 0.452,
                    "gamma": 0.0345,
                    "theta": -0.125,
                    "vega": 0.089,
                    "rho": 0.023,
                },
                "minute_bar": {
                    "t": "2024-01-01T16:00:00Z",
                    "o": 2.40,
                    "h": 2.60,
                    "l": 2.35,
                    "c": 2.50,
                    "v": 1000.0,
                    "n": 50,
                    "vw": 2.48,
                },
                "daily_bar": {
                    "t": "2024-01-01T00:00:00Z",
                    "o": 2.20,
                    "h": 2.65,
                    "l": 2.15,
                    "c": 2.50,
                    "v": 15000.0,
                    "n": 750,
                    "vw": 2.35,
                }
            }
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_snapshot("AAPL230120C00150000")
            
            assert "snapshots" in result
            assert len(result["snapshots"]) == 1
            assert result["symbol"] == "AAPL230120C00150000"
            assert result["count"] == 1
            
            # Check snapshot
            snapshot = result["snapshots"][0]
            assert isinstance(snapshot, OptionSnapshot)
            assert snapshot.symbol == "AAPL230120C00150000"
            assert snapshot.iv == 0.285
            assert snapshot.open_interest == 1250
            assert snapshot.underlying_price == 150.25
            
            # Check latest trade
            assert snapshot.latest_trade is not None
            assert snapshot.latest_trade.price == 2.50
            assert snapshot.latest_trade.size == 100
            assert snapshot.latest_trade.exchange == "BOX"
            
            # Check latest quote
            assert snapshot.latest_quote is not None
            assert snapshot.latest_quote.bid_price == 2.45
            assert snapshot.latest_quote.ask_price == 2.55
            assert snapshot.latest_quote.bid_size == 100
            
            # Check Greeks
            assert snapshot.greeks is not None
            assert snapshot.greeks.delta == 0.452
            assert snapshot.greeks.gamma == 0.0345
            assert snapshot.greeks.theta == -0.125
            
            # Check bars
            assert snapshot.minute_bar is not None
            assert snapshot.minute_bar.close == 2.50
            assert snapshot.minute_bar.volume == 1000.0
            assert snapshot.daily_bar is not None
            assert snapshot.daily_bar.close == 2.50
            assert snapshot.daily_bar.volume == 15000.0
            
            # Verify API call
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/snapshots/AAPL230120C00150000",
                params={}
            )

    def test_get_option_snapshot_multiple_symbols_success(self):
        """Test getting option snapshots for multiple symbols."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response data for multiple symbols
        mock_response_data = {
            "snapshots": [
                {
                    "S": "AAPL230120C00150000",
                    "iv": 0.285,
                    "oi": 1250,
                    "latest_trade": {
                        "t": "2024-01-01T15:59:30Z",
                        "p": 2.50,
                        "s": 100,
                        "x": "BOX",
                    },
                    "greeks": {"delta": 0.452, "gamma": 0.0345, "theta": -0.125, "vega": 0.089, "rho": 0.023}
                },
                {
                    "S": "AAPL230120P00150000",
                    "iv": 0.292,
                    "oi": 980,
                    "latest_trade": {
                        "t": "2024-01-01T16:00:00Z",
                        "p": 1.90,
                        "s": 75,
                        "x": "BOX",
                    },
                    "greeks": {"delta": -0.548, "gamma": 0.0289, "theta": -0.102, "vega": 0.085, "rho": -0.018}
                }
            ]
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            symbols = ["AAPL230120C00150000", "AAPL230120P00150000"]
            result = client.get_option_snapshot(symbols)
            
            assert "snapshots" in result
            assert len(result["snapshots"]) == 2
            assert result["symbol"] == symbols
            assert result["count"] == 2
            
            # Check call snapshot
            call_snapshot = result["snapshots"][0]
            assert call_snapshot.symbol == "AAPL230120C00150000"
            assert call_snapshot.iv == 0.285
            assert call_snapshot.open_interest == 1250
            assert call_snapshot.greeks.delta == 0.452
            
            # Check put snapshot
            put_snapshot = result["snapshots"][1]
            assert put_snapshot.symbol == "AAPL230120P00150000"
            assert put_snapshot.iv == 0.292
            assert put_snapshot.open_interest == 980
            assert put_snapshot.greeks.delta == -0.548
            
            # Verify API call for multiple symbols
            mock_request.assert_called_once_with(
                "GET",
                "/v1beta1/options/snapshots",
                params={
                    "symbols": "AAPL230120C00150000,AAPL230120P00150000"
                }
            )

    def test_get_option_snapshot_minimal_data(self):
        """Test getting option snapshot with minimal data."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        # Mock response with minimal data
        mock_response_data = {
            "snapshot": {
                "latest_trade": {
                    "t": "2024-01-01T15:59:30Z",
                    "p": 2.50,
                    "s": 100,
                    "x": "BOX",
                }
            }
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = client.get_option_snapshot("AAPL230120C00150000")
            
            assert "snapshots" in result
            assert len(result["snapshots"]) == 1
            
            snapshot = result["snapshots"][0]
            assert snapshot.symbol == "AAPL230120C00150000"
            assert snapshot.iv is None
            assert snapshot.open_interest is None
            assert snapshot.greeks is None
            assert snapshot.latest_trade is not None
            assert snapshot.latest_quote is None
            assert snapshot.minute_bar is None
            assert snapshot.daily_bar is None

    def test_get_option_snapshot_output_formats(self):
        """Test getting option snapshots with different output formats."""
        client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        
        mock_response_data = {
            "snapshot": {
                "iv": 0.285,
                "latest_trade": {
                    "t": "2024-01-01T15:59:30Z",
                    "p": 2.50,
                    "s": 100,
                    "x": "BOX",
                },
                "greeks": {"delta": 0.452, "gamma": 0.0345, "theta": -0.125, "vega": 0.089, "rho": 0.023}
            }
        }
        
        with patch.object(client, '_make_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            # Test JSON output
            result_json = client.get_option_snapshot("AAPL230120C00150000", output_format="json")
            assert isinstance(result_json, str)
            
            # Test dict output (default)
            result_dict = client.get_option_snapshot("AAPL230120C00150000", output_format="dict")
            assert isinstance(result_dict, dict)
            assert "snapshots" in result_dict
            assert len(result_dict["snapshots"]) == 1