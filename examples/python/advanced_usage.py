"""
Advanced Usage Examples for Alpaca Market Data SDK

This file demonstrates advanced usage patterns including multiple symbols,
output formats, error handling, and best practices.
"""

import json
import pandas as pd
from alpaca_data import AlpacaClient

def main():
    """
    Demonstrates advanced market data patterns.
    """
    client = AlpacaClient()
    
    print("=== Advanced Market Data Examples ===")
    
    # Example 1: Multiple symbols analysis
    print("\n1. Multiple Symbols Analysis")
    print("-" * 40)
    
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    # Get historical data for all symbols
    bars_data = client.get_bars(
        symbols=symbols,
        timeframe="1Day",
        start="2024-01-01",
        limit=30
    )
    
    print(f"Retrieved {len(bars_data['bars'])} bars for {symbols}")
    
    # Analyze performance
    if bars_data['bars']:
        # Group by symbol
        symbol_data = {}
        for bar in bars_data['bars']:
            symbol = bar.symbol
            if symbol not in symbol_data:
                symbol_data[symbol] = []
            symbol_data[symbol].append(bar)
        
        # Calculate basic statistics
        for symbol in symbols[:3]:  # Show first 3
            if symbol in symbol_data:
                data = symbol_data[symbol]
                first_close = data[0].close
                last_close = data[-1].close
                change = ((last_close - first_close) / first_close) * 100
                print(f"  {symbol}: {change:+.1f}% over period")
    
    # Example 2: Different output formats
    print("\n2. Output Format Examples")
    print("-" * 40)
    
    # JSON output
    json_result = client.get_bars(
        symbols="AAPL",
        timeframe="1Day",
        limit=3,
        output_format="json"
    )
    print(f"JSON format: {type(json_result)}")
    
    # DataFrame output (requires pandas)
    try:
        df_result = client.get_bars(
            symbols="AAPL",
            timeframe="1Day", 
            limit=10,
            output_format="dataframe"
        )
        if hasattr(df_result, 'head'):
            print(f"DataFrame shape: {df_result.shape}")
            print(f"Columns: {list(df_result.columns)}")
    except ImportError:
        print("Pandas not available - install with pip install pandas")
    
    # CSV output
    csv_result = client.get_bars(
        symbols="AAPL",
        timeframe="1Day",
        limit=3,
        output_format="csv"
    )
    print(f"CSV output length: {len(csv_result)} chars")
    
    # Example 3: Error handling
    print("\n3. Error Handling Examples")
    print("-" * 40)
    
    try:
        # Try to get data for invalid symbol
        invalid_result = client.get_bars(
            symbols="INVALID_SYMBOL",
            timeframe="1Day",
            limit=1
        )
        print("This should not print")
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}")
        print(f"Error message: {str(e)[:100]}...")
    
    # Example 4: Cryptocurrency data
    print("\n4. Cryptocurrency Data")
    print("-" * 40)
    
    # Crypto bars
    crypto_bars = client.get_crypto_bars(
        symbols=["BTC/USD", "ETH/USD"],
        timeframe="1Hour",
        limit=5
    )
    
    print(f"Retrieved {len(crypto_bars['bars'])} crypto bars")
    
    # Crypto quotes
    crypto_quotes = client.get_crypto_quotes(
        symbols=["BTC/USD"]
    )
    
    print(f"Retrieved {len(crypto_quotes['quotes'])} crypto quotes")
    
    # Crypto snapshots
    crypto_snapshots = client.get_crypto_snapshot(
        symbols=["BTC/USD", "ETH/USD"]
    )
    
    print(f"Retrieved {len(crypto_snapshots['snapshots'])} crypto snapshots")
    
    # Example 5: Rate limiting awareness
    print("\n5. Rate Limiting & Best Practices")
    print("-" * 40)
    
    print("Current rate limit setting:", getattr(client, 'rate_limiter', 'Default'))
    
    # Batch requests when possible
    symbols_batch = ["AAPL", "GOOGL"]
    
    print("\nBatch request approach:")
    batch_result = client.get_quotes(
        symbols=symbols_batch,
        limit=3
    )
    print(f"Batch quotes: {len(batch_result['quotes'])} items in single request")
    
    # Sequential approach
    print("\nSequential approach:")
    for symbol in symbols_batch:
        single_result = client.get_quotes(
            symbols=symbol,
            limit=1
        )
        print(f"Single quote for {symbol}: {len(single_result['quotes'])} items")
    
    print("\n=== Advanced Examples Complete ===")

def save_data_examples():
    """
    Examples of saving data to different formats.
    """
    client = AlpacaClient()
    
    print("\n=== Data Export Examples ===")
    
    # Get data
    bars = client.get_bars(
        symbols=["AAPL", "GOOGL"],
        timeframe="1Day",
        limit=20,
        start="2024-01-01"
    )
    
    # Save to JSON
    with open("market_data.json", "w") as f:
        # Convert to JSON-serializable format
        json_data = {
            "symbol": bars["symbol"],
            "timeframe": bars["timeframe"],
            "count": bars["count"],
            "bars": [
                {
                    "symbol": bar.symbol,
                    "timestamp": bar.timestamp.isoformat(),
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume
                }
                for bar in bars["bars"]
            ]
        }
        json.dump(json_data, f, indent=2)
    print("Data saved to market_data.json")
    
    # Save to CSV using pandas
    try:
        import pandas as pd
        
        # Convert to DataFrame
        df_data = []
        for bar in bars["bars"]:
            df_data.append({
                "symbol": bar.symbol,
                "timestamp": bar.timestamp,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv("market_data.csv", index=False)
        print("Data saved to market_data.csv")
        
        # Create analysis
        summary = df.groupby('symbol').agg({
            'close': ['min', 'max', 'mean'],
            'volume': 'mean'
        }).round(2)
        
        print("Price Summary:")
        print(summary)
        
    except ImportError:
        print("Pandas not available - skipping CSV export")

if __name__ == "__main__":
    main()
    save_data_examples()