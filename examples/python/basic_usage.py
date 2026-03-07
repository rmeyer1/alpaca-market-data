"""
Basic Usage Examples for Alpaca Market Data SDK

This file demonstrates the fundamental usage patterns for getting market data.
"""

from alpaca_data import AlpacaClient

def main():
    """
    Demonstrates basic market data retrieval.
    """
    # Initialize client (loads credentials from environment)
    client = AlpacaClient()
    
    print("=== Basic Market Data Examples ===")
    
    # Example 1: Get historical bars for a stock
    print("\n1. Historical Bars")
    print("-" * 40)
    
    bars = client.get_bars(
        symbols="AAPL",
        timeframe="1Day",
        start="2024-01-01",
        limit=5
    )
    
    print(f"Retrieved {len(bars['bars'])} bars for {bars['symbol']}")
    for bar in bars['bars'][-3:]:  # Show last 3 bars
        print(f"  {bar.timestamp.strftime('%Y-%m-%d')}: O:${bar.open:.2f} H:${bar.high:.2f} L:${bar.low:.2f} C:${bar.close:.2f}")
    
    # Example 2: Get current quotes
    print("\n2. Real-time Quotes")
    print("-" * 40)
    
    quotes = client.get_quotes(
        symbols=["AAPL", "GOOGL"],
        limit=2
    )
    
    print(f"Retrieved {len(quotes['quotes'])} quotes")
    for quote in quotes['quotes']:
        print(f"  {quote.symbol}: ${quote.bid_price:.2f} x {quote.bid_size} / ${quote.ask_price:.2f} x {quote.ask_size}")
    
    # Example 3: Get market snapshots
    print("\n3. Market Snapshots")
    print("-" * 40)
    
    snapshots = client.get_snapshot(
        symbols=["AAPL", "MSFT"]
    )
    
    print(f"Retrieved {len(snapshots['snapshots'])} snapshots")
    for snapshot in snapshots['snapshots']:
        print(f"  {snapshot.symbol}:")
        if snapshot.latest_trade:
            print(f"    Last Trade: ${snapshot.latest_trade.price:.2f} x {snapshot.latest_trade.size}")
        if snapshot.latest_quote:
            print(f"    Quote: ${snapshot.latest_quote.bid_price:.2f} - ${snapshot.latest_quote.ask_price:.2f}")
    
    # Example 4: Get recent news
    print("\n4. Market News")
    print("-" * 40)
    
    news = client.get_news(
        symbols=["AAPL"],
        limit=2
    )
    
    print(f"Retrieved {len(news['news'])} news articles")
    for article in news['news']:
        print(f"  {article.headline}")
        print(f"    Source: {article.source} | Time: {article.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    print("\n=== Basic Examples Complete ===")

if __name__ == "__main__":
    main()