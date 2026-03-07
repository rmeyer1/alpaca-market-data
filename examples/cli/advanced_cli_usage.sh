#!/bin/bash

# Advanced CLI Usage Examples for Alpaca Market Data SDK
# This script demonstrates advanced CLI commands and combinations

echo "=== Advanced CLI Usage Examples ==="
echo

# Example 1: Complex queries
echo "1. Complex Query Examples"
echo "-------------------------"
echo "# Get bars with specific timeframe and date range"
echo "alpaca-bars AAPL --timeframe 1Hour --start 2024-01-15T09:30:00-05:00 --end 2024-01-15T16:00:00-05:00 --limit 8"
echo
echo "# Get multiple symbols with different timeframe"
echo "alpaca-bars AAPL GOOGL --timeframe 1Day --adjustment splits_only --limit 20"
echo
echo "# Get data with descending sort (most recent first)"
echo "alpaca-bars TSLA --timeframe 1Day --sort desc --limit 10"
echo

# Example 2: Output format combinations
echo "2. Output Format Combinations"
echo "-----------------------------"
echo "# Save to specific files with different formats"
echo "alpaca-bars AAPL --format json --output-file daily_bars.json"
echo "alpaca-quotes AAPL --format csv --output-file current_quotes.csv"
echo "alpaca-snapshot AAPL --format dataframe --output-file snapshot.xlsx"
echo

# Example 3: Batch processing
echo "3. Batch Processing Examples"
echo "----------------------------"
echo "# Create a list of symbols to analyze"
echo "STOCKS=\"AAPL GOOGL MSFT TSLA NVDA\""
echo "for symbol in \$STOCKS; do"
echo "    echo \"Getting data for \$symbol...\""
echo "    alpaca-bars \$symbol --limit 5 --format json --output-file \${symbol}_data.json"
echo "done"
echo

# Example 4: Real-time monitoring
echo "4. Real-time Monitoring"
echo "----------------------"
echo "# Monitor quotes in a loop (every 30 seconds)"
echo "watch -n 30 'alpaca-quotes AAPL GOOGL --limit 1'"
echo
echo "# Get latest trades continuously"
echo "alpaca-trades AAPL --limit 10"
echo "sleep 30"
echo "alpaca-trades AAPL --limit 10"
echo

# Example 5: Data analysis pipeline
echo "5. Data Analysis Pipeline"
echo "-------------------------"
echo "# Get daily bars and analyze"
echo "alpaca-bars AAPL --timeframe 1Day --limit 252 --format csv --output-file aapl_1year.csv"
echo
echo "# Analyze with pandas (if available)"
echo "python3 -c \""
echo "import pandas as pd"
echo "df = pd.read_csv('aapl_1year.csv')"
echo "print('Average close price:', df['close'].mean())"
echo "print('Volatility:', df['close'].std())"
echo "print('Recent trend:', df['close'].tail(10).pct_change().mean() * 100, '%')"
echo "\""
echo

# Example 6: Cryptocurrency workflows
echo "6. Cryptocurrency Workflows"
echo "---------------------------"
echo "# Get multiple crypto pairs"
echo "alpaca-crypto bars BTC/USD ETH/USD --timeframe 1Hour --limit 24"
echo
echo "# Get crypto snapshots with specific exchange"
echo "alpaca-crypto snapshot BTC/USD ETH/USD --format json --output-file crypto_snapshot.json"
echo
echo "# Compare crypto vs stocks"
echo "alpaca-bars AAPL --timeframe 1Day --limit 5"
echo "alpaca-crypto bars BTC/USD --timeframe 1Day --limit 5"
echo

# Example 7: Error handling and debugging
echo "7. Error Handling & Debugging"
echo "------------------------------"
echo "# Get verbose output for troubleshooting"
echo "alpaca-bars INVALID_SYMBOL --limit 1 --verbose"
echo
echo "# Check CLI tool status"
echo "alpaca-bars --help | head -20"
echo "alpaca-quotes --help | head -20"
echo "alpaca-crypto --help | head -20"
echo

# Example 8: Integration examples
echo "8. Integration Examples"
echo "----------------------"
echo "# Pipe to other tools"
echo "alpaca-bars AAPL --format json | jq '.bars[0].close'"
echo
echo "# Use with grep/awk for filtering"
echo "alpaca-news --symbols AAPL --limit 10 --format csv | grep -i 'earnings'"
echo
echo "# Save and process later"
echo "alpaca-snapshot AAPL GOOGL --format json > market_data.json"
echo "cat market_data.json | jq '.snapshots[] | .symbol + \": \" + (.latest_trade.price|tostring)'"
echo

# Example 9: Performance and rate limiting
echo "9. Performance Considerations"
echo "-----------------------------"
echo "# Use batch requests instead of individual calls"
echo "# ❌ Don't do this:"
echo "# alpaca-quotes AAPL"
echo "# alpaca-quotes GOOGL"
echo "# alpaca-quotes MSFT"
echo
echo "# ✅ Do this instead:"
echo "alpaca-quotes AAPL GOOGL MSFT"
echo
echo "# Respect rate limits"
echo "alpaca-bars AAPL --limit 100"
echo "sleep 2"
echo "alpaca-bars GOOGL --limit 100"
echo

# Example 10: Workflow automation
echo "10. Workflow Automation Examples"
echo "--------------------------------"
echo "# Create a daily report script"
echo "cat > daily_report.sh << 'EOF'"
echo "#!/bin/bash"
echo "DATE=\$(date +%Y-%m-%d)"
echo "echo \"Daily Market Report - \$DATE\""
echo "alpaca-bars AAPL --timeframe 1Day --limit 1 --format json"
echo "alpaca-quotes AAPL --format json"
echo "alpaca-snapshot AAPL --format json"
echo "EOF"
echo "chmod +x daily_report.sh"
echo
echo "# Run the report"
echo "./daily_report.sh > daily_report_\$(date +%Y%m%d).txt"
echo

echo "=== Interactive Advanced Examples ==="
echo

read -p "Would you like to run advanced interactive examples? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo
    echo "Running advanced examples..."
    
    echo
    echo "Example 1: Multi-format output"
    read -p "Press Enter to run: alpaca-bars AAPL --limit 3 --format json" -r
    alpaca-bars AAPL --limit 3 --format json
    
    echo
    echo "Example 2: Crypto analysis"
    read -p "Press Enter to run: alpaca-crypto bars BTC/USD --limit 5" -r
    alpaca-crypto bars BTC/USD --limit 5
    
    echo
    echo "Example 3: Batch processing simulation"
    read -p "Press Enter to run: alpaca-bars AAPL GOOGL --limit 2" -r
    alpaca-bars AAPL GOOGL --limit 2
    
    echo
    echo "Example 4: Error handling demo"
    read -p "Press Enter to try invalid symbol (will show error):" -r
    alpaca-bars INVALID_SYMBOL --limit 1 || echo "Expected error handled gracefully"
fi

echo
echo "=== Advanced CLI Examples Complete ==="
echo "💡 Tip: Combine multiple commands for complex workflows"
echo "💡 Tip: Use output redirection to save data for analysis"
echo "💡 Tip: Respect rate limits when making multiple requests"