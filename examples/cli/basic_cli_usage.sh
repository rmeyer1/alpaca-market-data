#!/bin/bash

# Basic CLI Usage Examples for Alpaca Market Data SDK
# This script demonstrates common CLI commands for getting market data

echo "=== Alpaca Market Data CLI Examples ==="
echo

# Check if CLI is installed
if ! command -v alpaca-bars &> /dev/null; then
    echo "❌ CLI tools not found. Install with: pip install -e ."
    exit 1
fi

echo "✅ CLI tools found and ready to use"
echo

# Example 1: Historical bars
echo "1. Historical Bars"
echo "------------------"
echo "# Get AAPL daily bars for January 2024"
echo "alpaca-bars AAPL --timeframe 1Day --start 2024-01-01 --end 2024-01-31"
echo

# Example 2: Multiple symbols
echo "2. Multiple Symbols"
echo "-------------------"
echo "# Get bars for multiple stocks"
echo "alpaca-bars AAPL GOOGL MSFT --timeframe 1Day --limit 10"
echo

# Example 3: Different timeframes
echo "3. Timeframe Options"
echo "--------------------"
echo "# 1-minute bars (for recent intraday data)"
echo "alpaca-bars AAPL --timeframe 1Min --limit 60"
echo
echo "# 1-hour bars"
echo "alpaca-bars AAPL --timeframe 1Hour --limit 24"
echo
echo "# Weekly bars"
echo "alpaca-bars AAPL --timeframe 1Week --limit 12"
echo

# Example 4: Output formats
echo "4. Output Formats"
echo "-----------------"
echo "# JSON output to file"
echo "alpaca-bars AAPL --timeframe 1Day --format json --output-file aapl_daily.json"
echo
echo "# CSV output to file"
echo "alpaca-bars AAPL --timeframe 1Day --format csv --output-file aapl_daily.csv"
echo
echo "# Pandas DataFrame output"
echo "alpaca-bars AAPL --timeframe 1Day --format dataframe --output-file aapl_analysis.xlsx"
echo

# Example 5: Real-time data
echo "5. Real-time Data"
echo "-----------------"
echo "# Get current quotes"
echo "alpaca-quotes AAPL GOOGL"
echo
echo "# Get recent trades"
echo "alpaca-trades AAPL --limit 10"
echo

# Example 6: Market snapshots
echo "6. Market Snapshots"
echo "-------------------"
echo "# Get comprehensive market data"
echo "alpaca-snapshot AAPL MSFT TSLA --verbose"
echo

# Example 7: News
echo "7. Market News"
echo "--------------"
echo "# Get latest news for specific symbols"
echo "alpaca-news --symbols AAPL TSLA --limit 5"
echo
echo "# Include full article content"
echo "alpaca-news --symbols AAPL --limit 3 --include-content"
echo

# Example 8: Cryptocurrency
echo "8. Cryptocurrency Data"
echo "-----------------------"
echo "# Crypto bars"
echo "alpaca-crypto bars BTC/USD ETH/USD --timeframe 1Hour"
echo
echo "# Crypto quotes"
echo "alpaca-crypto quotes BTC/USD"
echo
echo "# Crypto snapshots"
echo "alpaca-crypto snapshot BTC/USD --format json"
echo

# Example 9: Help and documentation
echo "9. Getting Help"
echo "---------------"
echo "# General help"
echo "alpaca-bars --help"
echo
echo "# Specific command help"
echo "alpaca-bars AAPL --help"
echo
echo "# Crypto help"
echo "alpaca-crypto --help"
echo "alpaca-crypto bars --help"
echo

echo "=== Interactive Examples ==="
echo

# Ask user if they want to run interactive examples
read -p "Would you like to run interactive examples? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo
    echo "Running interactive examples..."
    echo
    
    # Interactive example 1
    echo "Example 1: Getting AAPL daily bars"
    read -p "Press Enter to run: alpaca-bars AAPL --limit 5" -r
    alpaca-bars AAPL --limit 5
    
    echo
    echo "Example 2: Getting quotes"
    read -p "Press Enter to run: alpaca-quotes AAPL" -r
    alpaca-quotes AAPL
    
    echo
    echo "Example 3: Getting crypto data"
    read -p "Press Enter to run: alpaca-crypto bars BTC/USD --limit 3" -r
    alpaca-crypto bars BTC/USD --limit 3
fi

echo
echo "=== CLI Examples Complete ==="
echo "💡 Tip: Check the full documentation in the README.md"
echo "💡 Tip: All commands support --help for detailed usage information"