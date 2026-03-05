#!/usr/bin/env python3
"""CLI script to fetch historical OHLCV bars."""

import argparse
import os
import sys
from datetime import datetime, timedelta


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

    print(f"Fetching {args.timeframe} bars for: {', '.join(args.symbols)}")
    print("Note: This is a placeholder. Full implementation coming in TASK-6.")


if __name__ == "__main__":
    main()
