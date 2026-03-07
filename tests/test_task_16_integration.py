"""Integration test for TASK-16: Client endpoints with output formatters."""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from src.alpaca_data.client import AlpacaClient
from src.alpaca_data.models import Bar, Quote, Trade


class TestClientWithFormatters(unittest.TestCase):
    """Test that client endpoints work with output formatters."""

    def setUp(self):
        """Set up test client with mock API."""
        self.client = AlpacaClient(api_key="test_key", secret_key="test_secret")
        self.mock_response = Mock()
        self.mock_response.json.return_value = {
            "bars": [
                {
                    "t": "2024-01-01T00:00:00Z",
                    "o": 150.0,
                    "h": 155.0,
                    "l": 149.0,
                    "c": 153.0,
                    "v": 1000000,
                    "n": 5000
                }
            ],
            "symbol": "AAPL",
            "next_page_token": None
        }

    @patch('requests.request')
    def test_get_bars_json_format(self, mock_request):
        """Test get_bars with JSON output format."""
        mock_request.return_value = self.mock_response
        
        # Test JSON format
        result = self.client.get_bars("AAPL", output_format="json")
        self.assertIsInstance(result, str)
        
        # Should be valid JSON
        import json
        parsed = json.loads(result)
        self.assertIn("bars", parsed)
        self.assertIn("symbol", parsed)

    @patch('requests.request')
    def test_get_bars_csv_format(self, mock_request):
        """Test get_bars with CSV output format."""
        mock_request.return_value = self.mock_response
        
        # Test CSV format
        result = self.client.get_bars("AAPL", output_format="csv")
        self.assertIsInstance(result, str)
        
        # Should contain CSV content
        self.assertIn("symbol", result)
        self.assertIn("AAPL", result)

    @patch('requests.request')
    def test_get_bars_dataframe_format(self, mock_request):
        """Test get_bars with DataFrame output format."""
        mock_request.return_value = self.mock_response
        
        try:
            # Test DataFrame format
            result = self.client.get_bars("AAPL", output_format="dataframe")
            self.assertIsNotNone(result)
            
            import pandas as pd
            self.assertIsInstance(result, pd.DataFrame)
            self.assertIn("symbol", result.columns)
            
        except ImportError:
            self.skipTest("pandas not available")

    @patch('requests.request')
    def test_get_bars_dict_format(self, mock_request):
        """Test get_bars with dict output format (default)."""
        mock_request.return_value = self.mock_response
        
        # Test dict format (default)
        result = self.client.get_bars("AAPL", output_format="dict")
        self.assertIsInstance(result, dict)
        self.assertIn("bars", result)
        self.assertIn("symbol", result)

    @patch('requests.request')
    def test_get_quotes_with_format(self, mock_request):
        """Test get_quotes with output formatting."""
        quotes_response = Mock()
        quotes_response.json.return_value = {
            "quotes": [
                {
                    "t": "2024-01-01T00:00:00Z",
                    "ap": 153.5,
                    "as": 100,
                    "bp": 153.0,
                    "bs": 200,
                    "ax": "XNAS",
                    "bx": "XNAS"
                }
            ],
            "symbol": "AAPL",
            "next_page_token": None
        }
        mock_request.return_value = quotes_response
        
        # Test JSON format
        result = self.client.get_quotes("AAPL", output_format="json")
        self.assertIsInstance(result, str)
        
        import json
        parsed = json.loads(result)
        self.assertIn("quotes", parsed)

    @patch('requests.request')
    def test_get_trades_with_format(self, mock_request):
        """Test get_trades with output formatting."""
        trades_response = Mock()
        trades_response.json.return_value = {
            "trades": [
                {
                    "t": "2024-01-01T00:00:00Z",
                    "p": 153.0,
                    "s": 100,
                    "x": "XNAS"
                }
            ],
            "symbol": "AAPL",
            "next_page_token": None
        }
        mock_request.return_value = trades_response
        
        # Test CSV format
        result = self.client.get_trades("AAPL", output_format="csv")
        self.assertIsInstance(result, str)
        self.assertIn("symbol", result)

    @patch('requests.request')
    def test_get_news_with_format(self, mock_request):
        """Test get_news with output formatting."""
        news_response = Mock()
        news_response.json.return_value = {
            "news": [
                {
                    "id": "123",
                    "headline": "Test News",
                    "created_at": "2024-01-01T00:00:00Z",
                    "symbols": ["AAPL"],
                    "source": "Test Source"
                }
            ],
            "next_page_token": None
        }
        mock_request.return_value = news_response
        
        # Test JSON format
        result = self.client.get_news(output_format="json")
        self.assertIsInstance(result, str)
        
        import json
        parsed = json.loads(result)
        self.assertIn("news", parsed)

    @patch('requests.request')
    def test_crypto_endpoints_with_format(self, mock_request):
        """Test crypto endpoints with output formatting."""
        crypto_response = Mock()
        crypto_response.json.return_value = {
            "bars": [
                {
                    "t": "2024-01-01T00:00:00Z",
                    "o": 50000.0,
                    "h": 51000.0,
                    "l": 49000.0,
                    "c": 50500.0,
                    "v": 100.5
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None
        }
        mock_request.return_value = crypto_response
        
        # Test crypto bars with JSON format
        result = self.client.get_crypto_bars("BTC/USD", output_format="json")
        self.assertIsInstance(result, str)
        
        import json
        parsed = json.loads(result)
        self.assertIn("bars", parsed)

    def test_unsupported_format(self):
        """Test handling of unsupported output formats."""
        with patch('requests.request') as mock_request:
            mock_request.return_value = self.mock_response
            
            # Should raise ValueError for unsupported format
            with self.assertRaises(ValueError):
                self.client.get_bars("AAPL", output_format="unsupported_format")

    def test_formatting_helper_method(self):
        """Test the _apply_formatting helper method."""
        test_data = {"test": "data", "items": [1, 2, 3]}
        
        # Test dict format
        result = self.client._apply_formatting(test_data, "dict")
        self.assertEqual(result, test_data)
        
        # Test JSON format
        result = self.client._apply_formatting(test_data, "json")
        self.assertIsInstance(result, str)
        
        # Test CSV format - use proper API response structure with 'bars' field
        csv_data = {"bars": [test_data], "next_page_token": None}
        result = self.client._apply_formatting(csv_data, "csv")
        self.assertIsInstance(result, str)
        self.assertIn("test", result)

    def test_convenience_functions_integration(self):
        """Test that convenience functions work with models."""
        from src.alpaca_data.formatters import to_json, to_csv
        
        bar = Bar(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=150.0,
            high=155.0,
            low=149.0,
            close=153.0,
            volume=1000000
        )
        
        # Test convenience functions
        json_result = to_json(bar)
        self.assertIsInstance(json_result, str)
        
        csv_result = to_csv([bar])
        self.assertIsInstance(csv_result, str)
        self.assertIn("symbol", csv_result)


if __name__ == '__main__':
    unittest.main()