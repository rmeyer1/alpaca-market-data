#!/usr/bin/env python3
"""CLI script for crypto market data."""

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
    """Main entry point for crypto CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch crypto market data from Alpaca API"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Bars command
    bars_parser = subparsers.add_parser("bars", help="Fetch crypto bars")
    bars_parser.add_argument("symbols", nargs="+", help="Crypto pairs (e.g., BTC/USD ETH/USD)")
    bars_parser.add_argument("--timeframe", default="1Day", help="Bar timeframe")
    bars_parser.add_argument("--start", help="Start date")
    bars_parser.add_argument("--end", help="End date")
    bars_parser.add_argument("--limit", type=int, default=100, help="Limit")

    # Quotes command
    quotes_parser = subparsers.add_parser("quotes", help="Fetch crypto quotes")
    quotes_parser.add_argument("symbols", nargs="+", help="Crypto pairs")

    # Snapshot command
    snapshot_parser = subparsers.add_parser("snapshot", help="Fetch crypto snapshots")
    snapshot_parser.add_argument("symbols", nargs="+", help="Crypto pairs")

    # Common args
    for p in [bars_parser, quotes_parser, snapshot_parser]:
        p.add_argument("--output", "-o", default="json", choices=["json", "csv"])

    args = parser.parse_args()

    from dotenv import load_dotenv
    load_dotenv()

    if not os.getenv("ALPACA_API_KEY") or not os.getenv("ALPACA_SECRET_KEY"):
        print("Error: API credentials required", file=sys.stderr)
        sys.exit(1)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize client
        client = AlpacaClient()
        
        print(f"Testing connection to Alpaca API...")
        if not client.test_connection():
            print("Error: Failed to connect to Alpaca API. Check your credentials.", file=sys.stderr)
            sys.exit(1)
            
        print("✅ Connected successfully!")
        
        # TODO: Implement actual crypto calls when TASK-11+ are ready
        print(f"Fetching crypto {args.command}...")
        if hasattr(args, 'symbols'):
            print(f"Symbols: {', '.join(args.symbols)}")
        print("Note: Full implementation coming in TASK-11+.")
        
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
