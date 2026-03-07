"""Tests for TASK-17: CLI Scripts (Tasks 17-21)"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, Mock
from typer.testing import CliRunner
from scripts.get_bars import app as bars_app
from scripts.get_quotes import app as quotes_app
from scripts.get_news import app as news_app
from scripts.get_snapshot import app as snapshot_app
from scripts.get_trades import app as trades_app
from scripts.crypto_cli import app as crypto_app


class TestCLIScripts(unittest.TestCase):
    """Test cases for CLI scripts."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
        
        # Mock response data for different endpoints
        self.mock_bars_response = {
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
            "timeframe": "1Day",
            "next_page_token": None,
            "count": 1,
            "has_next_page": False
        }
        
        self.mock_quotes_response = {
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
            "feed": "iex",
            "next_page_token": None,
            "count": 1,
            "has_next_page": False
        }
        
        self.mock_trades_response = {
            "trades": [
                {
                    "t": "2024-01-01T00:00:00Z",
                    "p": 153.0,
                    "s": 100,
                    "x": "XNAS"
                }
            ],
            "symbol": "AAPL",
            "feed": "iex",
            "next_page_token": None,
            "count": 1,
            "has_next_page": False
        }
        
        self.mock_news_response = {
            "news": [
                {
                    "id": "123",
                    "headline": "Test News Headline",
                    "created_at": "2024-01-01T00:00:00Z",
                    "symbols": ["AAPL"],
                    "source": "Test Source",
                    "summary": "Test summary"
                }
            ],
            "next_page_token": None,
            "count": 1,
            "has_next_page": False
        }
        
        self.mock_snapshot_response = {
            "snapshots": [
                {
                    "symbol": "AAPL",
                    "latest_trade": {
                        "t": "2024-01-01T00:00:00Z",
                        "p": 153.0,
                        "s": 100,
                        "x": "XNAS"
                    },
                    "latest_quote": {
                        "t": "2024-01-01T00:00:00Z",
                        "ap": 153.5,
                        "as": 100,
                        "bp": 153.0,
                        "bs": 200,
                        "ax": "XNAS",
                        "bx": "XNAS"
                    },
                    "daily_bar": {
                        "t": "2024-01-01T00:00:00Z",
                        "o": 150.0,
                        "h": 155.0,
                        "l": 149.0,
                        "c": 153.0,
                        "v": 1000000,
                        "n": 5000
                    }
                }
            ],
            "symbol": ["AAPL"],
            "count": 1
        }

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_bars_basic(self, mock_client):
        """Test basic get_bars command."""
        mock_instance = Mock()
        mock_instance.get_bars.return_value = self.mock_bars_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('📊 Got 1 bars for AAPL', result.output)
        self.assertIn('Timeframe: 1Day', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_bars_json_format(self, mock_client):
        """Test get_bars with JSON format."""
        mock_instance = Mock()
        mock_json_response = '{"bars": [], "count": 0}'
        mock_instance.get_bars.return_value = mock_json_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL', '--format', 'json'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('"bars": []', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_bars_csv_format(self, mock_client):
        """Test get_bars with CSV format."""
        mock_instance = Mock()
        mock_csv_response = 'symbol,timestamp,open,high,low,close,volume\nAAPL,2024-01-01T00:00:00Z,150.0,155.0,149.0,153.0,1000000\n'
        mock_instance.get_bars.return_value = mock_csv_response
        mock_client.return_value = mock_instance
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_filename = tmp.name
        
        try:
            result = self.runner.invoke(bars_app, ['AAPL', '--format', 'csv', '--output-file', tmp_filename])
            
            self.assertEqual(result.exit_code, 0)
            self.assertIn('✅ CSV written to', result.output)
            
            # Check file was created and has content
            self.assertTrue(os.path.exists(tmp_filename))
            with open(tmp_filename, 'r') as f:
                content = f.read()
                self.assertIn('symbol', content)
                self.assertIn('AAPL', content)
        finally:
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_bars_multiple_symbols(self, mock_client):
        """Test get_bars with multiple symbols."""
        mock_instance = Mock()
        mock_instance.get_bars.return_value = self.mock_bars_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL', 'GOOGL', 'MSFT'])
        
        self.assertEqual(result.exit_code, 0)
        mock_instance.get_bars.assert_called_once()
        
        # Check that it was called with list of symbols
        call_args = mock_instance.get_bars.call_args
        self.assertEqual(call_args.kwargs['symbols'], ['AAPL', 'GOOGL', 'MSFT'])

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_quotes_basic(self, mock_client):
        """Test basic get_quotes command."""
        mock_instance = Mock()
        mock_instance.get_quotes.return_value = self.mock_quotes_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(quotes_app, ['AAPL'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('📊 Got 1 quotes for AAPL', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_news_basic(self, mock_client):
        """Test basic get_news command."""
        mock_instance = Mock()
        mock_instance.get_news.return_value = self.mock_news_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(news_app, ['AAPL'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('📰 Got 1 news articles', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_news_no_symbols(self, mock_client):
        """Test get_news without specific symbols."""
        mock_instance = Mock()
        mock_instance.get_news.return_value = self.mock_news_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(news_app, [])
        
        self.assertEqual(result.exit_code, 0)
        mock_instance.get_news.assert_called_once()
        
        # Check that symbols was None or empty list
        call_args = mock_instance.get_news.call_args
        self.assertIsNone(call_args.kwargs['symbols'])

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_news_with_content(self, mock_client):
        """Test get_news with include content flag."""
        mock_instance = Mock()
        mock_instance.get_news.return_value = self.mock_news_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(news_app, ['AAPL', '--include-content'])
        
        self.assertEqual(result.exit_code, 0)
        call_args = mock_instance.get_news.call_args
        self.assertTrue(call_args.kwargs['include_content'])

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_snapshot_basic(self, mock_client):
        """Test basic get_snapshot command."""
        mock_instance = Mock()
        mock_instance.get_snapshot.return_value = self.mock_snapshot_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(snapshot_app, ['AAPL'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('📊 Got 1 snapshots', result.output)
        self.assertIn('Market snapshots:', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_get_trades_basic(self, mock_client):
        """Test basic get_trades command."""
        mock_instance = Mock()
        mock_instance.get_trades.return_value = self.mock_trades_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(trades_app, ['AAPL'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('📊 Got 1 trades for AAPL', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_crypto_bars(self, mock_client):
        """Test crypto bars command."""
        mock_instance = Mock()
        mock_crypto_bars_response = {
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
            "timeframe": "1Day",
            "next_page_token": None,
            "count": 1
        }
        mock_instance.get_crypto_bars.return_value = mock_crypto_bars_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(crypto_app, ['bars', 'BTC/USD'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('💰 Got 1 crypto bars', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_crypto_quotes(self, mock_client):
        """Test crypto quotes command."""
        mock_instance = Mock()
        mock_crypto_quotes_response = {
            "quotes": [
                {
                    "t": "2024-01-01T00:00:00Z",
                    "ap": 50500.0,
                    "as": 2.0,
                    "bp": 50490.0,
                    "bs": 1.5,
                    "ax": "CBSE",
                    "bx": "CBSE"
                }
            ],
            "symbol": "BTC/USD",
            "next_page_token": None,
            "count": 1
        }
        mock_instance.get_crypto_quotes.return_value = mock_crypto_quotes_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(crypto_app, ['quotes', 'BTC/USD'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('💰 Got 1 crypto quotes', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_crypto_snapshot(self, mock_client):
        """Test crypto snapshot command."""
        mock_instance = Mock()
        mock_crypto_snapshot_response = {
            "snapshots": [
                {
                    "symbol": "BTC/USD",
                    "latest_trade": {
                        "t": "2024-01-01T00:00:00Z",
                        "p": 50500.0,
                        "s": 1.0,
                        "x": "CBSE"
                    },
                    "latest_quote": {
                        "t": "2024-01-01T00:00:00Z",
                        "ap": 50500.0,
                        "as": 2.0,
                        "bp": 50490.0,
                        "bs": 1.5,
                        "ax": "CBSE",
                        "bx": "CBSE"
                    }
                }
            ],
            "symbol": ["BTC/USD"],
            "count": 1
        }
        mock_instance.get_crypto_snapshot.return_value = mock_crypto_snapshot_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(crypto_app, ['snapshot', 'BTC/USD'])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn('💰 Got 1 crypto snapshots', result.output)

    def test_cli_help_commands(self):
        """Test that CLI commands show proper help."""
        # Test bars help
        result = self.runner.invoke(bars_app, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get historical OHLCV bars', result.output)
        
        # Test quotes help
        result = self.runner.invoke(quotes_app, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get NBBO quotes', result.output)
        
        # Test news help
        result = self.runner.invoke(news_app, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get news articles', result.output)
        
        # Test snapshot help
        result = self.runner.invoke(snapshot_app, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get market snapshots', result.output)
        
        # Test trades help
        result = self.runner.invoke(trades_app, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get trade data', result.output)
        
        # Test crypto help
        result = self.runner.invoke(crypto_app, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get crypto market data', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_error_handling(self, mock_client):
        """Test error handling in CLI scripts."""
        mock_instance = Mock()
        mock_instance.get_bars.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn('❌ Error:', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_verbose_output(self, mock_client):
        """Test verbose output flag."""
        mock_instance = Mock()
        mock_instance.get_bars.return_value = self.mock_bars_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL', '--verbose'])
        
        self.assertEqual(result.exit_code, 0)
        # In verbose mode, it should show more details
        self.assertIn('Getting bars for symbols:', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_unsupported_format(self, mock_client):
        """Test unsupported format error."""
        mock_instance = Mock()
        mock_instance.get_bars.return_value = self.mock_bars_response
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL', '--format', 'xml'])
        
        self.assertEqual(result.exit_code, 1)
        self.assertIn('❌ Error: Unsupported format', result.output)

    @patch('src.alpaca_data.AlpacaClient')
    def test_dataframe_format_with_pandas(self, mock_client):
        """Test DataFrame format when pandas is available."""
        mock_instance = Mock()
        # Mock pandas DataFrame
        import pandas as pd
        mock_df = pd.DataFrame([{'symbol': 'AAPL', 'close': 153.0}])
        mock_instance.get_bars.return_value = mock_df
        mock_client.return_value = mock_instance
        
        result = self.runner.invoke(bars_app, ['AAPL', '--format', 'dataframe'])
        
        self.assertEqual(result.exit_code, 0)
        # Should output the DataFrame
        self.assertIn('symbol', result.output)

    def test_crypto_subcommand_help(self):
        """Test crypto subcommand help messages."""
        # Test bars subcommand help
        result = self.runner.invoke(crypto_app, ['bars', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get historical OHLCV bars for crypto pairs', result.output)
        
        # Test quotes subcommand help
        result = self.runner.invoke(crypto_app, ['quotes', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get quotes for crypto pairs', result.output)
        
        # Test snapshot subcommand help
        result = self.runner.invoke(crypto_app, ['snapshot', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Get market snapshots for crypto pairs', result.output)


if __name__ == '__main__':
    unittest.main()