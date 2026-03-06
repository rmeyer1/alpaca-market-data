#!/usr/bin/env python3
"""CLI script to fetch market snapshots."""

import argparse
import os
import sys

# Import SDK modules
try:
    from alpaca_data import AlpacaClient
    from alpaca_data.exceptions import (
        AlpacaAuthError,
        AlpacaNotFoundError,
        AlpacaRateLimitError,
        AlpacaAPIError,
    )
except ImportError as e:
    print(f"Error importing Alpaca SDK: {e}", file=sys.stderr)
    print("Make sure the package is installed: pip install -e .", file=sys.stderr)
    sys.exit(1)


def main():
    """Main entry point for get_snapshot CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch market snapshots from Alpaca Market Data API"
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Stock symbols (e.g., AAPL MSFT)",
    )
    parser.add_argument(
        "--feed",
        default="iex",
        choices=["iex", "sip"],
        help="Data feed",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="Output format",
    )
    parser.add_argument(
        "--output-file",
        "-f",
        type=str,
        help="Output file path",
    )

    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("ALPACA_API_KEY") or not os.getenv("ALPACA_SECRET_KEY"):
        print("Error: API credentials required", file=sys.stderr)
        sys.exit(1)

    try:
        # Initialize client
        client = AlpacaClient()
        
        print(f"Testing connection to Alpaca API...")
        if not client.test_connection():
            print("Error: Failed to connect to Alpaca API. Check your credentials.", file=sys.stderr)
            sys.exit(1)
            
        print("✅ Connected successfully!")
        
        # Fetch snapshots
        print(f"Fetching snapshots for: {', '.join(args.symbols)}")
        result = client.get_snapshot(args.symbols, feed=args.feed)
        
        # Format output
        if args.output == "json":
            import json
            output_data = {
                "symbol": result["symbol"],
                "feed": result["feed"],
                "count": result["count"],
                "snapshots": []
            }
            
            for snapshot in result["snapshots"]:
                snapshot_dict = {"symbol": snapshot.symbol}
                
                if snapshot.latest_trade:
                    snapshot_dict["latest_trade"] = {
                        "timestamp": snapshot.latest_trade.timestamp.isoformat(),
                        "price": snapshot.latest_trade.price,
                        "size": snapshot.latest_trade.size,
                        "exchange": snapshot.latest_trade.exchange
                    }
                
                if snapshot.latest_quote:
                    snapshot_dict["latest_quote"] = {
                        "timestamp": snapshot.latest_quote.timestamp.isoformat(),
                        "ask_price": snapshot.latest_quote.ask_price,
                        "bid_price": snapshot.latest_quote.bid_price,
                        "ask_size": snapshot.latest_quote.ask_size,
                        "bid_size": snapshot.latest_quote.bid_size
                    }
                
                if snapshot.minute_bar:
                    snapshot_dict["minute_bar"] = {
                        "timestamp": snapshot.minute_bar.timestamp.isoformat(),
                        "open": snapshot.minute_bar.open,
                        "high": snapshot.minute_bar.high,
                        "low": snapshot.minute_bar.low,
                        "close": snapshot.minute_bar.close,
                        "volume": snapshot.minute_bar.volume
                    }
                
                if snapshot.daily_bar:
                    snapshot_dict["daily_bar"] = {
                        "timestamp": snapshot.daily_bar.timestamp.isoformat(),
                        "open": snapshot.daily_bar.open,
                        "high": snapshot.daily_bar.high,
                        "low": snapshot.daily_bar.low,
                        "close": snapshot.daily_bar.close,
                        "volume": snapshot.daily_bar.volume
                    }
                
                output_data["snapshots"].append(snapshot_dict)
            
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    json.dump(output_data, f, indent=2)
                print(f"✅ Results saved to {args.output_file}")
            else:
                print(json.dumps(output_data, indent=2))
        
        else:
            # CSV format
            print("Symbol,Latest Trade Price,Latest Trade Size,Ask Price,Bid Price,Minute Bar Close,Daily Bar Close")
            for snapshot in result["snapshots"]:
                trade_price = snapshot.latest_trade.price if snapshot.latest_trade else "N/A"
                trade_size = snapshot.latest_trade.size if snapshot.latest_trade else "N/A"
                ask_price = snapshot.latest_quote.ask_price if snapshot.latest_quote else "N/A"
                bid_price = snapshot.latest_quote.bid_price if snapshot.latest_quote else "N/A"
                minute_close = snapshot.minute_bar.close if snapshot.minute_bar else "N/A"
                daily_close = snapshot.daily_bar.close if snapshot.daily_bar else "N/A"
                
                print(f"{snapshot.symbol},{trade_price},{trade_size},{ask_price},{bid_price},{minute_close},{daily_close}")
        
        print(f"\n✅ Retrieved {result['count']} snapshot(s) using {args.feed} feed")
        
    except AlpacaAuthError as e:
        print(f"Authentication Error: {e}", file=sys.stderr)
        print("Check your API credentials in .env file", file=sys.stderr)
        sys.exit(1)
    except AlpacaRateLimitError as e:
        print(f"Rate Limit Error: {e}", file=sys.stderr)
        if e.retry_after:
            print(f"Retry after: {e.retry_after} seconds", file=sys.stderr)
        sys.exit(1)
    except AlpacaNotFoundError as e:
        print(f"Not Found Error: {e}", file=sys.stderr)
        print("Check that your symbols are valid", file=sys.stderr)
        sys.exit(1)
    except AlpacaAPIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        if e.status_code:
            print(f"HTTP Status: {e.status_code}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
