"""Test for TASK-14: Crypto Snapshot Endpoint"""

import unittest
from unittest.mock import Mock, patch
from src.alpaca_data.client import AlpacaClient


class TestCryptoSnapshot(unittest.TestCase):
    """Test cases for get_crypto_snapshot method."""

    def setUp(self):
        """Set up test client."""
        self.client = AlpacaClient(
            api_key="test_key",
            secret_key="test_secret"
        )

    def test_get_crypto_snapshot_method_exists(self):
        """Test that get_crypto_snapshot method exists on the client."""
        self.assertTrue(hasattr(self.client, 'get_crypto_snapshot'))
        self.assertTrue(callable(getattr(self.client, 'get_crypto_snapshot')))

    @patch('src.alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_single_symbol(self, mock_request):
        """Test get_crypto_snapshot with single crypto symbol."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "snapshot": {
                "latest_trade": {
                    "p": 50000.0,
                    "s": 1.5,
                    "t": "2024-01-01T12:00:00Z",
                    "i": "12345"
                },
                "latest_quote": {
                    "ap": 50010.0,
                    "as": 1.0,
                    "ax": "CBSE",
                    "bp": 49990.0,
                    "bs": 2.0,
                    "bx": "CBSE",
                    "t": "2024-01-01T12:00:00Z"
                }
            }
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.get_crypto_snapshot("BTC/USD")

        # Verify the result structure
        self.assertIn("snapshots", result)
        self.assertIn("symbol", result)
        self.assertIn("count", result)
        self.assertEqual(result["symbol"], "BTC/USD")
        self.assertEqual(result["count"], 1)
        self.assertEqual(len(result["snapshots"]), 1)

        # Verify API was called with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["url"], "https://paper-api.alpaca.markets/v1beta1/crypto/snapshots/BTC/USD")

    @patch('src.alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_multiple_symbols(self, mock_request):
        """Test get_crypto_snapshot with multiple crypto symbols."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "snapshots": [
                {
                    "S": "BTC/USD",
                    "latest_trade": {
                        "p": 50000.0,
                        "s": 1.5,
                        "t": "2024-01-01T12:00:00Z",
                        "i": "12345"
                    },
                    "latest_quote": {
                        "ap": 50010.0,
                        "as": 1.0,
                        "ax": "CBSE",
                        "bp": 49990.0,
                        "bs": 2.0,
                        "bx": "CBSE",
                        "t": "2024-01-01T12:00:00Z"
                    }
                },
                {
                    "S": "ETH/USD", 
                    "latest_trade": {
                        "p": 3000.0,
                        "s": 10.0,
                        "t": "2024-01-01T12:00:00Z",
                        "i": "67890"
                    },
                    "latest_quote": {
                        "ap": 3010.0,
                        "as": 5.0,
                        "ax": "CBSE",
                        "bp": 2990.0,
                        "bs": 8.0,
                        "bx": "CBSE",
                        "t": "2024-01-01T12:00:00Z"
                    }
                }
            ]
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.get_crypto_snapshot(["BTC/USD", "ETH/USD"])

        # Verify the result structure
        self.assertIn("snapshots", result)
        self.assertIn("symbol", result)
        self.assertIn("count", result)
        self.assertEqual(result["symbol"], ["BTC/USD", "ETH/USD"])
        self.assertEqual(result["count"], 2)
        self.assertEqual(len(result["snapshots"]), 2)

        # Verify API was called with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["url"], "https://paper-api.alpaca.markets/v1beta1/crypto/snapshots")
        self.assertEqual(call_args[1]["params"]["symbols"], "BTC/USD,ETH/USD")

    @patch('src.alpaca_data.client.requests.request')
    def test_get_crypto_snapshot_with_exchange_filter(self, mock_request):
        """Test get_crypto_snapshot with exchange filter."""
        # Mock API response
        mock_response = Mock()
        mock_response.json.return_value = {
            "snapshot": {
                "latest_trade": {
                    "p": 50000.0,
                    "s": 1.5,
                    "t": "2024-01-01T12:00:00Z",
                    "i": "12345"
                },
                "latest_quote": {
                    "ap": 50010.0,
                    "as": 1.0,
                    "ax": "CBSE",
                    "bp": 49990.0,
                    "bs": 2.0,
                    "bx": "CBSE",
                    "t": "2024-01-01T12:00:00Z"
                }
            }
        }
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        # Call the method with exchange filter
        result = self.client.get_crypto_snapshot("BTC/USD", exchange="CBSE")

        # Verify the result structure
        self.assertIn("snapshots", result)
        self.assertIn("exchange", result)
        self.assertEqual(result["exchange"], "CBSE")

        # Verify API was called with exchange parameter
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[1]["params"]["exchange"], "CBSE")


if __name__ == '__main__':
    unittest.main()