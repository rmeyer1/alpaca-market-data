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
        
        # TODO: Implement actual get_bars call when TASK-6 is ready
        print(f"Fetching {args.timeframe} bars for: {', '.join(args.symbols)}")
        print("Note: Full implementation coming in TASK-6.")
        
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
