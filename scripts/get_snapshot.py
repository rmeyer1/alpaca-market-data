#!/usr/bin/env python3
"""CLI script to fetch market snapshots."""

import argparse
import os
import sys


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

    print(f"Fetching snapshots for: {', '.join(args.symbols)}")
    print("Note: Placeholder implementation. Full implementation coming in TASK-9.")


if __name__ == "__main__":
    main()
