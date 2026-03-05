#!/usr/bin/env python3
"""CLI script for crypto market data."""

import argparse
import os
import sys


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

    print(f"Fetching crypto {args.command}...")
    print("Note: Placeholder implementation. Full implementation coming in TASK-11+.")


if __name__ == "__main__":
    main()
