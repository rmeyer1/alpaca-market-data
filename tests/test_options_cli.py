"""Tests for options CLI scripts."""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, Mock
from typer.testing import CliRunner
from scripts.get_option_quotes import app as option_quotes_app
from scripts.get_option_trades import app as option_trades_app
from scripts.get_option_snapshot import app as option_snapshot_app


# Set up environment variables for CLI testing
os.environ["ALPACA_API_KEY"] = "test_api_key"
os.environ["ALPACA_API_SECRET"] = "test_api_secret"


class TestOptionCLIScripts(unittest.TestCase):
    """Test cases for options CLI scripts."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Mock response data for different option endpoints
        self.mock_option_quotes_response = {
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
            ],
            "symbol": "AAPL230120C00150000",
            "next_page_token": None,
            "count": 2,
            "has_next_page": False
        }
        
        self.mock_option_trades_response = {
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
            ],
            "symbol": "AAPL230120C00150000",
            "next_page_token": None,
            "count": 2,
            "has_next_page": False
        }
        
        self.mock_option_snapshot_response = {
            "snapshots": [
                {
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
            ],
            "symbol": "AAPL230120C00150000",
            "count": 1
        }

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_basic(self, mock_get_quotes):
        """Test basic option quotes CLI functionality."""
        mock_get_quotes.return_value = self.mock_option_quotes_response
        
        # Run the CLI command
        result = self.runner.invoke(option_quotes_app, [
            "AAPL230120C00150000",
            "--limit", "10"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0, f"Command failed with output: {result.output}")
        self.assertIn("AAPL230120C00150000", result.output)
        self.assertIn("Found 2 option quotes", result.output)
        
        # Verify the API was called with correct parameters
        mock_get_quotes.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            start=None,
            end=None,
            limit=10,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_multiple_symbols(self, mock_get_quotes):
        """Test option quotes CLI with multiple symbols."""
        mock_get_quotes.return_value = self.mock_option_quotes_response
        
        # Run the CLI command with multiple symbols
        result = self.runner.invoke(option_quotes_app, [
            "AAPL230120C00150000",
            "AAPL230120P00150000",
            "--limit", "5"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with multiple symbols
        mock_get_quotes.assert_called_once_with(
            symbols=["AAPL230120C00150000", "AAPL230120P00150000"],
            start=None,
            end=None,
            limit=5,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_with_date_range(self, mock_get_quotes):
        """Test option quotes CLI with date range."""
        mock_get_quotes.return_value = self.mock_option_quotes_response
        
        # Run the CLI command with date range
        result = self.runner.invoke(option_quotes_app, [
            "AAPL230120C00150000",
            "--start", "2024-01-01",
            "--end", "2024-01-02"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with date range
        mock_get_quotes.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            start="2024-01-01",
            end="2024-01-02",
            limit=100,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_json_output(self, mock_get_quotes):
        """Test option quotes CLI with JSON output."""
        mock_get_quotes.return_value = self.mock_option_quotes_response
        
        # Run the CLI command with JSON format
        result = self.runner.invoke(option_quotes_app, [
            "AAPL230120C00150000",
            "--format", "json"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with dict format (CLI converts json internally)
        mock_get_quotes.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            start=None,
            end=None,
            limit=100,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_verbose(self, mock_get_quotes):
        """Test option quotes CLI with verbose output."""
        mock_get_quotes.return_value = self.mock_option_quotes_response
        
        # Run the CLI command with verbose flag
        result = self.runner.invoke(option_quotes_app, [
            "AAPL230120C00150000",
            "--verbose"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_error_handling(self, mock_get_quotes):
        """Test option quotes CLI error handling."""
        mock_get_quotes.side_effect = Exception("API Error")
        
        # Run the CLI command
        result = self.runner.invoke(option_quotes_app, [
            "AAPL230120C00150000"
        ])
        
        # Verify the command failed gracefully
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error:", result.output)
        self.assertIn("API Error", result.output)

    @patch('alpaca_data.client.AlpacaClient.get_option_trades')
    def test_option_trades_basic(self, mock_get_trades):
        """Test basic option trades CLI functionality."""
        mock_get_trades.return_value = self.mock_option_trades_response
        
        # Run the CLI command
        result = self.runner.invoke(option_trades_app, [
            "AAPL230120C00150000",
            "--limit", "10"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0, f"Command failed with output: {result.output}")
        self.assertIn("AAPL230120C00150000", result.output)
        self.assertIn("Found 2 option trades", result.output)
        
        # Verify the API was called with correct parameters
        mock_get_trades.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            start=None,
            end=None,
            limit=10,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_trades')
    def test_option_trades_with_date_range(self, mock_get_trades):
        """Test option trades CLI with date range."""
        mock_get_trades.return_value = self.mock_option_trades_response
        
        # Run the CLI command with date range
        result = self.runner.invoke(option_trades_app, [
            "AAPL230120C00150000",
            "--start", "2024-01-01T09:30:00-05:00",
            "--end", "2024-01-02T16:00:00-05:00"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with date range
        mock_get_trades.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            start="2024-01-01T09:30:00-05:00",
            end="2024-01-02T16:00:00-05:00",
            limit=100,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_trades')
    def test_option_trades_csv_output(self, mock_get_trades):
        """Test option trades CLI with CSV output."""
        mock_get_trades.return_value = self.mock_option_trades_response
        
        # Run the CLI command with CSV format
        result = self.runner.invoke(option_trades_app, [
            "AAPL230120C00150000",
            "--format", "csv"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with dict format (CSV is formatted client-side)
        mock_get_trades.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            start=None,
            end=None,
            limit=100,
            sort="asc",
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_snapshot')
    def test_option_snapshot_basic(self, mock_get_snapshot):
        """Test basic option snapshot CLI functionality."""
        mock_get_snapshot.return_value = self.mock_option_snapshot_response
        
        # Run the CLI command
        result = self.runner.invoke(option_snapshot_app, [
            "AAPL230120C00150000"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        self.assertIn("AAPL230120C00150000", result.output)
        self.assertIn("Found 1 option snapshots", result.output)
        
        # Verify the API was called with correct parameters
        mock_get_snapshot.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_snapshot')
    def test_option_snapshot_multiple_symbols(self, mock_get_snapshot):
        """Test option snapshot CLI with multiple symbols."""
        mock_get_snapshot.return_value = self.mock_option_snapshot_response
        
        # Run the CLI command with multiple symbols
        result = self.runner.invoke(option_snapshot_app, [
            "AAPL230120C00150000",
            "AAPL230120P00150000"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with multiple symbols
        mock_get_snapshot.assert_called_once_with(
            symbols=["AAPL230120C00150000", "AAPL230120P00150000"],
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_snapshot')
    def test_option_snapshot_json_output(self, mock_get_snapshot):
        """Test option snapshot CLI with JSON output."""
        mock_get_snapshot.return_value = self.mock_option_snapshot_response
        
        # Run the CLI command with JSON format
        result = self.runner.invoke(option_snapshot_app, [
            "AAPL230120C00150000",
            "--format", "json"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        
        # Verify the API was called with dict format (CLI handles format conversion)
        mock_get_snapshot.assert_called_once_with(
            symbols=["AAPL230120C00150000"],
            output_format="dict"
        )

    @patch('alpaca_data.client.AlpacaClient.get_option_snapshot')
    def test_option_snapshot_verbose(self, mock_get_snapshot):
        """Test option snapshot CLI with verbose output."""
        mock_get_snapshot.return_value = self.mock_option_snapshot_response
        
        # Run the CLI command with verbose flag
        result = self.runner.invoke(option_snapshot_app, [
            "AAPL230120C00150000",
            "--verbose"
        ])
        
        # Verify the command succeeded
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Metadata:", result.output)

    @patch('alpaca_data.client.AlpacaClient.get_option_snapshot')
    def test_option_snapshot_error_handling(self, mock_get_snapshot):
        """Test option snapshot CLI error handling."""
        mock_get_snapshot.side_effect = Exception("API Error")
        
        # Run the CLI command
        result = self.runner.invoke(option_snapshot_app, [
            "AAPL230120C00150000"
        ])
        
        # Verify the command failed gracefully
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error: API Error", result.output)

    def test_option_quotes_help(self):
        """Test option quotes CLI help message."""
        result = self.runner.invoke(option_quotes_app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Fetch option quotes with greeks data from Alpaca Market Data API", result.output)
        self.assertIn("AAPL220121C00150000", result.output)
        self.assertIn("--start", result.output)
        self.assertIn("--end", result.output)
        self.assertIn("--limit", result.output)
        self.assertIn("--format", result.output)

    def test_option_trades_help(self):
        """Test option trades CLI help message."""
        result = self.runner.invoke(option_trades_app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Fetch option trades with greeks data from Alpaca Market Data API", result.output)
        self.assertIn("AAPL220121C00150000", result.output)

    def test_option_snapshot_help(self):
        """Test option snapshot CLI help message."""
        result = self.runner.invoke(option_snapshot_app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Fetch option snapshots with greeks, implied volatility, and open interest", result.output)
        self.assertIn("AAPL220121C00150000", result.output)

    @patch('alpaca_data.client.AlpacaClient.get_option_quotes')
    def test_option_quotes_output_formats(self, mock_get_quotes):
        """Test option quotes CLI with different output formats."""
        mock_get_quotes.return_value = self.mock_option_quotes_response
        
        # Test table format (default)
        result = self.runner.invoke(option_quotes_app, ["AAPL230120C00150000"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Symbol", result.output)
        self.assertIn("Price", result.output)
        
        # Test JSON format
        result = self.runner.invoke(option_quotes_app, ["AAPL230120C00150000", "--format", "json"])
        self.assertEqual(result.exit_code, 0)
        
        # Test CSV format
        result = self.runner.invoke(option_quotes_app, ["AAPL230120C00150000", "--format", "csv"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Symbol,Timestamp,Bid Price", result.output)

    @patch('alpaca_data.client.AlpacaClient.get_option_trades')
    def test_option_trades_output_formats(self, mock_get_trades):
        """Test option trades CLI with different output formats."""
        mock_get_trades.return_value = self.mock_option_trades_response
        
        # Test table format (default)
        result = self.runner.invoke(option_trades_app, ["AAPL230120C00150000"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Symbol", result.output)
        self.assertIn("Trade", result.output)
        
        # Test JSON format
        result = self.runner.invoke(option_trades_app, ["AAPL230120C00150000", "--format", "json"])
        self.assertEqual(result.exit_code, 0)
        
        # Test CSV format
        result = self.runner.invoke(option_trades_app, ["AAPL230120C00150000", "--format", "csv"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Symbol,Timestamp,Price", result.output)

    @patch('alpaca_data.client.AlpacaClient.get_option_snapshot')
    def test_option_snapshot_output_formats(self, mock_get_snapshot):
        """Test option snapshot CLI with different output formats."""
        mock_get_snapshot.return_value = self.mock_option_snapshot_response
        
        # Test table format (default)
        result = self.runner.invoke(option_snapshot_app, ["AAPL230120C00150000"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Symbol", result.output)
        self.assertIn("Type", result.output)
        
        # Test JSON format
        result = self.runner.invoke(option_snapshot_app, ["AAPL230120C00150000", "--format", "json"])
        self.assertEqual(result.exit_code, 0)
        
        # Test CSV format
        result = self.runner.invoke(option_snapshot_app, ["AAPL230120C00150000", "--format", "csv"])
        self.assertEqual(result.exit_code, 0)
        # CSV should contain CSV header
        self.assertIn("Symbol,Type,Strike", result.output)
        self.assertIn("Symbol,Type,Strike", result.output)


if __name__ == '__main__':
    unittest.main()