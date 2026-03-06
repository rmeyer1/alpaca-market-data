#!/usr/bin/env python3
"""CLI script to fetch historical OHLCV bars."""

import argparse
import os
import sys
from datetime import datetime, timedelta

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
    """Main entry point for get_bars CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch historical OHLCV bars from Alpaca Market Data API"
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Stock or crypto symbols (e.g., AAPL MSFT BTC/USD)",
    )
    parser.add_argument(
        "--timeframe",
        default="1Day",
        choices=["1Min", "5Min", "15Min", "1Hour", "1Day", "1Week", "1Month"],
        help="Bar timeframe (default: 1Day)",
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date (YYYY-MM-DD or ISO 8601)",
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date (YYYY-MM-DD or ISO 8601, defaults to now)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        help="Maximum number of bars to fetch (default: 100)",
    )
    parser.add_argument(
        "--feed",
        default="iex",
        choices=["iex", "sip"],
        help="Data feed (iex for free tier, sip requires subscription)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output-file",
        "-f",
        type=str,
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check for API credentials
    if not os.getenv("ALPACA_API_KEY") or not os.getenv("ALPACA_SECRET_KEY"):
        print(
            "Error: ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables required",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        # Initialize client
        client = AlpacaClient()
        
        print(f"Testing connection to Alpaca API...")
        if not client.test_connection():
            print("Error: Failed to connect to Alpaca API. Check your credentials.", file=sys.stderr)
            sys.exit(1)
            
        print("✅ Connected successfully!")
        
        # Prepare parameters
        params = {
            'symbols': args.symbols,
            'timeframe': args.timeframe,
            'limit': args.limit,
        }
        
        # Add optional parameters
        if args.start:
            params['start'] = args.start
        if args.end:
            params['end'] = args.end
            
        print(f"📊 Fetching {args.timeframe} bars for: {', '.join(args.symbols)}")
        
        # Make the API call
        result = client.get_bars(**params)
        
        # Display results
        print(f"✅ Retrieved {result['count']} bars")
        
        # Convert bars to output format
        if args.output == "json":
            if args.output_file:
                import json
                with open(args.output_file, 'w') as f:
                    json.dump(result, f, default=str, indent=2)
                print(f"💾 Saved to {args.output_file}")
            else:
                import json
                print(json.dumps(result, default=str, indent=2))
        
        elif args.output == "csv":
            if not result['bars']:
                print("No bars to export")
                return
                
            import csv
            import io
            
            # Create CSV content
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            first_bar = result['bars'][0]
            writer.writerow(['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume', 'trade_count', 'vwap'])
            
            # Write bar data
            for bar in result['bars']:
                writer.writerow([
                    bar.symbol,
                    bar.timestamp,
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                    bar.volume,
                    bar.trade_count or '',
                    bar.vwap or ''
                ])
            
            # Output CSV
            if args.output_file:
                with open(args.output_file, 'w') as f:
                    f.write(output.getvalue())
                print(f"💾 Saved to {args.output_file}")
            else:
                print("📄 CSV Output:")
                print(output.getvalue())
        
        # Show pagination info if available
        if result.get('has_next_page'):
            print(f"📖 More pages available. Next page token: {result['next_page_token']}")
        
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
