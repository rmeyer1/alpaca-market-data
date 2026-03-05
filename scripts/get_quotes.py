#!/usr/bin/env python3
"""CLI script to fetch quotes."""

import argparse
import os
import sys


def main():
    """Main entry point for get_quotes CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch quotes from Alpaca Market Data API"
    )
    parser.add_argument(
        "symbols",
        nargs="+",
        help="Stock symbols (e.g., AAPL MSFT)",
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date/time (for historical quotes)",
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date/time (for historical quotes)",
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

    print(f"Fetching quotes for: {', '.join(args.symbols)}")
    print("Note: Placeholder implementation. Full implementation coming in TASK-7.")


if __name__ == "__main__":
    main()
