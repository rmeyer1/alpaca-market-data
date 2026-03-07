"""Test for TASK-16: Output Formatters"""

import unittest
import tempfile
import os
from datetime import datetime
from src.alpaca_data.formatters import (
    JSONFormatter, 
    CSVFormatter, 
    DataFrameFormatter,
    OutputFormatter,
    format_output,
    to_json,
    to_csv,
    to_dataframe,
    detect_data_type,
    suggest_format
)
from src.alpaca_data.models import Bar, Quote, Trade, Snapshot, News


class TestFormatters(unittest.TestCase):
    """Test cases for output formatters."""

    def setUp(self):
        """Set up test data."""
        self.bar = Bar(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            open=150.0,
            high=155.0,
            low=149.0,
            close=153.0,
            volume=1000000,
            trade_count=5000
        )
        
        self.quote = Quote(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            ask_exchange="XNAS",
            ask_price=153.5,
            ask_size=100,
            bid_exchange="XNAS",
            bid_price=153.0,
            bid_size=200
        )
        
        self.trade = Trade(
            symbol="AAPL",
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            exchange="XNAS",
            price=153.0,
            size=100
        )
        
        self.bars_list = [self.bar, self.bar]
        self.api_response = {
            "bars": self.bars_list,
            "symbol": "AAPL",
            "timeframe": "1Day",
            "count": 2
        }

    def test_json_formatter_single_model(self):
        """Test JSON formatter with single model."""
        formatter = JSONFormatter()
        result = formatter.format(self.bar)
        
        # Should return valid JSON
        import json
        parsed = json.loads(result)
        
        self.assertEqual(parsed["symbol"], "AAPL")
        self.assertEqual(parsed["open"], 150.0)
        self.assertEqual(parsed["close"], 153.0)

    def test_json_formatter_list(self):
        """Test JSON formatter with list of models."""
        formatter = JSONFormatter()
        result = formatter.format(self.bars_list)
        
        import json
        parsed = json.loads(result)
        
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["symbol"], "AAPL")

    def test_json_formatter_api_response(self):
        """Test JSON formatter with API response."""
        formatter = JSONFormatter()
        result = formatter.format(self.api_response)
        
        import json
        parsed = json.loads(result)
        
        self.assertIn("bars", parsed)
        self.assertIn("symbol", parsed)
        self.assertEqual(parsed["count"], 2)

    def test_csv_formatter_list(self):
        """Test CSV formatter with list of models."""
        formatter = CSVFormatter()
        result = formatter.format(self.bars_list)
        
        # Should return CSV content
        lines = result.strip().split('\n')
        self.assertTrue(len(lines) > 1)  # Header + data rows
        
        # Check header
        headers = lines[0].split(',')
        self.assertIn("symbol", headers)
        self.assertIn("open", headers)
        self.assertIn("close", headers)

    def test_csv_formatter_with_filename(self):
        """Test CSV formatter with filename."""
        formatter = CSVFormatter()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tmp:
            tmp_filename = tmp.name
        
        try:
            formatter.format(self.bars_list, filename=tmp_filename)
            
            # File should exist and have content
            self.assertTrue(os.path.exists(tmp_filename))
            
            with open(tmp_filename, 'r') as f:
                content = f.read()
                self.assertIn("symbol", content)
                self.assertIn("AAPL", content)
                
        finally:
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)

    def test_dataframe_formatter(self):
        """Test DataFrame formatter."""
        try:
            formatter = DataFrameFormatter()
            df = formatter.format(self.bars_list)
            
            # Should be a pandas DataFrame
            import pandas as pd
            self.assertIsInstance(df, pd.DataFrame)
            
            # Should have correct columns and data
            self.assertIn("symbol", df.columns)
            self.assertEqual(len(df), 2)
            self.assertEqual(df["symbol"].iloc[0], "AAPL")
            
        except ImportError:
            self.skipTest("pandas not available")

    def test_output_formatter_interface(self):
        """Test main OutputFormatter interface."""
        output_formatter = OutputFormatter()
        
        # Test supported formats
        supported = output_formatter.get_supported_formats()
        self.assertIn("json", supported)
        self.assertIn("csv", supported)
        
        # Test JSON output
        json_result = output_formatter.format(self.bar, "json")
        self.assertIsInstance(json_result, str)
        
        # Test CSV output
        csv_result = output_formatter.format(self.bars_list, "csv")
        self.assertIsInstance(csv_result, str)
        self.assertIn("symbol", csv_result)

    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test to_json
        json_result = to_json(self.bar)
        self.assertIsInstance(json_result, str)
        
        # Test to_csv
        csv_result = to_csv(self.bars_list)
        self.assertIsInstance(csv_result, str)
        self.assertIn("symbol", csv_result)
        
        # Test to_dataframe (if pandas available)
        try:
            df = to_dataframe(self.bars_list)
            import pandas as pd
            self.assertIsInstance(df, pd.DataFrame)
        except ImportError:
            self.skipTest("pandas not available")

    def test_data_type_detection(self):
        """Test data type detection."""
        # Single model
        detected = detect_data_type(self.bar)
        self.assertEqual(detected, "bar")
        
        # List of models
        detected = detect_data_type(self.bars_list)
        self.assertEqual(detected, "list_of_bars")
        
        # API response
        detected = detect_data_type(self.api_response)
        self.assertEqual(detected, "api_response_with_bars")

    def test_format_suggestion(self):
        """Test format suggestion."""
        # Single model should suggest JSON
        suggested = suggest_format(self.bar)
        self.assertEqual(suggested, "json")
        
        # List should suggest CSV
        suggested = suggest_format(self.bars_list)
        self.assertEqual(suggested, "csv")
        
        # API response should suggest JSON
        suggested = suggest_format(self.api_response)
        self.assertEqual(suggested, "json")

    def test_error_handling(self):
        """Test error handling."""
        output_formatter = OutputFormatter()
        
        # Unsupported format
        with self.assertRaises(ValueError):
            output_formatter.format(self.bar, "unsupported_format")
        
        # DataFrame without pandas
        # This should work since we check availability in init
        try:
            df_formatter = DataFrameFormatter()
            df_formatter.format(self.bars_list)
        except ImportError:
            self.skipTest("pandas not available")

    def test_json_with_options(self):
        """Test JSON formatter with options."""
        formatter = JSONFormatter()
        
        # Test with indent and sort_keys
        result = formatter.format(self.bar, indent=4, sort_keys=True)
        
        import json
        parsed = json.loads(result)
        self.assertEqual(parsed["symbol"], "AAPL")

    def test_csv_with_options(self):
        """Test CSV formatter with options."""
        formatter = CSVFormatter()
        
        # Test with custom delimiter
        result = formatter.format(self.bars_list, delimiter=';')
        
        # Should use semicolon delimiter
        lines = result.strip().split('\n')
        if len(lines) > 1:
            headers = lines[0].split(';')
            self.assertIn("symbol", headers)

    def test_empty_data_handling(self):
        """Test handling of empty data."""
        formatter = JSONFormatter()
        
        # Empty list
        result = formatter.format([])
        self.assertEqual(result, "[]")
        
        # Empty dict
        result = formatter.format({})
        self.assertEqual(result, "{}")

    def test_nested_data_handling(self):
        """Test handling of nested data structures."""
        nested_data = {
            "bar": self.bar,
            "quote": self.quote,
            "nested_list": [self.bar, self.quote],
            "simple_value": "test"
        }
        
        formatter = JSONFormatter()
        result = formatter.format(nested_data)
        
        import json
        parsed = json.loads(result)
        
        self.assertEqual(parsed["simple_value"], "test")
        self.assertIn("nested_list", parsed)
        self.assertEqual(len(parsed["nested_list"]), 2)

    def test_quote_and_trade_formatting(self):
        """Test formatting of Quote and Trade models."""
        # Test Quote formatting
        quote_formatter = JSONFormatter()
        quote_result = quote_formatter.format(self.quote)
        
        import json
        parsed_quote = json.loads(quote_result)
        self.assertEqual(parsed_quote["symbol"], "AAPL")
        self.assertEqual(parsed_quote["ask_price"], 153.5)
        
        # Test Trade formatting
        trade_result = quote_formatter.format(self.trade)
        parsed_trade = json.loads(trade_result)
        self.assertEqual(parsed_trade["price"], 153.0)
        self.assertEqual(parsed_trade["size"], 100)


if __name__ == '__main__':
    unittest.main()